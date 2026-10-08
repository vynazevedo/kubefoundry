import json
import pathlib
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
subprocess.run(["helm", "lint", str(root / "charts/demo"), "--strict"], check=True)
subprocess.run(["helm", "template", "demo", str(root / "charts/demo")], check=True, stdout=subprocess.DEVNULL)
for script in (root / "scripts").glob("*.sh"):
    subprocess.run(["bash", "-n", str(script)], check=True)
for path in root.rglob("*.json"):
    if not any(part.startswith(".") for part in path.relative_to(root).parts):
        json.loads(path.read_text())
print("Chart rendering and shell syntax passed")
