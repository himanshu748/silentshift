import sys
from pathlib import Path

# Keep the core importable inside IRIS through PYTHONPATH and in local tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
