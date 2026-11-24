import os
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Maya Local PC Executor", version="1.0.0")

ALLOWED_BASE_DIR = Path(os.getenv("PC_WORKSPACE_DIR", "./generated_projects")).resolve()
API_TOKEN = os.getenv("PC_EXECUTOR_TOKEN", "dev-local-token")


class ProjectRequest(BaseModel):
    action: str
    path: str
    files: dict[str, str] = {}


def _resolve_safe_path(relative_path: str) -> Path:
    """Prevents directory traversal attacks by locking execution inside ALLOWED_BASE_DIR."""
    ALLOWED_BASE_DIR.mkdir(parents=True, exist_ok=True)
    target = (ALLOWED_BASE_DIR / relative_path).resolve()
    if not str(target).startswith(str(ALLOWED_BASE_DIR)):
        raise HTTPException(status_code=403, detail="Access denied: Path escapes allowed workspace.")
    return target


@app.get("/health")
def health_check():
    return {"status": "online", "workspace": str(ALLOWED_BASE_DIR)}


@app.post("/execute")
def execute_action(req: ProjectRequest, x_api_token: str = Header(default="")):
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized local network token.")

    if req.action == "create_project":
        project_dir = _resolve_safe_path(req.path)
        project_dir.mkdir(parents=True, exist_ok=True)
        created_files = []
        for filename, content in req.files.items():
            file_path = (project_dir / filename).resolve()
            if not str(file_path).startswith(str(project_dir)):
                raise HTTPException(status_code=403, detail="Invalid nested file path.")
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            created_files.append(str(file_path.relative_to(ALLOWED_BASE_DIR)))
        return {"status": "success", "project": str(project_dir), "files_created": created_files}

    raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")