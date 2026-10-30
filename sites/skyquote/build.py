"""Entry point for the independently stored V5 Skyquote preview generator.

Run: python sites/skyquote/build.py
Actual WebP binaries are mandatory; missing assets fail closed.
"""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[2]
if __name__=="__main__":
    runpy.run_path(str(ROOT/"scripts"/"build_skyquote.py"),run_name="__main__")
