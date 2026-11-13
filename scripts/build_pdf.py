#!/usr/bin/env python3
"""Generate a polished, searchable A4 PDF from the repository's canonical content.

All chapters and action cards are sourced from tracked Markdown/JSON. No invented results.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf" / "how-to-get-offer-guide.pdf"
EDITION = ROOT / "pdf" / "edition.json"
LINK_ROOT = "https://github.com/AIPMAndy/how-to-get-offer/blob/main/"
CHAPTERS = [
    ("01", "六步求职路线", sorted((ROOT / "guides").glob("0[0-6]-*.md"))),
    ("02", "进阶工作坊与 30 天计划", sorted((ROOT / "guides").glob("0[7-9]-*.md")) + sorted((ROOT / "guides").glob("1[0-3]-*.md")) + [ROOT / "guides" / "30-day-plan.md"]),
    ("03", "现实问题与排障指南", sorted((ROOT / "playbooks").glob("*.md"))),
    ("04", "可复制求职模板", sorted((ROOT / "templates").glob("*.md"))),
    ("05", "教学案例与事实依据", sorted((ROOT / "examples").glob("*.md")) + [ROOT / "SOURCES.md"]),
]
STYLE = r"""
@page {
 size:A4; margin:19mm 18mm 19mm;
 @top-left {content:"XINGJUE  /  CAREER FIELD NOTES";font:7.5pt "Noto Sans CJK SC";color:#708097;letter-spacing:.09em}
 @top-right {content:string(chapter);font:7.5pt "Noto Sans CJK SC";color:#708097}
 @bottom-left {content:"AI 酋长 Andy  ·  微信 AIPMAndy";font:7.5pt "Noto Sans CJK SC";color:#708097}
 @bottom-right {content:counter(page);font:8pt "Noto Sans CJK SC";color:#708097}
}
@page:first {margin:0;@top-left{content:none}@top-right{content:none}@bottom-left{content:none}@bottom-right{content:none}}
*{box-sizing:border-box}
html{font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif;color:#172638;font-size:9.2pt}
body{margin:0;line-height:1.8}
a{color:#24548d;text-decoration:none}
p{margin:2mm 0 3mm;orphans:3;widows:3}
li{margin:1.2mm 0;orphans:2;widows:2}
ol,ul{padding-left:6mm}
h1,h2,h3,h4{line-height:1.28;letter-spacing:-.02em;break-after:avoid;color:#14243a}
h1{font-size:20pt;margin:5mm 0}h2{font-size:14pt;margin:7mm 0 3mm}
h3{font-size:11pt;margin:5mm 0 2mm}
pre{background:#152339;color:#ecf2f7;padding:4mm;white-space:pre-wrap;overflow-wrap:anywhere;font:7.5pt/1.6 monospace;border-radius:2mm}
code{font:8pt monospace;background:#eef2f6;padding:.3mm 1mm;overflow-wrap:anywhere}
pre code{background:none;color:inherit;padding:0}
blockquote{padding:4mm 5mm;border-left:2px solid #38699c;background:#eff4f9;color:#42566e;margin:4mm 0}
blockquote p{margin:0}
table{border-collapse:collapse;width:100%;font-size:8pt;table-layout:fixed;margin:3mm 0}
th,td{padding:2mm 2.3mm;border:1px solid #dce4eb;vertical-align:top;word-break:break-word;overflow-wrap:anywhere}
th{background:#edf2f8}
img{max-width:100%;height:auto}
hr{border:0;border-top:1px solid #dae1e9;margin:6mm 0}
.cover{height:297mm;background:#111e30;color:white;page-break-after:always;padding:32mm 26mm;position:relative}
.cover .kicker{letter-spacing:.2em;color:#adcae8;font-size:9pt;margin-bottom:26mm}
.cover h1{color:#fff;font-size:38pt;letter-spacing:-.045em;line-height:1.18;margin:0 0 12mm}
.cover em{font-style:normal;color:#b8d2ea}
.cover .sub{font-size:14.5pt;color:#c7d5e4;line-height:1.75;max-width:142mm}
.cover .sep{height:1px;background:#61768b;margin:26mm 0 13mm}
.cover .metrics{display:flex;gap:11mm}
.cover .metrics b{display:block;color:#fff;font-size:24pt;line-height:1.16}
.cover .metrics small{color:#a8bcd0;font-size:8.5pt}
.cover .bottom{position:absolute;left:26mm;bottom:24mm;color:#c3d0dd;font-size:10pt;line-height:1.9}
.intro{page-break-after:always}
.kicker{font-size:8pt;color:#35638f;letter-spacing:.15em;font-weight:700}
.intro h2{font-size:24pt;margin:5mm 0}
.notice{background:#f0f4f8;border-left:3px solid #376a9b;padding:4mm 5mm;margin:5mm 0}
.toc{margin-top:7mm}
.toc-group{margin:5mm 0;break-inside:avoid}
.toc-group h3{font-size:11.2pt;margin:1mm 0 2mm}
.toc-row{padding:1.2mm 0;border-bottom:1px solid #e3e8ed}
.toc-row a{display:block;color:#2b4868;font-size:8.7pt}
.toc-row a:after{content:target-counter(attr(href),page);float:right;color:#8191a3}
.part{page-break-before:always;padding-top:28mm}
.part h2{font-size:26pt;margin:5mm 0;color:#14243a}
.part p{font-size:11pt;color:#637387}
.chapter{page-break-before:always}
.chapter-head{border-bottom:1px solid #dae2eb;padding-bottom:5mm;margin-bottom:6mm}
.chapter-head h2{font-size:20pt;margin:2mm 0;string-set:chapter content()}
.chapter-head p{font-size:8.2pt;color:#708094;overflow-wrap:anywhere;margin:0}
.chapter-body h1{font-size:15pt}
.chapter-body h2{font-size:13.5pt}
.chapter-body h3{font-size:10.5pt}
.task-intro{page-break-before:always}
.task-intro h2{font-size:24pt}
.task-group h3{font-size:15pt;border-bottom:1px solid #dbe3ec;padding-bottom:3mm}
.task{border:1px solid #dce5ec;border-radius:3mm;padding:3.5mm 4.5mm;margin:3mm 0;break-inside:avoid}
.task .number{color:#366899;font-size:7.4pt;font-weight:700}
.task b{color:#14253c}
.task p{font-size:8.5pt;margin:1mm 0;line-height:1.64}
.task .small{color:#55687d}
.contact{page-break-before:always;background:#111e30;color:white;padding:28mm 23mm;min-height:215mm}
.contact h2{font-size:29pt;color:#fff;margin:8mm 0 10mm}
.contact p{font-size:11pt;color:#cddae8}
.contact a{color:#cfe5fc}
.contact ul{padding:0;list-style:none;margin:13mm 0}
.contact li{border-bottom:1px solid #496077;padding:4mm 0;font-size:10.5pt}
.contact .legal{font-size:8.5pt;color:#b3c2d0;margin-top:24mm}
"""

def e(value): return html.escape(str(value), quote=True)

def page_title(path):
    found = re.search(r"^#\s+(.+)$", path.read_text("utf-8"), re.M)
    return found.group(1).strip() if found else path.stem

def rewrite_links(text, path):
    def update(match):
        label, target = match.group(1), match.group(2)
        if urlsplit(target).scheme or target.startswith(("#", "mailto:")):
            return match.group(0)
        relative = posixpath.normpath(posixpath.join(path.relative_to(ROOT).parent.as_posix(), target))
        if relative.startswith("../"): return match.group(0)
        return f"[{label}]({LINK_ROOT}{relative})"
    return re.sub(r"(?<!!)\[([^\]\n]+)\]\(([^)\s]+)\)", update, text)

def content_checksum(paths, tasks_path):
    digest = sha256(Path(__file__).read_bytes())
    for path in sorted(set(paths + [tasks_path])):
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()

def build():
    import markdown
    from weasyprint import HTML
    active = [(code, label, [p for p in paths if p.is_file()]) for code, label, paths in CHAPTERS]
    docs = [p for _, _, group in active for p in group]
    task_path = ROOT / "data" / "tasks.json"
    tasks = json.loads(task_path.read_text("utf-8"))
    if len(tasks) != 100 or len({t["id"] for t in tasks}) != 100:
        raise ValueError("100 unique tasks required")
    for row in tasks:
        if not all(row.get(key) for key in ("id","stage","title","do","done","stuck")):
            raise ValueError("Incomplete task data: " + str(row.get("id")))
    fingerprint = content_checksum(docs, task_path)
    if PDF.exists() and EDITION.exists():
        try:
            if json.loads(EDITION.read_text("utf-8")).get("source_sha256") == fingerprint:
                print("PDF is current:",PDF)
                return
        except (OSError, ValueError):
            pass
    cover = '''<section class="cover"><div class="kicker">AI CHIEF ANDY  /  XINGJUE KNOWLEDGE SERIES  2026</div>
<h1>社招拿 Offer<br><em>实战工作手册</em></h1>
<p class="sub">从职业定位到简历、投递、面试、谈薪和入职。把每一步变成可验证的行动，不靠“保 Offer”承诺。</p>
<div class="sep"></div><div class="metrics"><div><b>06</b><small>求职关键阶段</small></div>
<div><b>100</b><small>行动任务</small></div><div><b>30</b><small>天实操路线</small></div></div>
<p class="bottom">AI 酋长 Andy / 星觉科技<br>微信 AIPMAndy<br>metaver.vip · www.a6no1.cn<br>免费开源 · 完整原始来源</p></section>'''
    toc=[]
    for code,label,group in active:
        toc.append(f'<div class="toc-group"><h3>{e(code)} / {e(label)}</h3>')
        for path in group:
            anchor = "chapter-" + re.sub(r"[^a-z0-9]", "-", path.relative_to(ROOT).as_posix().lower())
            toc.append(f'<div class="toc-row"><a href="#{anchor}">{e(page_title(path))}</a></div>')
        toc.append('</div>')
    intro = '''<section class="intro"><div class="kicker">HOW TO USE THIS BOOK</div><h2>先做一件事，拿到一个证据。</h2>
<div class="notice"><b>第一步：</b>从六个求职阶段里找出当前最迫切的问题。<br>
<b>第二步：</b>跟着章节完成一份可查证的具体材料。<br>
<b>第三步：</b>用求职漏斗复盘下一步，而不是重复无效海投。</div>
<p>本电子书从开源仓库中的 Markdown 及 100 项任务数据生成。没有可公开核验的真实客户案例时，示例属于教学模拟，不代表某人拿到真实 Offer。</p>
<p>本 PDF 用于完整阅读，打卡、求职漏斗与薪资比较工具请使用
<a href="https://aipmandy.github.io/how-to-get-offer/">在线互动网站</a>。免费阅读，无需先添加微信。</p>
<p>招聘规则、法律和社保等可能随时间变化，具体权益以当期法规和相关官方信息为准。</p>
<h2>完整目录</h2><div class="toc">''' + ''.join(toc) + '''<div class="toc-group"><h3>06 / 附录</h3>
<div class="toc-row"><a href="#task-index">100 项行动任务</a></div>
<div class="toc-row"><a href="#author-contact">联系与咨询</a></div></div></div></section>'''
    chapters=[]
    for code,label,group in active:
        chapters.append(f'<section class="part"><div class="kicker">PART {e(code)}</div><h2>{e(label)}</h2><p>循序执行，不代替必要的独立调查与个人判断。</p></section>')
        for i,path in enumerate(group,1):
            relative=path.relative_to(ROOT).as_posix()
            anchor="chapter-"+re.sub(r"[^a-z0-9]","-",relative.lower())
            raw=rewrite_links(path.read_text("utf-8"),path)
            raw=re.sub(r"^#\s+[^\n]+\n?","",raw,count=1)
            body=markdown.markdown(raw, extensions=("tables","fenced_code","sane_lists"))
            chapters.append(f'''<section class="chapter" id="{anchor}">
<header class="chapter-head"><div class="kicker">{e(code)}.{i:02d}  /  SOURCE-BASED LESSON</div>
<h2>{e(page_title(path))}</h2><p>原始文件：{e(relative)} ·
<a href="{LINK_ROOT}{e(relative)}">查看最新原文 ↗</a></p></header>
<div class="chapter-body">{body}</div></section>''')
    cards=['''<section id="task-index" class="task-intro"><div class="kicker">PART 06 / ACTION CHECKLIST</div>
<h2>100 项任务 · 逐项验收</h2><p>所有任务来自项目 data/tasks.json：明确动作、完成凭证与卡住时的替代路径。</p></section>''']
    prev=None
    for i,row in enumerate(tasks,1):
        if row["stage"]!=prev:
            if prev is not None:cards.append("</div>")
            prev=row["stage"];cards.append(f'<div class="task-group"><h3>{e(prev)}阶段</h3>')
        cards.append(f'''<div class="task"><div class="number">TASK {i:03d} / {e(row["id"])}</div><b>{e(row["title"])}</b>
<p>执行动作：{e(row["do"])}</p><p class="small">完成证据：{e(row["done"])}</p>
<p class="small">卡住怎么办：{e(row["stuck"])}</p></div>''')
    cards.append("</div>")
    contact='''<section class="contact" id="author-contact"><div class="kicker">AI CHIEF ANDY / XINGJUE TECHNOLOGY</div>
<h2>求职靠证据。<br>专业成长靠复盘。</h2>
<p>开源知识永久免费。如果希望针对岗位定位、项目经历、简历或模拟面试得到进一步支持，可以联系作者沟通具体问题。</p>
<ul><li>个人微信：<b>AIPMAndy</b></li><li>个人官网：
<a href="https://metaver.vip/">https://metaver.vip/</a></li>
<li>星觉科技公司官网：<a href="https://www.a6no1.cn/">https://www.a6no1.cn/</a></li>
<li>咨询服务：<a href="https://metaver.vip/services">https://metaver.vip/services</a></li>
<li>GitHub 源码：<a href="https://github.com/AIPMAndy/how-to-get-offer">AIPMAndy/how-to-get-offer</a></li></ul>
<p class="legal">本资料不保证录用、涨薪、签证或内推结果。个人咨询自愿选择，不影响免费阅读。请勿在公开仓库或评论区发送含身份证、家庭住址、联系方式的完整简历。</p></section>'''
    document='<html lang="zh-CN"><head><meta charset="utf-8"><title>社招拿 Offer 实战手册</title><style>'+STYLE+'</style></head><body>'+cover+intro+''.join(chapters)+''.join(cards)+contact+'</body></html>'
    PDF.parent.mkdir(parents=True,exist_ok=True)
    HTML(string=document,base_url=str(ROOT)).write_pdf(PDF)
    if not PDF.exists() or PDF.stat().st_size<40000 or PDF.read_bytes()[:4]!=b"%PDF":
        raise RuntimeError("Invalid PDF publication artifact")
    EDITION.write_text(json.dumps({"source_sha256":fingerprint,"chapters":len(docs),"tasks":len(tasks),"publication":"2026-11-14"},ensure_ascii=False,indent=2)+"\n","utf-8")
    print("Published PDF", PDF.stat().st_size, "bytes; chapters:", len(docs), "tasks:", len(tasks))

if __name__=="__main__":
    build()
