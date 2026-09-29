"""Build PopTracker's update feed from published release ZIP assets."""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import urllib.request
import zipfile

REPO = os.environ.get("GITHUB_REPOSITORY", "Xannon-rgb/Yooka-Replaylee-PopTracker")
FEED_URL = f"https://raw.githubusercontent.com/{REPO}/main/versions.json"
UID = "yooka_replaylee_ap_quill_tracker"

def fetch(url):
    headers = {"User-Agent": "Yooka-Replaylee-release-index"}
    if url.startswith("https://api.github.com/") and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()

def main():
    path = Path("versions.json")
    previous = json.loads(path.read_text())["versions"] if path.exists() else []
    by_version = {entry["package_version"]: entry for entry in previous}
    cached = {(entry["download_url"], entry.get("sha256")): entry for entry in previous}
    releases = json.loads(fetch(f"https://api.github.com/repos/{REPO}/releases?per_page=100"))
    # Process older releases first so the newest asset wins for a repeated version.
    for release in reversed(releases):
        if release["draft"] or release["prerelease"]:
            continue
        assets = [a for a in release["assets"] if a["state"] == "uploaded"
                  and a["name"].startswith("Yooka-Replaylee_PopTracker_")
                  and a["name"].endswith(".zip")]
        if not assets:
            continue
        if len(assets) != 1:
            raise ValueError(f"Expected one pack ZIP in {release['tag_name']}")
        asset = assets[0]
        url = asset["browser_download_url"]
        digest = (asset.get("digest") or "").removeprefix("sha256:")
        if (url, digest) in cached:
            entry = cached[(url, digest)]
        else:
            data = fetch(url)
            checksum = hashlib.sha256(data).hexdigest()
            if digest and checksum != digest:
                raise ValueError("Release asset checksum mismatch")
            with zipfile.ZipFile(io.BytesIO(data)) as pack:
                if pack.testzip() is not None:
                    raise ValueError("Corrupt ZIP")
                manifests = [n for n in pack.namelist() if n == "manifest.json"
                             or (n.count("/") == 1 and n.endswith("/manifest.json"))]
                if len(manifests) != 1:
                    raise ValueError("Expected one pack manifest")
                manifest = json.loads(pack.read(manifests[0]))
            if manifest.get("package_uid") != UID:
                raise ValueError("Wrong pack UID")
            if manifest.get("versions_url") != FEED_URL:
                raise ValueError("Pack must point to this repository's versions.json")
            version = manifest["package_version"]
            if not re.fullmatch(r"\d+(?:\.\d+)*", version):
                raise ValueError("Use a numeric package_version, for example 2.71.0")
            entry = {
                "package_version": version,
                "download_url": url,
                "sha256": checksum,
                "changelog": (release.get("body") or "Published release.").splitlines(),
            }
            if release["tag_name"].lstrip("v") != version:
                print(f"Release {release['tag_name']} contains pack {version}; using internal version.")
        by_version[entry["package_version"]] = entry
    if not by_version:
        raise ValueError("No published pack ZIPs found")
    entries = sorted(by_version.values(),
                     key=lambda e: tuple(map(int, e["package_version"].split("."))),
                     reverse=True)
    path.write_text(json.dumps({"versions": entries}, indent=2) + "\n")
    print(f"Indexed {len(entries)} versions; latest internal version: {entries[0]['package_version']}")

if __name__ == "__main__":
    main()
