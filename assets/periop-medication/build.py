"""根拠台帳・画面・判定コードを外部依存のない単一HTMLへ組み立てる。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / 'evidence.json').read_text(encoding='utf-8'))
html = (ROOT / 'page.html').read_text(encoding='utf-8')
html = html.replace('/*__DATA__*/', 'var PERIOP_DATA = ' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + ';')
html = html.replace('/*__APP__*/', (ROOT / 'app.js').read_text(encoding='utf-8'))
target = ROOT.parent.parent / 'periop_medication_navigator.html'
target.write_text(html, encoding='utf-8')
print(f'Built {target.name}: {len(data["drugs"])} entries / {len(data["rules"])} rules')
