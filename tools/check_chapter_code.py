"""Run complete chapter programs in isolated processes and compare printed output."""
import datetime
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
results = {}
with tempfile.TemporaryDirectory(prefix='fluid-chapter-checks-') as folder:
    work = Path(folder)
    for path in sorted(ROOT.glob('chapter-[0-9][0-9]-*.html')):
        text = path.read_text(encoding='utf-8')
        body = text.split('<!-- BOOK-CONTENT-START -->', 1)[1].split(
            '<!-- BOOK-CONTENT-END -->', 1)[0]
        blocks = re.findall(r'<pre\b[^>]*>\s*<code([^>]*)>(.*?)</code>\s*</pre>',
                            body, re.S)
        checks = []
        for i, (attrs, source) in enumerate(blocks):
            if 'language-python' not in attrs:
                continue
            assert i + 1 < len(blocks) and 'language-python' not in blocks[i + 1][0]
            code = html.unescape(source)
            expected = html.unescape(blocks[i + 1][1]).strip('\n')
            script = work / f'chapter_{path.name[8:10]}_{i}.py'
            script.write_bytes(code.encode('utf-8'))
            run = subprocess.run([sys.executable, '-I', str(script)], cwd=work,
                                 capture_output=True, text=True, encoding='utf-8',
                                 timeout=120, env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            passed = run.returncode == 0 and run.stdout.rstrip('\n') == expected
            checks.append({'block': i, 'returncode': run.returncode,
                           'output_matches': passed,
                           'listing_sha256': hashlib.sha256(code.encode()).hexdigest(),
                           'stdout_sha256': hashlib.sha256(run.stdout.encode()).hexdigest(),
                           'stderr': run.stderr[-1500:]})
        status = 'passed' if checks and all(c['output_matches'] for c in checks) else 'failed'
        results[path.name] = {'status': status,
                              'body_sha256': hashlib.sha256(body.encode()).hexdigest(),
                              'checks': checks}
        print(path.name, status)
report = {'scope': 'Actual isolated chapter programs compared with displayed output; universal-newline normalization and terminal-newline trimming',
          'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'python': sys.version, 'chapters': results}
(ROOT / 'chapter-code-validation.json').write_bytes((json.dumps(report, indent=2) + '\n').encode())
raise SystemExit(0 if len(results) == 17 and all(r['status'] == 'passed' for r in results.values()) else 1)
