import glob
import os


def get_filepaths(directory, *accepts):
    filepaths = []
    if not len(accepts):
        accepts = [".*"]
    for accept in accepts:
        filepaths += glob.glob(os.path.join(directory, f"**{accept}"), recursive=True)
    return filepaths
