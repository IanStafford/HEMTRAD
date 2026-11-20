"""Build dashboard/cleanup-plan.html (the published clean-up plan page) from kb/workflow/cleanup-plan.md.

usage (from the repo root): python3 dashboard/build_cleanup_page.py
The markdown is the source of truth. This script converts the subset it uses (headings, paragraphs, nested bullet
and numbered lists, pipe tables, **bold**, `code`, [[wikilinks]]) and turns the appendix tables into filterable
finding rows. Model output and repo facts only; no measured numbers.
"""
import html
import re

SRC = "kb/workflow/cleanup-plan.md"
OUT = "dashboard/cleanup-plan.html"


def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[\[([^\]]+)\]\]", r'<span class="wl">\1</span>', t)
    return t


def table(rows, cls=""):
    head = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    out = [f'<div class="tw"><table class="{cls}"><thead><tr>' + "".join(f"<th>{inline(h)}</th>" for h in head) + "</tr></thead><tbody>"]
    for r in rows[2:]:
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", r.strip().strip("|"))]
        out.append("<tr>" + "".join(f"<td>{inline(c.replace(chr(92) + '|', '|'))}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def lists(lines):
    """Nested ul/ol from lines indented by multiples of 2 or 3 spaces."""
    out, stack = [], []
    for l in lines:
        ind = len(l) - len(l.lstrip(" "))
        s = l.strip()
        m = re.match(r"(\d+)\.\s+(.*)", s)
        kind, text = ("ol", m.group(2)) if m else ("ul", s[2:] if s.startswith("- ") else s)
        while stack and stack[-1][0] > ind:
            out.append(f"</li></{stack.pop()[1]}>")
        if stack and stack[-1][0] == ind:
            out.append("</li>")
        else:
            out.append(f"<{kind}>")
            stack.append((ind, kind))
        out.append(f"<li>{inline(text)}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "\n".join(out)


def body_html(md):
    out, i, L = [], 0, md.split("\n")
    sec = 0
    while i < len(L):
        l = L[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith("## "):
            title = l[3:].strip()
            sec += 1
            sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
            out.append(f'<h2 id="{sid}">{inline(title)}</h2>')
            i += 1
            continue
        if l.startswith("# "):
            i += 1          # page title is in the header
            continue
        if l.lstrip().startswith("|"):
            rows = []
            while i < len(L) and L[i].lstrip().startswith("|"):
                rows.append(L[i])
                i += 1
            out.append(table(rows))
            continue
        if re.match(r"\s*(- |\d+\.\s)", l):
            block = []
            while i < len(L) and (re.match(r"\s*(- |\d+\.\s)", L[i]) or (L[i].startswith("  ") and L[i].strip())):
                block.append(L[i])
                i += 1
            out.append(lists(block))
            continue
        para = []
        while i < len(L) and L[i].strip() and not L[i].startswith("#") and not L[i].lstrip().startswith("|") \
                and not re.match(r"\s*(- |\d+\.\s)", L[i]):
            para.append(L[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)


def appendix_html(md):
    """The appendix's per-slice tables become finding rows with severity chips and a filter."""
    parts = re.split(r"\n### ", md)
    intro, slices = parts[0], parts[1:]
    out = ['<div class="filters" role="group" aria-label="Filter findings by severity">'
           '<button type="button" class="f on" data-sev="all" id="f-all">All</button>'
           '<button type="button" class="f" data-sev="H" id="f-h">High</button>'
           '<button type="button" class="f" data-sev="M" id="f-m">Medium</button>'
           '<button type="button" class="f" data-sev="L" id="f-l">Low</button></div>']
    for sl in slices:
        head, _, rest = sl.partition("\n")
        rows = [r for r in rest.split("\n") if r.lstrip().startswith("|")][2:]
        out.append(f'<details class="slice" open><summary><span>{inline(head.strip())}</span></summary><ul class="fl">')
        for r in rows:
            c = [x.strip() for x in re.split(r"(?<!\\)\|", r.strip().strip("|"))]
            fid, sev, eff, ver, text, files = c[0], c[1], c[2], c[3], c[4].replace("\\|", "|"), c[5].replace("\\|", "|")
            vt = "confirmed" if ver == "✓" else "confirmed, corrected"
            out.append(f'<li class="fi" data-sev="{sev}"><span class="sev s{sev}">{ {"H": "High", "M": "Med", "L": "Low"}[sev] }</span>'
                       f'<span class="fid">{html.escape(fid)}</span><span class="txt">{inline(text)}'
                       f'<span class="meta">{inline(files)} · effort {eff} · {vt}</span></span></li>')
        out.append("</ul></details>")
    return "\n".join(out)


md = open(SRC).read()
md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
main, _, app = md.partition("\n## Appendix: all verified findings\n")
app_intro = app.split("\n### ", 1)[0].strip()
n_kept = len(re.findall(r"^\| [A-Z]+(?:-[A-Z]+)*-\d+ \|", app, flags=re.M))

CSS = """
:root{
  /* layout: one reading column with a sticky contents rail on wide screens */
  --bg:#f5f6f4; --panel:#ffffff; --ink:#17201f; --muted:#5d6866; --line:#dfe3e0; --accent:#0e6d68; --accent-soft:#e1efed;
  --hi:#b23a2e; --hi-bg:#f8e6e3; --md:#9a6a08; --md-bg:#f8efd9; --lo:#56636b; --lo-bg:#e9edef; --done:#2f7a3d; --done-bg:#e3f1e5;
  --f-body:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-head:"IBM Plex Sans Condensed","IBM Plex Sans",system-ui,sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#111716; --panel:#182120; --ink:#e3e9e7; --muted:#97a4a1; --line:#2b3634; --accent:#5cc2b9; --accent-soft:#1d3532;
  --hi:#f08b7f; --hi-bg:#3a1f1c; --md:#e4b65a; --md-bg:#362c16; --lo:#a9b4ba; --lo-bg:#252d31; --done:#7fcb8b; --done-bg:#1d3121; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#111716; --panel:#182120; --ink:#e3e9e7; --muted:#97a4a1; --line:#2b3634; --accent:#5cc2b9; --accent-soft:#1d3532;
  --hi:#f08b7f; --hi-bg:#3a1f1c; --md:#e4b65a; --md-bg:#362c16; --lo:#a9b4ba; --lo-bg:#252d31; --done:#7fcb8b; --done-bg:#1d3121; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.6 var(--f-body);margin:0}
.wrap{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:28px 64px;display:grid;grid-template-columns:200px minmax(0,1fr);gap:40px}
@media (max-width:860px){.wrap{grid-template-columns:minmax(0,1fr);gap:16px;padding-inline:16px}.rail{position:static!important}}
header{grid-column:1/-1;border-bottom:1px solid var(--line);padding-bottom:18px}
.eyebrow{font:600 12px/1 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
h1{font:600 clamp(26px,4vw,36px)/1.15 var(--f-head);margin:.35em 0 .3em;text-wrap:balance}
.lede{color:var(--muted);max-width:68ch;margin:0}
.stats{display:flex;flex-wrap:wrap;gap:8px 22px;margin-top:14px;font:500 13px/1.4 var(--f-mono);color:var(--muted)}
.stats b{color:var(--ink);font-weight:600}
.rail{position:sticky;top:calc(env(safe-area-inset-top,0px) + 16px);align-self:start;font-size:13px}
.rail a{display:block;color:var(--muted);text-decoration:none;padding:5px 0 5px 10px;border-left:2px solid var(--line)}
.rail a:hover,.rail a:focus-visible{color:var(--ink);border-left-color:var(--accent)}
main{min-width:0;max-width:78ch}
h2{font:600 22px/1.25 var(--f-head);margin:2.2em 0 .6em;padding-top:.2em;text-wrap:balance;scroll-margin-top:16px}
main>h2:first-child{margin-top:.4em}
p{margin:.7em 0}
ul,ol{padding-left:1.3em;margin:.5em 0}
li{margin:.3em 0}
li>ul,li>ol{margin:.25em 0}
strong{font-weight:600}
code{font:500 .86em/1 var(--f-mono);background:var(--accent-soft);padding:.12em .35em;border-radius:3px;word-break:break-word}
.wl{color:var(--accent);font-weight:500}
.tw{overflow-x:auto;margin:1em 0;border:1px solid var(--line);border-radius:6px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.45}
th,td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
th{font:600 12px/1.3 var(--f-head);letter-spacing:.04em;text-transform:uppercase;color:var(--muted);background:var(--bg)}
tr:last-child td{border-bottom:0}
td:first-child{font-weight:500}
.decisions ol>li{margin:.8em 0}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:1em 0}
.f{font:500 13px/1 var(--f-body);color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.f.on{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.f:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
details.slice{border:1px solid var(--line);border-radius:6px;background:var(--panel);margin:.7em 0}
details.slice>summary{cursor:pointer;padding:11px 14px;font:600 15px/1.3 var(--f-head)}
details.slice>summary:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.fl{list-style:none;margin:0;padding:0 0 4px}
.fi{display:grid;grid-template-columns:auto auto minmax(0,1fr);gap:4px 10px;align-items:baseline;padding:9px 14px;border-top:1px solid var(--line);font-size:14px}
.fi[hidden]{display:none!important}
.sev{font:600 11px/1 var(--f-mono);letter-spacing:.04em;text-transform:uppercase;padding:4px 7px;border-radius:4px;min-width:3.6em;text-align:center}
.sH{color:var(--hi);background:var(--hi-bg)} .sM{color:var(--md);background:var(--md-bg)} .sL{color:var(--lo);background:var(--lo-bg)}
.fid{font:600 12.5px/1 var(--f-mono);color:var(--muted);white-space:nowrap}
.txt{min-width:0}
.meta{display:block;color:var(--muted);font-size:12.5px;margin-top:3px;overflow-wrap:anywhere}
.meta code{background:none;padding:0}
.note{border-left:3px solid var(--accent);background:var(--accent-soft);padding:10px 14px;border-radius:0 6px 6px 0;margin:1em 0}
.done{display:inline-block;font:600 11px/1 var(--f-mono);letter-spacing:.04em;text-transform:uppercase;color:var(--done);background:var(--done-bg);padding:4px 7px;border-radius:4px;margin-right:6px}
@media (max-width:520px){.fi{grid-template-columns:auto minmax(0,1fr)}.fid{grid-column:2}.txt{grid-column:1/-1}}
@media (prefers-reduced-motion:no-preference){.f{transition:background .15s,color .15s}}
"""

main_html = body_html(main)
main_html = main_html.replace("<strong>DONE 2026-11-20", '<span class="done">Done Nov 20</span><strong>', 1)
# wrap the decisions list
main_html = re.sub(r'(<h2 id="1-decisions-for-ian[^"]*">.*?</h2>\s*)(<ol>.*?</ol>)', r'\1<div class="decisions">\2</div>', main_html, count=1, flags=re.S)
toc = "".join(f'<a href="#{m.group(1)}">{m.group(2)}</a>' for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', main_html))
toc += '<a href="#appendix">Appendix: all findings</a>'

page = f"""<title>HEMTRAD Clean-up Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <div class="eyebrow">FLOOXS HEMT model · repo survey · 2026-11-20</div>
  <h1>HEMTRAD Clean-up Plan</h1>
  <p class="lede">A staged, behaviour-preserving plan to make the code and knowledge base easier to read, plus the conflicts found in the KB. Every finding was checked by a second, independent reviewer.</p>
  <div class="stats"><span><b>156</b> findings</span><span><b>{n_kept}</b> kept</span><span><b>115</b> confirmed</span><span><b>40</b> confirmed with corrections</span><span><b>1</b> refuted</span></div>
</header>
<nav class="rail" aria-label="Contents">{toc}</nav>
<main>
{main_html}
<h2 id="appendix">Appendix: all verified findings</h2>
<p>{inline(app_intro.splitlines()[0]) if app_intro else ''}</p>
{appendix_html(app)}
</main>
</div>
<script>
(function(){{
  var btns=[].slice.call(document.querySelectorAll('.f'));
  var rows=[].slice.call(document.querySelectorAll('.fi'));
  function apply(sev){{
    btns.forEach(function(b){{b.classList.toggle('on',b.dataset.sev===sev);b.setAttribute('aria-pressed',b.dataset.sev===sev)}});
    rows.forEach(function(r){{r.hidden=!(sev==='all'||r.dataset.sev===sev)}});
    try{{localStorage.setItem('cleanupSev',sev)}}catch(e){{}}
  }}
  btns.forEach(function(b){{b.addEventListener('click',function(){{apply(b.dataset.sev)}})}});
  var s='all';try{{s=localStorage.getItem('cleanupSev')||'all'}}catch(e){{}}
  apply(['all','H','M','L'].indexOf(s)>=0?s:'all');
}})();
</script>
"""
open(OUT, "w").write(page)
print("wrote", OUT, len(page) // 1024, "kB;", n_kept, "findings")
