import os
import time
from pathlib import Path

from core.message import Message
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


# ============================================================
# TAVILY CONFIGURATION
# ============================================================

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(
    api_key=TAVILY_API_KEY
)


# ============================================================
# FILE DIRECTORY
# ============================================================

FILES_DIR = Path("files")


# ============================================================
# WEB SEARCH
# ============================================================

def search(query: str):
    """
    Search the web using Tavily.

    Temporary network/API failures are retried automatically
    before returning an error.
    """

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:

            print(
                f"🌐 Tavily web search "
                f"(attempt {attempt}/{max_retries}): {query}"
            )

            result = client.search(
                query=query
            )

            print(
                "✅ Tavily web search completed."
            )

            return result

        except Exception as e:

            print(
                f"⚠️ Tavily search attempt "
                f"{attempt}/{max_retries} failed: {e}"
            )

            # If this was the final attempt,
            # return the error instead of retrying.
            if attempt == max_retries:

                print(
                    "❌ Tavily web search failed "
                    "after all retry attempts."
                )

                return f"Error: {str(e)}"

            # Exponential backoff:
            #
            # Attempt 1 → wait 1 second
            # Attempt 2 → wait 2 seconds
            #
            # This gives temporary network problems
            # time to recover.

            wait_time = 2 ** (attempt - 1)

            print(
                f"🔁 Retrying Tavily search "
                f"in {wait_time} second(s)..."
            )

            time.sleep(
                wait_time
            )


# ============================================================
# SEARCH ALL FILES
# ============================================================

def search_all_file(keyword: str):
    """
    Search all files for a keyword.

    Progress messages are yielded while files are scanned.
    """

    results = []

    files = [
        file
        for file in FILES_DIR.iterdir()
        if file.is_file()
    ]

    for index, file in enumerate(
        files,
        start=1
    ):

        yield Message.progress(
            current=index,
            total=len(files),
            filename=file.name
        )

        try:

            content = file.read_text(
                encoding="utf-8"
            )

        except (
            UnicodeDecodeError,
            PermissionError,
            OSError,
        ) as e:

            print(
                f"Could not read {file}: {e}"
            )

            continue

        if keyword.lower() in content.lower():

            lines = content.splitlines()

            for line_number, line in enumerate(
                lines,
                start=1
            ):

                if keyword.lower() in line.lower():

                    results.append(
                        {
                            "file": file.name,
                            "line": line_number,
                            "text": line,
                        }
                    )

    yield Message.result(
        results
    )