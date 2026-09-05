from pathlib import Path
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "checkpoints.db"


def create_memory():
    return AsyncSqliteSaver.from_conn_string(
        str(DB_PATH)
    )