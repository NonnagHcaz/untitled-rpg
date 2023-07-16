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
    if hasattr(sys, "_MEIPASS"):
        # Running in bundled executable mode
        base_path = sys._MEIPASS
    else:
        # Running in development mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
