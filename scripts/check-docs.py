"""Check repository-local Markdown links and image paths without network access."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.paths.extend(value for key, value in attrs if key == 'src' and value)

errors = []
files = [ROOT / 'README.md', *sorted((ROOT / 'docs').rglob('*.md'))]
for source in files:
    text = source.read_text()
    text = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
    html = Images()
    html.feed(text)
    links = re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', text) + html.paths
    for link in links:
        parsed = urlsplit(link)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (ROOT / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/')
                  else source.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f'{source.relative_to(ROOT)} -> {link}')
if errors:
    raise SystemExit('Broken local documentation links:\n' + '\n'.join(errors))
print(f'Validated local links and image paths in {len(files)} Markdown files')
