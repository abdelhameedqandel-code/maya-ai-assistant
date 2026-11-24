# Local Personal AI Assistant

A production-oriented repository scaffold for a local personal assistant. The design separates room-level voice interaction, model serving and private data storage, and tightly scoped execution on a main PC. Python modules are architectural stubs; training, inference, persistence, voice processing, and remote execution logic will be implemented in later engineering phases.

## System architecture

```text
+--------------------------+       Local Wi-Fi       +----------------------------------+
| Room Voice Interface     | <---------------------> | Dedicated AI Server              |
|                          |                         |                                  |
| Wake word                |   audio / response      | Fine-Tuned LLM                    |
| Faster-Whisper STT       |                         | Encrypted SQLite Vault           |
| Piper / Kokoro TTS       |                         | Agent loop and JSON tool router   |
+--------------------------+                         +----------------+-----------------+
                                                                      |
                                                       scoped requests | Local Wi-Fi
                                                                      v
                                                    +-------------------------------+
                                                    | Main PC Remote Executor       |
                                                    | Authenticated FastAPI service |
                                                    | Scoped project/file/command   |
                                                    | operations                    |
                                                    +-------------------------------+
```

## Repository layout

```text
MY Assistant/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── configs/
│   └── train_config.yaml
├── data/
│   ├── processed/
│   │   └── .gitkeep
│   └── raw/
│       └── .gitkeep
├── database/                 # Local database files are gitignored
├── notebooks/
│   └── .gitkeep
└── src/
    ├── __init__.py
    ├── database/
    │   ├── __init__.py
    │   ├── crypto_manager.py
    │   └── db_handler.py
    ├── inference/
    │   ├── __init__.py
    │   └── agent_loop.py
    ├── remote_agent/
    │   ├── __init__.py
    │   └── pc_executor.py
    ├── training/
    │   ├── __init__.py
    │   ├── dataset_builder.py
    │   └── train.py
    └── voice/
        ├── __init__.py
        └── audio_pipeline.py
```

## Configuration and security

- Copy `.env.example` to `.env` and supply private values locally. Never commit `.env` or vault key material.
- Keep database files under `database/`; this directory and common SQLite files are ignored by Git.
- `configs/train_config.yaml` records initial model, LoRA, and training settings. Review hardware compatibility before installing the model training stack.
- The remote executor is intended to be bound to a trusted local network and protected by an authentication token. Its implementation must enforce scoped paths and commands.

## Planned engineering phases

1. Define encryption and SQLite data contracts for reminders, notes, and vault entries.
2. Build and validate ChatML JSONL datasets for tool use, scheduling, and technical mentorship.
3. Implement an explicit, auditable QLoRA/PEFT training workflow.
4. Add inference and constrained JSON tool routing.
5. Implement offline voice processing and an authenticated, scoped PC executor.
