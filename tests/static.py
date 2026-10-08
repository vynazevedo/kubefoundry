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

import ast
for script in (root / "scripts").glob("*.py"):
    ast.parse(script.read_text(), filename=str(script))
for script in (root / "tests").glob("*.py"):
    ast.parse(script.read_text(), filename=str(script))
print("Python syntax passed")

versions = dict(line.split('=', 1) for line in (root / 'versions.env').read_text().splitlines()
                if line and not line.startswith('#'))
observability = json.loads((root / 'labs/advanced/observability.json').read_text())
images = {item['metadata']['name']: item['spec']['template']['spec']['containers'][0]['image']
          for item in observability['items'] if item['kind'] == 'Deployment'}
for name, key in [('collector', 'OTEL_COLLECTOR_VERSION'), ('jaeger', 'JAEGER_VERSION'),
                  ('prometheus', 'PROMETHEUS_VERSION')]:
    assert images[name].rsplit(':', 1)[1] == versions[key], f'{name} image differs from versions.env'
print('Observability image pins match the version inventory')
