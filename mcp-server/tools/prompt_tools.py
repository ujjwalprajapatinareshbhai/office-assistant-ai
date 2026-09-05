from pathlib import Path

PROMPTS_DIR = Path("prompts")

def load_prompt(prompt_name:str):
    """Load a prompt from the prompts folder."""

    path = PROMPTS_DIR / f"{prompt_name}.md"

    if not path.exists():
        return f"Prompt '{prompt_name}' not found."

    return path.read_text(encoding="utf-8")