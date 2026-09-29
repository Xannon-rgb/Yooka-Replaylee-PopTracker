"""Prepare the 2.70.0 launch ZIP from the verified original release."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

SOURCE_SHA = "cb888f3acaf48f3af84775d9102b3c599c1d6541e8b756dbf0d9e594c7cd8b98"

def build(source, output):
    source, output = Path(source), Path(output)
    if hashlib.sha256(source.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("Source does not match the audited release; refusing to rebuild")
    with zipfile.ZipFile(source) as pack:
        if pack.testzip() is not None:
            raise ValueError("Source ZIP is corrupt")
        manifest = json.loads(pack.read("manifest.json"))
        assert manifest["package_version"] == "2.62.0"
        assert manifest["package_uid"] == "yooka_replaylee_ap_quill_tracker"
        manifest["package_version"] = "2.70.0"
        manifest["version"] = "2.70.0"
        manifest["name"] = "Yooka-Replaylee World Map Tabs v2.70.0"
        for variant in manifest["variants"].values():
            variant["display_name"] = variant["display_name"].replace("v2.62", "v2.70.0")
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as fixed:
            for info in pack.infolist():
                data = pack.read(info.filename)
                if info.filename == "manifest.json":
                    data = (json.dumps(manifest, indent=2) + "\n").encode()
                elif info.filename.endswith(".json"):
                    json.loads(data)
                fixed.writestr(info, data)
    with zipfile.ZipFile(source) as before, zipfile.ZipFile(output) as after:
        assert after.testzip() is None
        assert before.namelist() == after.namelist()
        for name in before.namelist():
            if name != "manifest.json":
                assert before.read(name) == after.read(name), name
        assert json.loads(after.read("manifest.json"))["package_version"] == "2.70.0"
    print("Validated launch ZIP:", output.name, hashlib.sha256(output.read_bytes()).hexdigest())

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
