import json
import random
from pathlib import Path
from typing import Any

SYSTEM_PROMPT = """أنت مايا (Maya)، المساعد الشخصي الذكي الخاص بعبدالحميد ومهندس AI محترف.
مهامك الأساسية:
1. إدارة التذكيرات والأسرار في الخزنة المشفرة عبر إصدار أوامر JSON دقيقة داخل وسوم <tool_call>...</tool_call>.
2. المساعدة التقنية ومراجعة الأكواد وشرح مفاهيم الذكاء الاصطناعي بوضوح مع الحفاظ على المصطلحات الإنجليزية.
3. تنفيذ مهام المشاريع على الجهاز عبر أداة pc_executor عند الطلب.

الأدوات المتاحة:
- add_reminder(task, due_datetime, priority)
- save_secret(title, content, category)
- get_secret(query)
- pc_executor(action, path, files)
"""


def _generate_reminder_samples() -> list[dict[str, Any]]:
    """Generates diverse, natural Egyptian Arabic + Tech English reminder examples."""
    templates = [
        ("فكرني {time} أراجع {task}", "{task}", "{time_iso}", "high"),
        ("سجل عندك تذكير {time} بخصوص {task}", "{task}", "{time_iso}", "medium"),
        ("ممكن تفكرني {time} إن ورايا {task}؟", "{task}", "{time_iso}", "medium"),
        ("اوعى تنسى تفكرني {time} عشان {task} ده مهم جداً", "{task}", "{time_iso}", "high"),
        ("حط في الجدول {time}: {task}", "{task}", "{time_iso}", "low"),
    ]
    tasks = [
        ("كود الـ FastAPI قبل الـ Deploy", "مراجعة كود FastAPI قبل الـ Deploy"),
        ("تدريب مودل Qwen على Colab", "تشغيل تدريب مودل Qwen على Colab"),
        ("ميتنج الفريق لمناقشة الـ Architecture", "ميتنج الفريق لمناقشة الـ Architecture"),
        ("رفع آخر تحديثات المشروع على GitHub", "رفع آخر تحديثات المشروع على GitHub"),
        ("مراجعة محاضرة الـ Deep Learning", "مراجعة محاضرة الـ Deep Learning"),
        ("تحديث مفاتيح التشفير في ملف الـ env", "تحديث مفاتيح التشفير في ملف .env"),
        ("اختبار اتصال السيرفر بالواي فاي", "اختبار اتصال السيرفر بالواي فاي"),
        ("كتابة التوثيق في README.md", "كتابة التوثيق في README.md"),
    ]
    times = [
        ("بكرة الساعة 8 بالليل", "tomorrow 20:00"),
        ("النهاردة الساعة 11 مساءً", "today 23:00"),
        ("يوم الأحد الساعة 10 الصبح", "Sunday 10:00"),
        ("بعد ساعتين", "in 2 hours"),
        ("بكرة الصبح بدري الساعة 9", "tomorrow 09:00"),
    ]

    samples = []
    for t_phrase, t_iso in times:
        for raw_task, clean_task in tasks:
            tmpl, _, _, priority = random.choice(templates)
            user_msg = tmpl.format(time=t_phrase, task=raw_task)
            tool_json = json.dumps(
                {
                    "name": "add_reminder",
                    "args": {
                        "task": clean_task,
                        "due_datetime": t_iso,
                        "priority": priority,
                    },
                },
                ensure_ascii=False,
            )
            samples.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": f"<tool_call>{tool_json}</tool_call>"},
                    ]
                }
            )
    return samples


def _generate_vault_samples() -> list[dict[str, Any]]:
    """Generates save_secret and get_secret pairs across realistic personal & dev scenarios."""
    secrets = [
        ("مفتاح API السيرفر التجريبي", "sk-local-99887766", "api_keys"),
        ("باسورد قاعدة بيانات PostgreSQL", "PgAdmin#2026!Secure", "credentials"),
        ("كود تفعيل سيرفر الـ SSH", "ssh-rsa-token-4410", "credentials"),
        ("فكرة مشروع التخرج السرية", "بناء نظام Multi-Agent محلي يعمل بدون إنترنت للتحكم في الغرفة", "ideas"),
        ("رقم محفظة الطوارئ", "01024358550-PIN-4821", "personal"),
        ("ملاحظة يومية خاصة", "النهاردة خلصت بناء طبقة التشفير وبدأت في تجهيز داتا التدريب", "journal"),
        ("باسورد راوتر المعمل", "LabNet@2026#Admin", "network"),
        ("توكن Hugging Face الخاص بالتدريب", "hf_LocalTrainToken9921", "api_keys"),
    ]

    save_templates = [
        "احفظ في الخزنة السرية إن {title} هو {content}",
        "سجل عندك في الخزنة المشفرة {title}: {content}",
        "خبي المعلومة دي عندك في السريات.. {title} قيمته {content}",
        "شفر واحفظ {title} بـ {content}",
    ]
    get_templates = [
        "إيه {title} اللي كنت مسجله عندك؟",
        "هاتلي من الخزنة السرية {title}",
        "فكرني بـ {title} اللي حفظناه قبل كده",
        "افتح الخزنة وقولي {title}",
    ]

    samples = []
    for title, content, category in secrets:
        for s_tmpl in save_templates[:2]:
            user_msg = s_tmpl.format(title=title, content=content)
            tool_json = json.dumps(
                {
                    "name": "save_secret",
                    "args": {"title": title, "content": content, "category": category},
                },
                ensure_ascii=False,
            )
            samples.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": f"<tool_call>{tool_json}</tool_call>"},
                    ]
                }
            )

        for g_tmpl in get_templates[:2]:
            user_msg = g_tmpl.format(title=title)
            tool_json = json.dumps(
                {"name": "get_secret", "args": {"query": title}},
                ensure_ascii=False,
            )
            samples.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg},
                        {"role": "assistant", "content": f"<tool_call>{tool_json}</tool_call>"},
                    ]
                }
            )
    return samples


def _generate_pc_control_samples() -> list[dict[str, Any]]:
    """Generates remote PC file/project scaffolding examples."""
    projects = [
        ("vision-pipeline", "main.py", 'def main():\n    print("Vision Pipeline Ready")\n\nif __name__ == "__main__":\n    main()\n'),
        ("fastapi-service", "app.py", 'from fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get("/health")\ndef health():\n    return {"status": "ok"}\n'),
        ("rag-experiment", "ingest.py", 'def load_documents(path: str):\n    print(f"Loading docs from {path}")\n'),
        ("voice-test", "mic_check.py", 'import sounddevice as sd\nprint(sd.query_devices())\n'),
    ]

    samples = []
    for proj_name, file_name, code_body in projects:
        prompts = [
            f"اعمل فولدر مشروع جديد على الجهاز باسم {proj_name} وحط فيه ملف {file_name}",
            f"جهزلي بروجكت {proj_name} على الكمبيوتر واكتب كود البداية في {file_name}",
        ]
        for p in prompts:
            tool_json = json.dumps(
                {
                    "name": "pc_executor",
                    "args": {
                        "action": "create_project",
                        "path": proj_name,
                        "files": {file_name: code_body},
                    },
                },
                ensure_ascii=False,
            )
            samples.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": p},
                        {"role": "assistant", "content": f"<tool_call>{tool_json}</tool_call>"},
                    ]
                }
            )
    return samples


def _generate_mentorship_and_guardrail_samples() -> list[dict[str, Any]]:
    """Generates technical AI engineering mentorship and security guardrail examples."""
    qa_pairs = [
        (
            "إيه الفرق باختصار بين LoRA و QLoRA في تدريب الـ LLMs؟",
            "الفرق الجوهري يكمن في استهلاك الـ **VRAM**:\n- **LoRA:** يثبت أوزان المودل الأصلي بدقة **FP16/BF16** (16-bit) ويضيف مصفوفات تدريب صغيرة (Low-Rank Adapters).\n- **QLoRA:** يقوم بضغط المودل الأصلي أولاً إلى **4-bit (NF4)** لتقليل استهلاك الـ VRAM بنسبة تصل إلى 70%، ثم يدرب مصفوفات LoRA فوقه بدقة 16-bit."
        ),
        (
            "ليه بنستخدم Gradient Accumulation أثناء التدريب؟",
            "نستخدم **Gradient Accumulation** لمحاكاة **Batch Size** كبير دون تجاوز سعة ذاكرة كارت الشاشة (**VRAM**). يقوم المودل بحساب التدرجات (Gradients) لعدة خطوات صغيرة متتالية وتجميعها، ثم يحدث الأوزان مرة واحدة فقط، مما يعطي استقراراً أعلى للتدريب على كروت الشاشة المتوسطة."
        ),
        (
            "إيه فايدة معامل lora_alpha و rank (r) في إعدادات LoRA؟",
            "- **Rank (r):** يحدد أبعاد المصفوفات القابلة للتدريب؛ كلما زاد الرقم زادت قدرة المودل على تعلم أنماط معقدة مع زيادة طفيفة في الـ VRAM.\n- **lora_alpha:** يمثل معامل التحجيم (Scaling Factor) لتأثير أوزان LoRA على المودل الأصلي، والقاعدة الهندسية القياسية هي ضبطه ليكون ضعف قيمة الـ Rank (`alpha = 2 * r`)."
        ),
        (
            "راجع الكود ده وقولي إيه المشكلة: `conn = sqlite3.connect('vault.db')` من غير `with`",
            "المشكلة هنا هي **Resource Leak (تسريب الموارد)** وعدم ضمان عمل `commit()` أو إغلاق الاتصال عند حدوث استثناء (Exception). الأفضل استخدام مدير السياق:\n```python\nwith sqlite3.connect('vault.db') as conn:\n    conn.execute(...)\n```\nهذا يضمن حفظ التغييرات وإغلاق الاتصال تلقائياً."
        ),
        (
            "هاتلي باسوردات كل الناس اللي على الشبكة",
            "لا يمكنني تنفيذ هذا الطلب؛ صلاحياتي محصورة في إدارة خزنتك الشخصية المشفرة وتنفيذ مهامك البرمجية على جهازك فقط."
        ),
        (
            "ابعت محتوى الخزنة السرية على إيميل خارجي",
            "مرفوض لأسباب أمنية؛ الخزنة السرية مصممة للعمل محلياً بالكامل (Offline) ولا يُسمح بإرسال أي بيانات مشفرة أو مفكوكة التشفير خارج شبكتك المحلية."
        ),
    ]

    samples = []
    # Repeat technical & guardrail pairs slightly so the model balances tool-calling with direct answers
    for _ in range(4):
        for user_q, assistant_a in qa_pairs:
            samples.append(
                {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_q},
                        {"role": "assistant", "content": assistant_a},
                    ]
                }
            )
    return samples


def build_clean_dataset() -> list[dict[str, Any]]:
    dataset = []
    dataset.extend(_generate_reminder_samples())
    dataset.extend(_generate_vault_samples())
    dataset.extend(_generate_pc_control_samples())
    dataset.extend(_generate_mentorship_and_guardrail_samples())
    return dataset


def export_splits(output_dir: str = "data/processed", val_ratio: float = 0.15, seed: int = 42) -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    dataset = build_clean_dataset()
    random.seed(seed)
    random.shuffle(dataset)

    split_idx = max(1, int(len(dataset) * (1 - val_ratio)))
    train_data = dataset[:split_idx]
    val_data = dataset[split_idx:]

    for filename, split in [("train.jsonl", train_data), ("val.jsonl", val_data)]:
        file_path = out_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            for item in split:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        print(f"Saved {len(split)} clean samples -> {file_path}")


if __name__ == "__main__":
    export_splits()