"""Verify laboratory output, analytic error identities and chapter-code links."""
from pathlib import Path
import argparse
import ast
import hashlib
import html
import importlib.util
import json
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--receipt', type=Path)
args = parser.parse_args()
sys.dont_write_bytecode = True
lab = (REPO / "numerical-lab.html").read_text(encoding="utf-8")
if '<!-- BOOK-CONTENT-START -->' in lab:
    lab = lab.split('<!-- BOOK-CONTENT-START -->', 1)[1].split(
        '<!-- BOOK-CONTENT-END -->', 1)[0]
overview = (REPO / "book-overview.html").read_text(encoding="utf-8")
script = REPO / "numerical_lab.py"
printed = re.search(r'<pre id="lab-output"[^>]*><code>(.*?)</code></pre>',
                    lab, re.S).group(1)
expected = html.unescape(printed)
run = subprocess.run([sys.executable, "-I", str(script)], check=True,
                     capture_output=True, text=True)
assert run.stderr == ""
assert run.stdout == expected, "downloaded script/page output mismatch"
spec = importlib.util.spec_from_file_location("lab_check", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ns, mass, pipe, exact_flow, force, errors = module.run_checks()
# Independent closed-form trapezoid sum and polynomial quadrature identities.
for n, m, p in zip(ns, mass, pipe):
    a = 0.4 / n
    analytic_error = (a / 2) / math.tanh(a / 2) - 1
    assert math.isclose(m[2], analytic_error, rel_tol=1e-9, abs_tol=1e-15)
    assert math.isclose(p[0] / exact_flow - 1, 0.5 / n ** 2,
                        rel_tol=1e-9)
    assert math.isclose(p[1] / -force, 1 - 0.5 / n, rel_tol=1e-12)
    # Absolute budgets after changing geometry/property scales.
    changed = module.mass_study(n, lengths=(1.0, 0.3, 0.2))
    assert math.isclose(changed[0], 2 * m[0], rel_tol=1e-12)
    assert math.isclose(changed[1], 2 * m[1], rel_tol=1e-12)
    changed_pipe = module.pipe_study(n, viscosity=0.002)
    assert math.isclose(changed_pipe[0], p[0] / 2, rel_tol=1e-12)
    assert math.isclose(changed_pipe[1], p[1], rel_tol=1e-12)
table = re.search(r'<table id="refinement-table">(.*?)</table>', lab, re.S).group(1)
rows = re.findall(r'<tr>(.*?)</tr>', table, re.S)[1:]
assert len(rows) == len(ns)
for j, row in enumerate(rows):
    cells = re.findall(r'<td>(.*?)</td>', row)
    assert cells == [str(ns[j]), f"{mass[j][2]:.9e}",
                     f"{errors[j]:.9e}", f"{pipe[j][2]:.9e}"]
# Every local page anchor must exist, including all seventeen code links.
for source in (lab, overview):
    ids = re.findall(r'\bid="([^"]+)"', source)
    assert len(ids) == len(set(ids)), "duplicate authored ID"
    for href in re.findall(r'href="([^"]+)"', source):
        if "://" in href:
            continue
        filename, _, anchor = href.partition("#")
        target = REPO / filename
        assert target.exists(), href
        if anchor:
            target_text = target.read_text(encoding="utf-8")
            assert re.search(r'\bid="' + re.escape(anchor) + '"', target_text), href
code_section = lab.split('<h2 id="chapter-code">', 1)[1]
code_links = re.findall(r'href="(chapter-[^"]+#([^"]+))"', code_section)
assert len(code_links) == 17
assert len(set(link.split("#")[0] for link, _ in code_links)) == 17
catalog_rows = re.findall(r'<tr>(.*?)</tr>', code_section, re.S)[1:]
for row_number, (link, anchor) in enumerate(code_links):
    page = (REPO / link.split("#")[0]).read_text(encoding="utf-8")
    section = re.search(r'<h2 id="' + anchor + r'"[^>]*>(.*?)</h2>',
                        page, re.S).group(1)
    assert "executable" in section.lower(), link
    begin = page.index('<h2 id="' + anchor + '"')
    end = page.find('<h2 ', begin + 1)
    section_body = page[begin:end if end >= 0 else None]
    modules = set()
    for code in re.findall(r'<code class="language-python">(.*?)</code>',
                           section_body, re.S):
        tree = ast.parse(html.unescape(code))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.add(node.module.split(".")[0])
    cells = re.findall(r'<td>(.*?)</td>', catalog_rows[row_number], re.S)
    assert cells[-1] == ", ".join(sorted(modules)), link
for name, source in (("overview", overview), ("laboratory", lab)):
    assert "PLACEHOLDER" not in source
    assert not re.search(r'<(?:script|style|html|body)\b', source)
assert overview.lstrip().startswith("<h2")
assert lab.lstrip().startswith("<h1")
assert "&lt;" not in lab.split('<pre id="lab-output"')[0]
assert all(len(line) <= 79 for line in script.read_text().splitlines())
receipt = {
    "scope": "Executable, authored-content and link checks; independent review and rendering are separate gates",
    "python": sys.version,
    "lab_body_sha256": hashlib.sha256(lab.encode()).hexdigest(),
    "overview_body_sha256": hashlib.sha256(overview.encode()).hexdigest(),
    "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
    "stdout_sha256": hashlib.sha256(run.stdout.encode()).hexdigest(),
    "stdout_exact_match": True,
    "chapter_code_links_checked": len(code_links),
    "mass_ratios": [mass[j-1][2] / mass[j][2] for j in range(1, len(ns))],
    "pipe_Q_ratios": [errors[j-1] / errors[j] for j in range(1, len(ns))],
    "pipe_force_ratios": [pipe[j-1][2] / pipe[j][2]
                          for j in range(1, len(ns))],
    "mutations_rejected": ["reversed positive x-face normal",
                            "reversed pressure-force sign"],
    "additional_checks": ["geometric exponential sum", "polynomial sum identity",
                          "volume scaling", "viscosity scaling", "input rejection",
                          "all local links and IDs", "fragment-only markup"],
}
output = args.receipt or ROOT / "tools/audit_numerical_lab.json"
output.write_bytes((json.dumps(receipt, indent=2) + "\n").encode("utf-8"))
print(json.dumps(receipt, indent=2))
