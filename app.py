"""Root Streamlit entry point for preview runners.

The actual app lives in frontend/app.py. Keeping this thin wrapper lets tools
that expect app.py at the repository root launch the preview correctly.
"""

from pathlib import Path
import runpy


APP_PATH = Path(__file__).parent / "frontend" / "app.py"

runpy.run_path(str(APP_PATH), run_name="__main__")
