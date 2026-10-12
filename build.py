#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate self-contained GitHub Pages/offline website. No external dependencies."""
from pathlib import Path
import json
import html

BASE=Path(__file__).resolve().parent

def build():
    data=json.loads((BASE/'data/tasks.json').read_text('utf-8'))
    assert len({x['id'] for x in data})==len(data)
    assert len(data)>=50
    for x in data:
        assert all(x.get(k) for k in ('id','stage','title','do','done','stuck'))
    js_tasks=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    css=(BASE/'assets/app.css').read_text('utf-8')
    js=(BASE/'assets/app.js').read_text('utf-8')
    html_doc='''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta name="theme-color" content="#f6f8fc"><meta name="description" content="社招拿Offer保姆级指南｜定位、简历、投递内推、面试、谈薪、入职；免费开源，100项可执行任务，离线可用。"><title>社招拿 Offer 保姆级指南｜AI 酋长 Andy</title><style>''' + css.replace('</style','<\\/style') + '''</style></head><body>
<nav class="nav"><div class="wrap nav-inner"><a href="#top" class="logo">Offer<span>Guide.</span></a><div class="nav-links"><a href="#plan">路线图</a><a href="#tasks">任务卡</a><a href="#pipeline">求职漏斗</a><a href="#salary">薪酬比较</a><a href="#library">资料库</a><a href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">个人官网 ↗</a></div></div></nav>
<header id="top" class="hero"><div class="wrap hero-inner"><div><div class="eyebrow">FREE · OPEN SOURCE · OFFLINE FIRST</div><h1>社招拿 Offer<br><em>保姆级指南</em></h1><p>从确定方向、改简历、精准投递、内推、面试，到谈薪与入职。把一次焦虑的求职拆成100件能做到、能复盘的事。</p><div class="hero-actions"><a class="btn" href="#tasks">开始执行 →</a><a class="btn ghost" href="#library">查看完整攻略</a></div><p class="hero-tip">✦ 纯本地运行 · 不需账户 · 不收集简历 · 不承诺“保 Offer”</p></div><div class="glass"><div class="metric-top"><div><div class="label">你的执行进度</div><strong id="progressNum">0 / 100</strong></div><div><span class="pill" id="progressPct">0%</span></div></div><div class="progress-track"><div id="progressFill"></div></div><div class="fine">每个任务都写清具体动作、完成凭证以及卡住怎么办。</div><div class="stage-dots" id="stageProgress"></div></div></div></header>
<main class="wrap"><section id="plan"><div class="section-head"><div class="pill">THE ROADMAP</div><h2>拿 Offer 的六个环节</h2><p>从最早的卡点开始，不必机械读完整本书。</p></div><div class="cards">
'''
    stages=[('01','定位','知道该投什么岗位，避免无差别求职','guides/01-positioning.md'),('02','简历','用真实的项目和成果证明岗位匹配','guides/02-resume.md'),('03','渠道','找到有效岗位，建立投递与内推系统','guides/03-channels.md'),('04','面试','经得起事实、决策和复盘的深挖','guides/04-interview.md'),('05','Offer','拆开收入结构，核验条件、合理谈薪','guides/05-offer.md'),('06','入职','合法交接，并把前90天目标对齐','guides/06-onboarding.md')]
    for number,title,desc,link in stages:
        html_doc+=f'<article class="card"><div class="n">STEP {number}</div><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p><a class="more" href="{link.removesuffix(".md")}.html">阅读完整步骤 ↗</a></article>'
    html_doc+='''</div></section>
<section id="tasks"><div class="section-head"><div class="pill">100 ACTIONS</div><h2>每一项，都有完成凭证</h2><p>勾选保存在你当前浏览器。下方可以导出备份；换设备不会自动同步。</p></div><div class="toolbox"><input aria-label="搜索任务" id="taskSearch" class="field search" placeholder="搜索任务 / 面试 / 简历 / 谈薪…"><select id="stageFilter" aria-label="按阶段筛选"><option>全部</option><option>定位</option><option>简历</option><option>渠道</option><option>面试</option><option>Offer</option><option>入职</option></select><span class="fine" id="taskCount"></span></div><div id="taskList" class="task-list"></div><div class="tool-actions"><button id="backup" class="btn small">导出全部进度 JSON ↓</button><label class="btn small ghost" for="restore" style="cursor:pointer">导入进度 JSON ↑</label><input type="file" id="restore" accept=".json,application/json" class="hidden"><button id="clearTasks" class="btn small ghost">清空勾选</button></div><div id="storageWarning" class="notice hidden" role="status">当前浏览器阻止了本地持久化，数据可能在关闭页面后丢失。请用「导出进度 JSON」手动备份。</div></section>
<section id="pipeline"><div class="section-head"><div class="pill">JOB PIPELINE</div><h2>求职漏斗：别再靠猜</h2><p>手动标记岗位当前阶段，系统保存你曾达到的最高阶段，粗略展示各环节推进情况。</p></div><div class="two"><div class="panel"><h3>录入目标岗位</h3><p class="sub">仅存本机。尽量使用公司简称或代号，不填个人隐私。</p><form id="jobForm" class="form-grid"><label>公司/代号<input class="field" id="jobCompany" required maxlength="80" placeholder="例：A公司"></label><label>岗位<input class="field" id="jobRole" required maxlength="80" placeholder="例：AI产品经理"></label><label class="wide">当前最高阶段<select id="jobStatus"><option>已投递</option><option>已回复</option><option>已约面</option><option>面试中</option><option>Offer</option><option>已结束</option></select></label><button type="submit" class="btn wide">新增岗位记录 +</button></form><p class="fine">新增后可直接在表格里调整状态。「已结束」保留此前到达的最高阶段；请及时记录实际进度。</p></div><div class="panel"><h3>现在的机会分布</h3><p class="sub">以你手动标记的「曾到达最高阶段」统计；它假定流程逐级推进，跳步会高估中间阶段，不能算真实转化率。</p><div class="stat-row"><div class="stat"><b id="jobsAll">0</b><small>累计录入</small></div><div class="stat"><b id="jobsActive">0</b><small>进行中</small></div><div class="stat"><b id="jobsInterview">0</b><small>推定曾约面</small></div><div class="stat"><b id="jobsOffer">0</b><small>标记到Offer阶段</small></div></div><div id="funnelBars" style="margin-top:23px"></div></div></div><div class="panel" style="margin-top:17px"><div style="display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap"><h3>机会清单</h3><button class="btn small ghost" id="csvExport">导出 CSV</button></div><div class="scroll-table"><table class="data-table"><thead><tr><th>公司</th><th>岗位</th><th>当前阶段</th><th>录入日期</th><th>操作</th></tr></thead><tbody id="jobRows"></tbody></table></div><p class="fine">每条记录独立保存在当前浏览器。CSV 导出会对电子表格公式前缀做安全转义；不要上传含隐私的备份到公开仓库。</p></div></section>
<section id="salary"><div class="section-head"><div class="pill">SALARY CHECK</div><h2>比较 Offer，先看确定性现金</h2><p>把月薪、固定发薪月数、固定补贴和额外年成本拆开；目标奖金单独显示。</p></div><div class="two">
'''
    for letter,heading in [('a','Offer A'),('b','Offer B')]:
        html_doc+=f'''<div class="panel"><h3>{heading}</h3><p class="sub">填确定金额，单位全部为人民币元。</p><div class="form-grid"><label>税前固定月薪<input class="field" type="number" min="0" step="100" id="{letter}Base" value="20000"></label><label>确定发薪月数<input class="field" type="number" min="0" step=".5" id="{letter}Months" value="12"></label><label>固定年度补贴<input class="field" type="number" min="0" step="100" id="{letter}Stipend" value="0"></label><label>目标奖金（浮动）<input class="field" type="number" min="0" step="100" id="{letter}Target" value="0"></label><label class="wide">相较当前生活的新增年度成本<input class="field" type="number" min="0" step="100" id="{letter}Cost" value="0"></label></div></div>'''
    html_doc+='''</div><div id="salaryResults" class="compare-output" aria-live="polite"></div><div class="notice">仅做简单的年度税前固定现金比较。输入未确认的「13薪/14薪」会抬高计算结果；请先核实支付条件。未计算税、社保公积金、签字费条款、期权价值、各项风险与成长空间。</div></section>
<section id="library"><div class="section-head"><div class="pill">FREE HANDBOOK</div><h2>模板和深度 SOP</h2><p>从简历到谈薪，提供可以复制的文档。所有指南都有独立离线 HTML 阅读页，点击即可阅读。</p></div><div class="resources">
'''
    links=[('3分钟分流','guides/00-start-here.md','先找卡点'),('30天执行表','guides/30-day-plan.md','逐日交付物'),('JD匹配矩阵','templates/jd-match.md','筛选目标岗位'),('真实项目素材库','templates/project-evidence.md','改简历的根'),('求职简历骨架','templates/resume-outline.md','定制PDF'),('HR/内推私信','templates/referral-messages.md','减少无效打扰'),('完整面试复盘','playbooks/02-interview-review.md','找到真缺口'),('谈薪完整对话','playbooks/03-salary-negotiation.md','有依据地报价'),('Offer 核查','templates/offer-checklist.md','别漏关键条款'),('AI 提示词库','templates/ai-prompts.md','安全使用AI'),('特殊处境求职','playbooks/04-special-situations.md','空窗/转行/35+'),('防招聘骗局','playbooks/06-job-scams.md','招转培/付费内推'),
    ('20份JD实操','guides/07-positioning-lab.md','逐条匹配真实岗位'),
    ('简历改写工作坊','guides/08-resume-workshop.md','前后对照'),
    ('投递内推作战表','guides/09-channel-operating-system.md','包含时间线'),
    ('面试40问','guides/10-interview-answer-bank.md','附追问方式'),
    ('多Offer决策','guides/11-offer-decision-lab.md','含辞职顺序'),
    ('六大岗位打法','guides/12-role-playbooks.md','产品/技术/运营等'),
    ('模拟候选人完整旅程','guides/13-real-world-journey.md','30天教学示例'),
    ('招聘经理视角','playbooks/07-recruiter-view.md','反向审核自己'),
    ('模拟面试实战','playbooks/08-interview-live.md','90秒介绍'),
    ('背调竞业SOP','playbooks/09-background-check.md','个人信息保护'),
    ('零回复排查','playbooks/10-zero-replies.md','避免盲目海投'),
    ('Offer撤回止损','playbooks/11-offer-withdrawn.md','合同与保留证据'),
    ('总监负责人路线','playbooks/12-executive-track.md','管理决策卡'),
    ('35+/转行/空窗','playbooks/13-career-gap-35.md','特殊情况'),
    ('市场薪资调查','playbooks/14-market-salary-research.md','真实薪资区间'),
    ('面试评分卡','templates/interview-scorecard.md','五维评审'),
    ('候选人一页纸','templates/candidate-one-pager.md','求职第一步'),
    ('企业尽职调查','templates/company-due-diligence.md','12项风险核验')]
    for title,url,tip in links:
        html_doc+=f'<a class="resource" href="{url.removesuffix(".md")}.html"><span>{html.escape(title)}<small>{html.escape(tip)}</small></span><span aria-hidden="true">↗</span></a>'
    html_doc+='''</div></section><div class="cta"><div><div class="pill" style="color:#aeb7ff">OPTIONAL · NOT REQUIRED</div><h2>需要人帮你审一次简历或模拟面试？</h2><p>AI 酋长 Andy · 微信 AIPMAndy · 备注「社招 Offer」并简单说明年限、目标岗位、卡点。咨询可选，所有开源内容免费。</p></div><a class="btn" href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">了解作者 ↗</a></div></main><footer class="wrap foot">© 2026 AI 酋长 Andy · 内容采用 CC BY 4.0，代码采用 MIT · <a href="https://github.com/AIPMAndy/how-to-get-offer" rel="noopener">GitHub</a> · <a href="PUBLISH.md">发布说明</a> · 所有用户数据默认仅存于本地浏览器。<br>微信 <strong>AIPMAndy</strong> · <a href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">个人官网</a> · 求职、职业发展与 AI 应用咨询可选，不影响免费使用。</footer>
<script>const TASKS = '''+js_tasks+''';</script><script>'''+js.replace('</script','<\\/script')+'''</script></body></html>'''
    (BASE/'index.html').write_text(html_doc,encoding='utf-8')
    build_readers()
    return len(data)



def inline(text):
    """Conservative safe subset of Markdown, sufficient for bundled docs."""
    import re
    text=html.escape(text,quote=True)
    def a(m):
        label=m.group(1)
        url=html.unescape(m.group(2))
        if url.lower().startswith(('javascript:', 'data:')): return label
        if url.endswith('.md'): url=url[:-3]+'.html'
        return f'<a href="{html.escape(url,quote=True)}">{label}</a>'
    text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',a,text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    return text

def md_to_html(md):
    import re
    lines=md.splitlines()
    out=[];i=0
    while i<len(lines):
        t=lines[i].strip()
        if not t: i+=1;continue
        if t.startswith('```'):
            buff=[]; i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                buff.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(buff))+'</code></pre>'); i+=1;continue
        if t.startswith('#') and re.match(r'^#{1,6} ',t):
            level=len(t)-len(t.lstrip('#'));out.append(f'<h{level}>{inline(t[level:].strip())}</h{level}>');i+=1;continue
        if t=='---':out.append('<hr>');i+=1;continue
        if t.startswith('|') and i+1<len(lines) and re.match(r'^\|?\s*:?-{3,}',lines[i+1].strip()):
            heads=[x.strip() for x in t.strip('|').split('|')]; i+=2
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                rows.append([x.strip() for x in lines[i].strip().strip('|').split('|')]);i+=1
            table='<div class="scroll"><table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in heads)+'</tr></thead><tbody>'
            for r in rows:table+='<tr>'+''.join('<td>'+inline(c)+'</td>' for c in r)+'</tr>'
            out.append(table+'</tbody></table></div>');continue
        if t.startswith('>'):
            quote=[]
            while i<len(lines) and lines[i].strip().startswith('>'):
                quote.append(lines[i].strip()[1:].strip());i+=1
            out.append('<blockquote>'+ '<p>'+inline(' '.join(quote))+'</p></blockquote>');continue
        if re.match(r'^([-*] |\d+\. )',t):
            ordered=bool(re.match(r'^\d+\. ',t));ls=[]
            while i<len(lines) and re.match(r'^([-*] |\d+\. )',lines[i].strip()):
                v=re.sub(r'^([-*] |\d+\. )','',lines[i].strip());ls.append('<li>'+inline(v)+'</li>');i+=1
            tag='ol' if ordered else 'ul';out.append(f'<{tag}>'+''.join(ls)+f'</{tag}>');continue
        buff=[t];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|[-*] |\d+\. |```)',lines[i].strip()):
            buff.append(lines[i].strip());i+=1
        out.append('<p>'+inline(' '.join(buff))+'</p>')
    return '\n'.join(out)

DOC_CSS='\n:root{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:#19243c;background:#f7f8fc}body{margin:0;padding:0 20px;line-height:1.85}.top{max-width:860px;margin:0 auto;padding:22px 0;font-size:14px;color:#5d66aa}.top a{color:#5550d6}.contact{max-width:860px;margin:0 auto 36px;font-size:12px;color:#69738a;overflow-wrap:anywhere}article{max-width:860px;margin:0 auto 60px;padding:34px 44px;border-radius:20px;background:white;border:1px solid #e8ecf3;box-shadow:0 8px 45px rgba(30,45,80,.06)}h1{line-height:1.25;font-size:35px;letter-spacing:-.8px;margin:15px 0 24px}h2{margin-top:36px;font-size:25px}h3{margin-top:27px}p,li{font-size:15px}li{margin-bottom:4px}a{color:#524ed7;text-decoration:none}a:hover{text-decoration:underline}code{font-family:ui-monospace,SFMono-Regular,monospace;color:#4d429a;background:#f2f1ff;padding:2px 5px;border-radius:4px}pre{background:#182034;color:#ecf1ff;padding:18px;border-radius:12px;overflow-x:auto;font-size:13px;line-height:1.6}pre code{color:inherit;background:none;padding:0;white-space:pre}blockquote{margin:20px 0;padding:10px 18px;border-left:3px solid #6359e9;background:#f7f6ff;color:#4a5272}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px;min-width:450px}th,td{border:1px solid #e5e9f0;padding:8px 10px;text-align:left}th{background:#f5f6fb}hr{border:0;border-top:1px solid #e7eaf1;margin:32px 0}@media(max-width:600px){body{padding:0 12px}article{padding:23px 18px}h1{font-size:29px}h2{font-size:22px}}\n'

def build_readers():
    """Generate offline friendly HTML sibling for every Markdown handbook page."""
    for root in ('guides','playbooks','templates','examples'):
        for p in (BASE/root).glob('*.md'):
            title=p.read_text('utf-8').splitlines()[0].lstrip('# ').strip()
            body=md_to_html(p.read_text('utf-8'))
            # relative links back to root on subfolder documents
            doc=f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>{html.escape(title)}｜社招拿Offer保姆级指南</title><style>{DOC_CSS}</style></head><body><nav class="top"><a href="../index.html">← 返回互动指南</a>　·　<a href="https://github.com/AIPMAndy/how-to-get-offer" target="_blank" rel="noopener noreferrer">GitHub项目</a>　·　<a href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">个人官网 ↗</a></nav><article>{body}</article><footer class="contact">AI 酋长 Andy · 微信 <strong>AIPMAndy</strong> · <a href="https://metaver.vip/" target="_blank" rel="noopener noreferrer">个人官网</a><br>求职、职业发展与 AI 应用咨询可选，不影响免费阅读。</footer></body></html>'
            p.with_suffix('.html').write_text(doc,encoding='utf-8')

if __name__=='__main__':
    print('generated index.html with',build(),'task cards')
