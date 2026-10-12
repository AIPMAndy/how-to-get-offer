'use strict';
// All personal fields remain local; this static website never calls fetch or external APIs.
(function(){
 const $=(id)=>document.getElementById(id);
 const STAGES=['定位','简历','渠道','面试','Offer','入职'];
 const STATUS=['已投递','已回复','已约面','面试中','Offer','已结束'];
 const K='how-to-get-offer.v1';
 const defaultData=()=>({version:1,done:[],jobs:[]});
 function safeLoad(){try{const raw=JSON.parse(localStorage.getItem(K)||'null');return validate(raw)||defaultData();}catch{return defaultData();}}
 function validate(v){if(!v||v.version!==1||!Array.isArray(v.done)||!Array.isArray(v.jobs)||v.jobs.length>5000||v.done.length>1000)return null;
  if(!v.done.every(x=>typeof x==='string'&&/^[A-Z0-9-]{1,14}$/.test(x)))return null;
  if(!v.jobs.every(x=>x&&typeof x.id==='string'&&typeof x.company==='string'&&x.company.length<=80&&typeof x.role==='string'&&x.role.length<=80&&STATUS.includes(x.status)&&typeof x.date==='string'&&x.date.length<=30))return null;
  return {version:1,done:v.done.filter(id=>TASKS.some(t=>t.id===id)),jobs:v.jobs.map(j=>({id:j.id.slice(0,90),company:j.company,role:j.role,status:j.status,date:j.date,maxRank:Number.isInteger(j.maxRank)&&j.maxRank>=0&&j.maxRank<=4?j.maxRank:Math.max(0,Math.min(4,STATUS.indexOf(j.status)))}))};}
 let store=safeLoad();
 let canSave=true;
 function save(){try{localStorage.setItem(K,JSON.stringify(store));}catch{canSave=false;$('storageWarning').classList.remove('hidden');}}
 function el(tag,cls,txt){const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n;}
 function updateProgress(){const count=store.done.length;const pct=Math.round(count/TASKS.length*100);$('progressNum').textContent=count+' / '+TASKS.length;$('progressPct').textContent=pct+'%';$('progressFill').style.width=pct+'%';const box=$('stageProgress');box.replaceChildren();STAGES.forEach(stage=>{const all=TASKS.filter(t=>t.stage===stage), done=all.filter(t=>store.done.includes(t.id)).length;const tile=el('div','stage-tile');tile.append(el('b','',stage),el('small','',done+'/'+all.length+' 完成'));box.append(tile);});}
 function renderTasks(){const q=$('taskSearch').value.trim().toLowerCase();const s=$('stageFilter').value;const matches=TASKS.filter(t=>(s==='全部'||t.stage===s)&&(!q||[t.title,t.do,t.done,t.stuck,t.stage,t.id].join(' ').toLowerCase().includes(q)));$('taskCount').textContent=`显示 ${matches.length} 项 · 总计 ${TASKS.length} 项`;
 const box=$('taskList');box.replaceChildren();matches.forEach(task=>{const done=store.done.includes(task.id);const art=el('article','task'+(done?' is-done':''));const line=el('div','task-line');const input=el('input');input.type='checkbox';input.checked=done;input.id='check-'+task.id;input.setAttribute('aria-label','完成'+task.title);input.addEventListener('change',()=>{store.done=input.checked?[...new Set([...store.done,task.id])]:store.done.filter(i=>i!==task.id);save();updateProgress();renderTasks();});const block=el('div');block.style.flex='1';block.append(el('span','task-id',task.id+' · '+task.stage));const label=el('label','',task.title);label.htmlFor=input.id;block.append(label);line.append(input,block);const details=el('details');const sum=el('summary','', '查看步骤 / 完成标准 / 卡住怎么办');details.append(sum);[['执行','do'],['完成凭证','done'],['受阻处理','stuck']].forEach(([title,k])=>{const p=el('p');p.append(el('strong','',title+'：'),document.createTextNode(task[k]));details.append(p);});art.append(line,details);box.append(art);});}
 function renderJobs(){
 const box=$('jobRows');box.replaceChildren();for(const j of store.jobs){const tr=el('tr');tr.append(el('td','',j.company),el('td','',j.role));
 const statusCell=el('td'),sel=el('select');sel.setAttribute('aria-label','更新 '+j.company+' 的状态');sel.style.maxWidth='125px';STATUS.forEach(st=>{const op=el('option','',st);op.value=st;op.selected=(st===j.status);sel.append(op);});
 sel.addEventListener('change',()=>{j.status=sel.value;if(j.status!=='已结束')j.maxRank=Math.max(j.maxRank,STATUS.indexOf(j.status));save();renderJobs();});statusCell.append(sel);tr.append(statusCell);
 tr.append(el('td','',j.date));const d=el('td');const btn=el('button','rm','删除');btn.type='button';btn.setAttribute('aria-label','删除记录 '+j.company+' '+j.role);btn.addEventListener('click',()=>{if(confirm('删除这条岗位记录？')){store.jobs=store.jobs.filter(x=>x.id!==j.id);save();renderJobs();}});d.append(btn);tr.append(d);box.append(tr);}
 if(!store.jobs.length){const tr=el('tr');const td=el('td','','尚未添加岗位。上方录入一条即可开始。');td.colSpan=5;tr.append(td);box.append(tr);}
 const n=store.jobs.length,active=store.jobs.filter(x=>x.status!=='已结束').length;
 const reached=(i)=>store.jobs.filter(x=>x.maxRank>=i).length;
 $('jobsAll').textContent=n;$('jobsActive').textContent=active;$('jobsInterview').textContent=reached(2);$('jobsOffer').textContent=reached(4);
 const b=$('funnelBars');b.replaceChildren();[['已投递',n],['曾收到有效回复',reached(1)],['曾约面',reached(2)],['曾实际面试',reached(3)],['曾到Offer阶段',reached(4)]].forEach(([title,count])=>{const item=el('div','bar-item'),head=el('div','bar-head');head.append(el('span','',title),el('b','',`${count} / ${n||0}`));const bg=el('div','bar-bg'),fg=el('div','bar-fg');fg.style.width=(n?Math.round(count/n*100):0)+'%';bg.append(fg);item.append(head,bg);b.append(item);});}
 $('taskSearch').addEventListener('input',renderTasks);
 $('stageFilter').addEventListener('change',renderTasks);
 $('jobForm').addEventListener('submit',(e)=>{e.preventDefault();const company=$('jobCompany').value.trim(),role=$('jobRole').value.trim();if(!company||!role)return;if(store.jobs.length>=5000){alert('最多保存5000条，请导出备份后删除旧数据。');return;}const job={id:String(Date.now())+'-'+Math.random().toString(36).slice(2,9),company:company.slice(0,80),role:role.slice(0,80),status:$('jobStatus').value,date:new Date().toLocaleDateString('zh-CN'),maxRank:STATUS.indexOf($('jobStatus').value)};store.jobs.unshift(job);save();renderJobs();$('jobForm').reset();});
 function download(name,mime,body){const a=document.createElement('a');const url=URL.createObjectURL(new Blob([body],{type:mime}));a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
 $('backup').addEventListener('click',()=>download('offer-guide-backup.json','application/json;charset=utf-8',JSON.stringify({...store,exportedAt:new Date().toISOString()},null,2)));
 $('restore').addEventListener('change',async(e)=>{const file=e.target.files?.[0];if(!file)return;if(file.size>2000000){alert('文件超过2MB，不予导入。');e.target.value='';return;}try{const d=validate(JSON.parse(await file.text()));if(!d)throw Error('格式不正确');if(confirm('导入将覆盖当前任务与岗位记录，确认继续？')){store=d;save();updateProgress();renderTasks();renderJobs();alert('已导入到当前浏览器。');}}catch(err){alert('无法导入：'+err.message);}e.target.value='';});
 function csvEsc(s){let x=String(s??'');if(/^[\s]*[=+@\-]/.test(x))x="'"+x;return '"'+x.replace(/"/g,'""')+'"';}
 $('csvExport').addEventListener('click',()=>{const rows=[['公司','岗位','当前状态','曾达到最高阶段','录入日期'],...store.jobs.map(j=>[j.company,j.role,j.status,STATUS[j.maxRank]||'已投递',j.date])];download('job-pipeline.csv','text/csv;charset=utf-8','\ufeff'+rows.map(r=>r.map(csvEsc).join(',')).join('\r\n'));});
 $('clearTasks').addEventListener('click',()=>{if(confirm('确认清空全部任务勾选？岗位记录不会删除。')){store.done=[];save();renderTasks();updateProgress();}});
 // Annual confirmed cash = monthly base * number of confirmed payments + guaranteed allowance - annual incremental cost.
 const num=(id)=>{const n=Number($(id).value);return Number.isFinite(n)&&n>=0?n:0;};
 function money(n){return n.toLocaleString('zh-CN',{minimumFractionDigits:0,maximumFractionDigits:0})+' 元';}
 function salary(){const data=['a','b'].map(x=>{const base=num(x+'Base'),months=num(x+'Months'),stipend=num(x+'Stipend'),target=num(x+'Target'),cost=num(x+'Cost');return {fixed:base*months+stipend,net:base*months+stipend-cost,variable:target};});const d=$('salaryResults');d.replaceChildren();data.forEach((x,i)=>{const row=el('div','salary-row'),left=el('div'),v=el('div','val',money(x.net));left.append(el('b','',i?'Offer B':'Offer A'),el('div','fine','年度固定现金 '+money(x.fixed)+' − 额外年成本；目标奖金 '+money(x.variable)+'（不计入确定收入）'));row.append(left,v);d.append(row);});const diff=data[1].net-data[0].net;const tip=el('p','fine','B − A 的年度固定现金差：'+(diff>0?'+':'')+money(diff)+'。这是税前粗算，仅比较已确认固定现金与新增成本，未计算个税、社保及其他利益。');d.append(tip);}
 ['aBase','aMonths','aStipend','aTarget','aCost','bBase','bMonths','bStipend','bTarget','bCost'].forEach(id=>$(id).addEventListener('input',salary));
 updateProgress();renderTasks();renderJobs();salary();save();
 if(!canSave){$('storageWarning').classList.remove('hidden');}
})();
