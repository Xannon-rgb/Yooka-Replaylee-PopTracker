"""Publish the audited 2.70.0 correction while preserving the original ZIP."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from prepare_launch import build

REPO = "Xannon-rgb/Yooka-Replaylee-PopTracker"
TAG = "v2.70"
SOURCE_ID = 599448797
FINAL_NAME = "Yooka-Replaylee_PopTracker_v2.70.0.zip"
STAGED_NAME = "launch-candidate-2.70.0.zip"
PREFIX = f"repos/{REPO}"

def gh(*args, binary=False):
    result = subprocess.check_output(["gh", *args])
    return result if binary else result.decode()

def api(path, *args):
    return json.loads(gh("api", path, *args))

def run():
    if os.environ.get("GITHUB_REPOSITORY") != REPO:
        raise ValueError("This correction is scoped to the intended repository")
    directory = Path(os.environ["RUNNER_TEMP"]) / "poptracker-launch"
    directory.mkdir(exist_ok=True)
    source = directory / "original.zip"
    source.write_bytes(gh("api", f"{PREFIX}/releases/assets/{SOURCE_ID}",
                          "-H", "Accept: application/octet-stream", binary=True))
    target = directory / STAGED_NAME
    build(source, target)
    digest = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
    release = api(f"{PREFIX}/releases/tags/{TAG}")
    current = next((a for a in release["assets"] if a["name"] == FINAL_NAME), None)
    if current is None or current.get("digest") != digest:
        if current and current["id"] != SOURCE_ID:
            raise ValueError("Another launch build exists; refusing to overwrite it")
        staged = next((a for a in release["assets"] if a["name"] == STAGED_NAME), None)
        if staged and staged.get("digest") != digest:
            raise ValueError("Unexpected staged asset; refusing to overwrite it")
        if staged is None:
            gh("release", "upload", TAG, str(target), "--repo", REPO)
            release = api(f"{PREFIX}/releases/tags/{TAG}")
            staged = next(a for a in release["assets"] if a["name"] == STAGED_NAME)
        if staged.get("digest") != digest:
            raise ValueError("Uploaded launch ZIP checksum mismatch")
        if current:
            api(f"{PREFIX}/releases/assets/{SOURCE_ID}", "--method", "PATCH",
                "-f", "name=archived-v2.62.0-original.zip",
                "-f", "label=Archived original v2.62.0 (recovery copy)")
        api(f"{PREFIX}/releases/assets/{staged['id']}", "--method", "PATCH",
            "-f", "name=" + FINAL_NAME,
            "-f", "label=Yooka-Replaylee PopTracker 2.70.0")
    gh("release", "edit", TAG, "--repo", REPO,
       "--title", "Yooka-Replaylee PopTracker 2.70.0",
       "--notes-file", ".github/release-notes-2.70.0.md")
    release = api(f"{PREFIX}/releases/tags/{TAG}")
    installed = next(a for a in release["assets"] if a["name"] == FINAL_NAME)
    assert installed.get("digest") == digest
    print("Published verified launch ZIP:", installed["browser_download_url"])

if __name__ == "__main__":
    run()
