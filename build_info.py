"""Visible runtime identity without credentials or environment dumps."""
from pathlib import Path
import subprocess
import streamlit

def build_info():
    root=Path(__file__).resolve().parent
    def git(*args):
        try:return subprocess.check_output(['git','-C',str(root),*args],text=True,stderr=subprocess.DEVNULL,timeout=2).strip()
        except (OSError,subprocess.SubprocessError):return 'unavailable'
    return {'working_tree_has_changes':bool(git('status','--porcelain')),'commit':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'entry_point':'app.py','streamlit':streamlit.__version__}
