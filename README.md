# Maya AI: Local Encrypted Personal Assistant & Fine-Tuned Tool-Calling Agent

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Base Model](https://img.shields.io/badge/Model-Qwen2.5--3B--Instruct-purple.svg)](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[![Fine-Tuning](https://img.shields.io/badge/Method-QLoRA%204--bit%20NF4-green.svg)](https://github.com/huggingface/peft)
[![Security](https://img.shields.io/badge/Vault-AES--128%20Fernet%20Encrypted-red.svg)](https://cryptography.io/)

**Maya AI** is an end-to-end, privacy-first local AI assistant engineered from scratch. It combines a **QLoRA fine-tuned Large Language Model** (`Qwen2.5-3B-Instruct`) capable of structured Egyptian-Arabic/English tool calling with a **field-level encrypted SQLite vault** and a **sandboxed local network execution agent**.

---

## System Architecture

```text
+-------------------------------------------------------------------+
|                        User Input (Arabic / English)              |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  LLM Inference Layer (Qwen2.5-3B-Instruct + QLoRA Adapter)        |
|  - Emits structured <tool_call>{...}</tool_call> JSON payloads    |
+---------------------------------+---------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|  Agent Router (`src/inference/agent_loop.py`)                     |
|  - Regex & JSON Schema Parser                                     |
|  - Routes tool calls vs. direct technical responses               |
+-----------------+-------------------------------+-----------------+
                  |                               |
                  v                               v
+---------------------------------+   +-----------------------------+
|  Encrypted Local Vault          |   |  Sandboxed PC Executor      |
|  (`src/database/db_handler.py`) |   |  (`src/remote_agent/`)      |
|  - SQLite + AES-128 Fernet      |   |  - FastAPI + Token Auth     |
|  - Master Key via `.env`        |   |  - Path Traversal Guard     |
+---------------------------------+   +-----------------------------+---

## QLoRA Fine-Tuning Pipeline & Benchmarks

### Training Configuration
* **Base Model:** `Qwen/Qwen2.5-3B-Instruct` (3.11B parameters)
* **Quantization:** 4-bit NormalFloat (`NF4`) with Double Quantization (`float16` compute dtype)
* **LoRA Hyperparameters:** `r=16`, `lora_alpha=32`, `lora_dropout=0.05`
* **Target Modules:** `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`
* **Trainable Parameters:** `29,933,568` (**0.9607%** of total parameters)
* **Dataset:** 104 curated ChatML samples (`88 train` / `16 validation`) covering encrypted vault operations, reminders, remote project scaffolding, and security guardrails.
* **Hardware:** NVIDIA T4 GPU (16GB VRAM)

### Training Metrics Progression

| Epoch | Training Loss | Validation Loss | Mean Token Accuracy |
| :--- | :---: | :---: | :---: |
| **1** | 1.6187 | 0.8118 | 84.48% |
| **2** | 0.4133 | 0.3411 | 92.43% |
| **3** | 0.2302 | 0.2331 | 94.88% |
| **4** | **0.1699** | **0.2109** | **95.36%** |

---

## Before vs. After Fine-Tuning Evaluation

**Test Prompt:** `"احفظ في الخزنة السرية إن مفتاح الـ API بتاع السيرفر هو sk-9988"` *(Save in the secret vault that the server API key is sk-9988)*

* **Base Model (Zero-Shot Baseline — Failed Schema):**
  ```json
  [
    {
      "id": "api_key_storage",
      "?action?": "store",
      "?key?": "sk-9988",
      "?inVault?": "secret"
    }
  ]
Result: Hallucinated invalid keys and omitted <tool_call> tags, breaking downstream execution.

Fine-Tuned Maya Model (Post-QLoRA — Valid Execution):

XML
<tool_call>{"name": "save_secret", "args": {"title": "مفتاح الـ API السريرى", "content": "sk-9988", "category": "api_keys"}}</tool_call>
Result: 100% adherence to the <tool_call> JSON schema, routed directly into the AES-encrypted SQLite vault.

Security Architecture
Symmetric Field-Level Encryption (crypto_manager.py): Sensitive vault entries are encrypted using Fernet (AES-128-CBC + HMAC-SHA256) before touching disk. The VAULT_MASTER_KEY is loaded strictly from environment variables (.env) and excluded from version control.

Sandboxed Remote Execution (pc_executor.py): The local FastAPI agent enforces header token authentication (X-API-Token) and resolves canonical paths via .resolve() to block directory traversal attacks outside the designated workspace.

Quickstart
Clone & Setup Environment:

Bash
git clone [https://github.com/abdelhameedqandel-code/maya-ai-assistant.git](https://github.com/abdelhameedqandel-code/maya-ai-assistant.git)
cd maya-ai-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Generate Master Encryption Key:

Bash
python -c "from src.database.crypto_manager import VaultCryptoManager; open('.env', 'w').write(f'VAULT_MASTER_KEY={VaultCryptoManager.generate_key()}\n')"
Run Encrypted Vault & Agent Loop Verification:

Bash
python -m src.database.db_handler
python -m src.inference.agent_loop
Author
Abdelhameed Qandel — AI Engineering Student, Faculty of Artificial Intelligence, Kafrelsheikh University.

GitHub | LinkedIn
