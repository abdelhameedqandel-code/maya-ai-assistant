import json
import re
from pathlib import Path
from typing import Any
from src.database.db_handler import PrivateVaultDB
from src.training.dataset_builder import SYSTEM_PROMPT


class MayaAgentRouter:
    """
    Core Agent Runtime:
    1. Loads the fine-tuned LoRA adapter over Qwen2.5-3B-Instruct (optional local inference).
    2. Parses <tool_call> JSON payloads emitted by the model.
    3. Routes commands to the AES-encrypted SQLite Vault or Remote PC Executor.
    """

    def __init__(
        self,
        vault: PrivateVaultDB | None = None,
        adapter_path: str = "models/maya-lora-adapter",
        base_model_id: str = "Qwen/Qwen2.5-3B-Instruct",
        load_llm: bool = False,
    ):
        self.vault = vault or PrivateVaultDB()
        self.tool_pattern = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL)
        self.model = None
        self.tokenizer = None

        if load_llm:
            self._load_local_model(base_model_id, adapter_path)

    def _load_local_model(self, base_model_id: str, adapter_path: str) -> None:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        if not Path(adapter_path).exists():
            raise FileNotFoundError(f"LoRA adapter not found at: {adapter_path}")

        print(f"Loading tokenizer and base model ({base_model_id})...")
        self.tokenizer = AutoTokenizer.from_pretrained(adapter_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        base = AutoModelForCausalLM.from_pretrained(
            base_model_id,
            dtype=dtype,
            device_map="auto" if device == "cuda" else None,
        )
        self.model = PeftModel.from_pretrained(base, adapter_path).to(device)
        self.model.eval()
        print(f"Maya fine-tuned model loaded successfully on {device.upper()}.")

    def generate_raw(self, user_prompt: str) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Local LLM is not loaded. Initialize with `load_llm=True`.")

        import torch
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_new_tokens=256, do_sample=False)
        return self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

    def execute_tool(self, tool_payload: dict[str, Any]) -> str:
        name = tool_payload.get("name")
        args = tool_payload.get("args", {})

        if name == "add_reminder":
            res = self.vault.add_reminder(
                task=args["task"],
                due_datetime=args["due_datetime"],
                priority=args.get("priority", "medium"),
            )
            return f"تم تسجيل التذكير بنجاح: '{res['task']}' في موعد ({res['due_datetime']})."

        if name == "save_secret":
            res = self.vault.save_secret(
                title=args["title"],
                content=args["content"],
                category=args.get("category", "general"),
            )
            return f"تم تشفير وحفظ '{res['title']}' في خزنتك السرية بأمان."

        if name == "get_secret":
            records = self.vault.get_secret(query=args["query"])
            if not records:
                return f"لم أجد أي سجل في الخزنة السرية يطابق: '{args['query']}'."
            formatted = "\n".join(
                [f"- **{r['title']}** ({r['category']}): `{r['content']}`" for r in records]
            )
            return f"البيانات المسترجعة من خزنتك المشفرة:\n{formatted}"

        if name == "pc_executor":
            return f"[PC Executor Ready] Action: `{args.get('action')}` -> Path: `{args.get('path')}`"

        return f"أداة غير معروفة: {name}"

    def process_model_output(self, raw_response: str) -> str:
        match = self.tool_pattern.search(raw_response)
        if not match:
            return raw_response.strip()

        try:
            tool_json = json.loads(match.group(1).strip())
            return self.execute_tool(tool_json)
        except json.JSONDecodeError as exc:
            return f"حدث خطأ في قراءة أمر الأداة من المودل: {exc}"

    def chat(self, user_prompt: str) -> str:
        raw = self.generate_raw(user_prompt)
        return self.process_model_output(raw)


if __name__ == "__main__":
    # Switch load_llm=True once `models/maya-lora-adapter` is placed locally and torch/peft are installed
    agent = MayaAgentRouter(load_llm=False)
    print("MayaAgentRouter initialized and ready.")