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
+---------------------------------+   +-----------------------------+