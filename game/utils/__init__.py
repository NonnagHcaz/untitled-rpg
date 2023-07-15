import glob
import sys
import os


def get_filepaths(directory, *accepts):
    filepaths = []
    if not len(accepts):
        accepts = [".*"]
    for accept in accepts:
        filepaths += glob.glob(os.path.join(directory, f"**{accept}"), recursive=True)
    return filepaths


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
