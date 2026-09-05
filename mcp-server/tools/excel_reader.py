import pandas as pd
from pathlib import Path

FILES_DIR = Path("files")

def read_excel(filename: str):

    path = FILES_DIR / filename

    df = pd.read_excel(path)

    return df.to_string(index=False)