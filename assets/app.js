'use strict';
// All personal fields remain local; this static website never calls fetch or external APIs.
(function(){
 const $=(id)=>document.getElementById(id);
 const STAGES=['定位','简历','渠道','面试','Offer','入职'];
 const STATUS=['已投递','已回复','已约面','面试中','Offer','已结束'];
 const K='how-to-get-offer.v1';
 const defaultData=()=>({version:1,done:[],jobs:[]});
 let originalRecovery=null,readFailed=false;
 function safeLoad(){
   try{
     const raw=localStorage.getItem(K);
     if(raw===null)return defaultData();
     try{const clean=validate(JSON.parse(raw));if(clean)return clean;}catch{}
     originalRecovery=raw;return defaultData();
   }catch{readFailed=true;return defaultData();}
 }
 function validate(v){if(!v||v.version!==1||!Array.isArray(v.done)||!Array.isArray(v.jobs)||v.jobs.length>5000||v.done.length>1000)return null;
  if(!v.done.every(x=>typeof x==='string'&&/^[A-Z0-9-]{1,14}$/.test(x)))return null;
  if(!v.jobs.every(x=>x&&typeof x.id==='string'&&x.id.length>0&&x.id.length<=90&&typeof x.company==='string'&&x.company.length<=80&&typeof x.role==='string'&&x.role.length<=80&&STATUS.includes(x.status)&&typeof x.date==='string'&&x.date.length<=30))return null;
  if(new Set(v.jobs.map(j=>j.id)).size!==v.jobs.length)return null;
  return {version:1,done:[...new Set(v.done.filter(id=>TASKS.some(t=>t.id===id)))],jobs:v.jobs.map(j=>({id:j.id.slice(0,90),company:j.company,role:j.role,status:j.status,date:j.date,maxRank:Number.isInteger(j.maxRank)&&j.maxRank>=0&&j.maxRank<=4?j.maxRank:(j.status==='已结束'?0:STATUS.indexOf(j.status))}))};}
 let store=safeLoad();
 let canSave=!readFailed&&originalRecovery===null;
 const openedTasks=new Set();
 function storageFeedback(){
   const recovering=originalRecovery!==null;
   $('storageWarning').classList.toggle('hidden',canSave&&!recovering);
   $('storageMessage').textContent=recovering?'旧记录格式异常，原始数据仍在本机，当前编辑不会覆盖它。请先下载原始记录；确认替换后才会写入当前内容。':'当前浏览器无法读取或保存本机数据。请导出进度 JSON 手动备份。';
   $('recoveryActions').classList.toggle('hidden',!recovering);
 }
 function save(replaceRecovery=false){
   if(originalRecovery!==null&&!replaceRecovery){canSave=false;storageFeedback();return false;}
   try{localStorage.setItem(K,JSON.stringify(store));originalRecovery=null;readFailed=false;canSave=true;storageFeedback();return true;}
   catch{canSave=false;storageFeedback();return false;}
 }
 function el(tag,cls,txt){const n=document.createElement(tag);if(cls)n.className=cls;if(txt!==undefined)n.textContent=txt;return n;}
 function updateProgress(){const count=store.done.length;const pct=Math.round(count/TASKS.length*100);$('progressNum').textContent=count+' / '+TASKS.length;$('progressPct').textContent=pct+'%';$('progressFill').style.transform='scaleX('+pct/100+')';$('progressMeter').setAttribute('aria-valuenow',String(pct));const box=$('stageProgress');box.replaceChildren();STAGES.forEach(stage=>{const all=TASKS.filter(t=>t.stage===stage), done=all.filter(t=>store.done.includes(t.id)).length;const tile=el('div','stage-tile');tile.append(el('b','',stage),el('small','',done+'/'+all.length+' 完成'));box.append(tile);});}
 function visibleTasks(){const q=$('taskSearch').value.trim().toLowerCase();const s=$('stageFilter').value;const pending=$('pendingOnly').checked;
  return TASKS.filter(t=>(s==='全部'||t.stage===s)&&(!pending||!store.done.includes(t.id))&&(!q||[t.title,t.do,t.done,t.stuck,t.stage,t.id].join(' ').toLowerCase().includes(q)));}
 function renderTasks(){const matches=visibleTasks();$('taskCount').textContent=`显示 ${matches.length} 项 · 总计 ${TASKS.length} 项`;$('taskEmpty').classList.toggle('hidden',matches.length!==0);
 const box=$('taskList');for(const article of box.querySelectorAll('.task[data-task-id]')){if(article.querySelector('details').open)openedTasks.add(article.dataset.taskId);else openedTasks.delete(article.dataset.taskId);}box.replaceChildren();matches.forEach(task=>{const done=store.done.includes(task.id);const art=el('article','task'+(done?' is-done':''));art.dataset.taskId=task.id;const line=el('div','task-line');const input=el('input');input.type='checkbox';input.checked=done;input.id='check-'+task.id;input.setAttribute('aria-label','完成'+task.title);input.addEventListener('change',()=>{store.done=input.checked?[...new Set([...store.done,task.id])]:store.done.filter(i=>i!==task.id);save();updateProgress();if($('pendingOnly').checked&&input.checked){renderTasks();($('taskList').querySelector('input[type=checkbox]')||$('pendingOnly')).focus({preventScroll:true});}else art.classList.toggle('is-done',input.checked);});const block=el('div');block.style.flex='1';block.append(el('span','task-id',task.id+' · '+task.stage));const label=el('label','',task.title);label.htmlFor=input.id;block.append(label);line.append(input,block);const details=el('details');details.open=openedTasks.has(task.id);const sum=el('summary','', '查看步骤 / 完成标准 / 卡住怎么办');details.append(sum);[['执行','do'],['完成凭证','done'],['受阻处理','stuck']].forEach(([title,k])=>{const p=el('p');p.append(el('strong','',title+'：'),document.createTextNode(task[k]));details.append(p);});art.append(line,details);box.append(art);});}
 function renderJobs(){
 const box=$('jobRows');box.replaceChildren();for(const j of store.jobs){const tr=el('tr');tr.append(el('td','',j.company),el('td','',j.role));
 const statusCell=el('td'),sel=el('select');sel.setAttribute('aria-label','更新 '+j.company+' 的状态');sel.style.maxWidth='125px';STATUS.forEach(st=>{const op=el('option','',st);op.value=st;op.selected=(st===j.status);sel.append(op);});
 sel.addEventListener('change',()=>{j.status=sel.value;if(j.status!=='已结束')j.maxRank=Math.max(j.maxRank,STATUS.indexOf(j.status));save();updateFunnel();});statusCell.append(sel);tr.append(statusCell);
 tr.append(el('td','',j.date));const d=el('td');const btn=el('button','rm','删除');btn.type='button';btn.setAttribute('aria-label','删除记录 '+j.company+' '+j.role);btn.addEventListener('click',()=>{if(confirm('删除这条岗位记录？')){store.jobs=store.jobs.filter(x=>x.id!==j.id);save();renderJobs();}});d.append(btn);tr.append(d);box.append(tr);}
 if(!store.jobs.length){const tr=el('tr');const td=el('td','','尚未添加岗位。上方录入一条即可开始。');td.colSpan=5;tr.append(td);box.append(tr);}
 updateFunnel();}
 function updateFunnel(){
 const n=store.jobs.length,active=store.jobs.filter(x=>x.status!=='已结束').length;
 const reached=(i)=>store.jobs.filter(x=>x.maxRank>=i).length;
 $('jobsAll').textContent=n;$('jobsActive').textContent=active;$('jobsInterview').textContent=reached(2);$('jobsOffer').textContent=reached(4);
 const b=$('funnelBars');b.replaceChildren();[['已投递',n],['曾收到有效回复',reached(1)],['曾约面',reached(2)],['曾实际面试',reached(3)],['曾到Offer阶段',reached(4)]].forEach(([title,count])=>{const item=el('div','bar-item'),head=el('div','bar-head');head.append(el('span','',title),el('b','',`${count} / ${n||0}`));const bg=el('div','bar-bg'),fg=el('div','bar-fg');fg.style.width=(n?Math.round(count/n*100):0)+'%';bg.append(fg);item.append(head,bg);b.append(item);});}
 $('taskSearch').addEventListener('input',renderTasks);
 $('stageFilter').addEventListener('change',renderTasks);
 $('pendingOnly').addEventListener('change',renderTasks);
 $('resetTaskFilters').addEventListener('click',()=>{$('taskSearch').value='';$('stageFilter').value='全部';$('pendingOnly').checked=false;renderTasks();$('taskSearch').focus();});
 $('jobForm').addEventListener('submit',(e)=>{e.preventDefault();const company=$('jobCompany').value.trim(),role=$('jobRole').value.trim();if(!company||!role)return;if(store.jobs.length>=5000){alert('最多保存5000条，请导出备份后删除旧数据。');return;}const job={id:String(Date.now())+'-'+Math.random().toString(36).slice(2,9),company:company.slice(0,80),role:role.slice(0,80),status:$('jobStatus').value,date:new Date().toLocaleDateString('zh-CN'),maxRank:$('jobStatus').value==='已结束'?0:STATUS.indexOf($('jobStatus').value)};store.jobs.unshift(job);save();renderJobs();$('jobForm').reset();$('jobCompany').focus({preventScroll:true});});
 function download(name,mime,body){const a=document.createElement('a');const url=URL.createObjectURL(new Blob([body],{type:mime}));a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),2000);}
 $('taskTxtExport').addEventListener('click',()=>{const visible=visibleTasks();const lines=['社招拿 Offer · 当前任务清单','作者：AI 酋长 Andy / 星觉科技','微信：AIPMAndy','个人官网：https://metaver.vip/','公司官网：https://www.a6no1.cn/','说明：仅导出当前筛选的公开任务内容，不包含个人岗位记录或薪酬输入。',`当前筛选共 ${visible.length} 项`,''];visible.forEach(t=>{lines.push(`[${store.done.includes(t.id)?'已完成':'未完成'}] ${t.id} · ${t.stage} · ${t.title}`,'执行：'+t.do,'凭证：'+t.done,'受阻：'+t.stuck,'');});download('offer-current-tasks.txt','text/plain;charset=utf-8','\ufeff'+lines.join('\r\n'));});
 $('downloadRecovery').addEventListener('click',()=>{if(originalRecovery!==null)download('offer-original-recovery.json','application/json;charset=utf-8',originalRecovery);});
 $('replaceRecovery').addEventListener('click',()=>{if(originalRecovery!==null&&confirm('这将用当前页面内容替换旧的异常记录。请先下载原始记录。确认替换？'))save(true);});
 $('backup').addEventListener('click',()=>download('offer-guide-backup.json','application/json;charset=utf-8',JSON.stringify({...store,exportedAt:new Date().toISOString()},null,2)));
 $('restore').addEventListener('change',async(e)=>{const file=e.target.files?.[0];if(!file)return;if(file.size>2000000){alert('文件超过2MB，不予导入。');e.target.value='';return;}try{const d=validate(JSON.parse(await file.text()));if(!d)throw Error('格式不正确');if(confirm('导入将覆盖当前任务与岗位记录，确认继续？')){store=d;const persisted=save(true);updateProgress();renderTasks();renderJobs();alert(persisted?'已导入到当前浏览器。':'已导入当前页面，但未保存成功，请备份。');}}catch(err){alert('无法导入：'+err.message);}e.target.value='';});
 function csvEsc(s){let x=String(s??'');if(/^[\s]*[=+@\-]/.test(x))x="'"+x;return '"'+x.replace(/"/g,'""')+'"';}
 $('csvExport').addEventListener('click',()=>{const rows=[['公司','岗位','当前状态','曾达到最高阶段','录入日期'],...store.jobs.map(j=>[j.company,j.role,j.status,STATUS[j.maxRank]||'已投递',j.date])];download('job-pipeline.csv','text/csv;charset=utf-8','\ufeff'+rows.map(r=>r.map(csvEsc).join(',')).join('\r\n'));});
 $('clearTasks').addEventListener('click',()=>{if(confirm('确认清空全部任务勾选？岗位记录不会删除。')){store.done=[];save();renderTasks();updateProgress();}});
 // A blank or invalid field is unknown, not zero. An ended application does not imply an Offer.
 const salaryIds=['aBase','aMonths','aStipend','aTarget','aCost','bBase','bMonths','bStipend','bTarget','bCost'];
 const values=()=>salaryIds.map(id=>$(id).value);
 let demoMode=false,salaryUndo=null;
 function amount(id,months=false,optional=false){
   const input=$(id),raw=input.value.trim();
   if(optional&&!raw&&!input.validity.badInput){input.removeAttribute('aria-invalid');return null;}
   const syntax=months?/^\d+(?:\.5|\.0)?$/:/^\d+(?:\.\d{1,2})?$/;
   const n=Number(raw);
   const ok=!!raw&&syntax.test(raw)&&Number.isFinite(n)&&(months?n>0&&n<=36:n>=0&&n<=1000000000)&&!input.validity.badInput;
   if(raw||input.validity.badInput)input.setAttribute('aria-invalid',String(!ok));else input.removeAttribute('aria-invalid');
   return ok?n:NaN;
 }
 function money(n){return n.toLocaleString('zh-CN',{maximumFractionDigits:2})+' 元';}
 function salary(){
   const any=salaryIds.some(id=>$(id).value.trim()||$(id).validity.badInput);
   $('salaryDemo').disabled=any;$('salaryClear').disabled=!any;
   $('salaryUndo').classList.toggle('hidden',salaryUndo===null);
   $('salaryMode').textContent=demoMode?'当前来自虚构教学示例（含可能修改的示例值）。清空后再录入真实数据。':'真实录入：未知留空，确认没有费用或补贴才填 0。目标奖金可不填。';
   const data=['a','b'].map(x=>{
     const base=amount(x+'Base'),months=amount(x+'Months',true),stipend=amount(x+'Stipend'),target=amount(x+'Target',false,true),cost=amount(x+'Cost');
     const valid=[base,months,stipend,cost].every(Number.isFinite)&&(target===null||Number.isFinite(target));
     return valid?{fixed:base*months+stipend,net:base*months+stipend-cost,variable:target}:null;
   });
   const d=$('salaryResults');d.replaceChildren();
   data.forEach((x,i)=>{
     const row=el('div','salary-row'),left=el('div');
     left.append(el('b','',i?'Offer B':'Offer A'));
     if(!x){left.append(el('div','fine','等待完整有效的确认金额。月数 0.5–36，按半月录入；金额最多两位小数。'));row.append(left,el('div','val','—'));}
     else{left.append(el('div','fine','年度固定现金 '+money(x.fixed)+' − 额外年成本；目标奖金 '+(x.variable===null?'未填写':money(x.variable))+'（不计入确定收入）'));row.append(left,el('div','val',money(x.net)));}
     d.append(row);
   });
   if(data.every(Boolean)){const diff=data[1].net-data[0].net;d.append(el('p','fine','B − A 的年度固定现金差：'+(diff>0?'+':'')+money(diff)+'。税前粗算，未计算个税、社保及其他利益。'));}
   else d.append(el('p','fine','两份 Offer 均填完整后，才显示年度固定现金差。'));
 }
 salaryIds.forEach(id=>$(id).addEventListener('input',()=>{salaryUndo=null;salary();}));
 $('salaryDemo').addEventListener('click',()=>{if(salaryIds.some(id=>$(id).value.trim()||$(id).validity.badInput))return;const sample=['20000','12','0','0','0','22000','13','0','10000','12000'];salaryIds.forEach((id,i)=>$(id).value=sample[i]);demoMode=true;salaryUndo=null;salary();});
 $('salaryClear').addEventListener('click',()=>{if(!confirm('清空当前薪酬输入？可立即撤销。'))return;salaryUndo={values:values(),demoMode};salaryIds.forEach(id=>$(id).value='');demoMode=false;salary();$('salaryUndo').focus({preventScroll:true});});
 $('salaryUndo').addEventListener('click',()=>{if(!salaryUndo)return;salaryIds.forEach((id,i)=>$(id).value=salaryUndo.values[i]);demoMode=salaryUndo.demoMode;salaryUndo=null;salary();$('salaryClear').focus({preventScroll:true});});
 // Explicit opt-in copy: no collection, transmission, or analytics.
 const copyBtn=$('copyWechat');
 if(copyBtn)copyBtn.addEventListener('click',async()=>{
   try{if(!navigator.clipboard||!window.isSecureContext)throw Error('clipboard');
     await navigator.clipboard.writeText('AIPMAndy');copyBtn.textContent='已复制 AIPMAndy';}
   catch{copyBtn.textContent='请手动复制 AIPMAndy';}
 });
 updateProgress();renderTasks();renderJobs();salary();storageFeedback();
})();
