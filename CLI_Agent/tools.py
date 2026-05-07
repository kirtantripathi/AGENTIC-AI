import os
from pathlib import Path
from typing import List, Optional
from langchain_core.tools import tool
from langchain_community.tools import ShellTool
import re
from pydantic import BaseModel, Field
from typing import List

# ============== CONFIG ==============
BASE_DIR = Path(r"D:\HB iPaaS - Documents").resolve()  # ← Change this if you want
BASE_DIR.mkdir(parents=True, exist_ok=True)
# ====================================

def _safe_path(file_path: str) -> Path:
    """Prevent path traversal attacks"""
    full_path = (BASE_DIR / file_path).resolve()
    if not str(full_path).startswith(str(BASE_DIR)):
        raise ValueError("Path traversal attempt detected!")
    return full_path


@tool
def list_directory(path: str = ".") -> str:
    """List files and directories in a given path (relative to workspace)."""
    dir_path = _safe_path(path)
    if not dir_path.exists():
        return f"Directory does not exist: {path}"
    items = [f.name + ("/" if f.is_dir() else "") for f in dir_path.iterdir()]
    return "\n".join(items) or "Empty directory."


@tool
def read_file(file_path: str) -> str:
    """Read the entire content of a file."""
    full_path = _safe_path(file_path)
    if not full_path.exists():
        return f"File not found: {file_path}"
    return full_path.read_text(encoding="utf-8")


# @tool
# def write_file(file_path: str, content: str) -> str:
#     """Write (or overwrite) content to a file. Creates directories if needed."""
#     full_path = _safe_path(file_path)
#     full_path.parent.mkdir(parents=True, exist_ok=True)
#     full_path.write_text(content, encoding="utf-8")
#     return f"✅ Successfully wrote to {file_path}"


@tool
def grep_files(pattern: str, path: str = ".", case_insensitive: bool = False) -> str:
    """Search for a regex pattern across files (like grep)."""
    dir_path = _safe_path(path)
    flags = 0 if not case_insensitive else re.IGNORECASE
    results = []
    for file in dir_path.rglob("*"):
        if file.is_file():
            try:
                content = file.read_text(encoding="utf-8")
                matches = list(re.finditer(pattern, content, flags))
                for m in matches:
                    line = content.splitlines()[content[:m.start()].count("\n")]
                    results.append(f"{file.relative_to(BASE_DIR)}:{line.strip()}")
            except:
                continue
    return "\n".join(results) or "No matches found."


# @tool
# def make_directory(path: str) -> str:
#     """Create a new directory (and parents if needed)."""
#     dir_path = _safe_path(path)
#     dir_path.mkdir(parents=True, exist_ok=True)
#     return f"✅ Directory created: {path}"


@tool
def file_exists(path: str) -> bool:
    """Check if a file or directory exists."""
    return _safe_path(path).exists()


class ShellInput(BaseModel):
    commands: List[str] = Field(..., description="List of shell commands to run sequentially.")

shell_tool = ShellTool(args_schema=ShellInput)
shell_tool.name = "terminal"   # or "run_shell"
shell_tool.description = """Run one or more bash commands in the sandboxed workspace.
Prefer using the dedicated safe tools (list_directory, read_file, etc.) first.
Only use this tool when necessary.
Always provide clean commands without trailing $ or invalid syntax."""

# Export all tools
fs_tools = [
    list_directory,
    read_file,
    # write_file,
    grep_files,
    # make_directory,
    file_exists,
    shell_tool,
]