const html = `<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>训练日志与感悟</title><style>
body{font-family:"Microsoft YaHei",sans-serif;background:#1b1f24;color:#e8eaed;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#262b33;border-radius:12px;padding:32px 40px;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.4);max-width:640px}
h1{font-size:22px;margin:0 0 8px}p.desc{color:#9aa3af;font-size:13px;margin:0 0 20px;line-height:1.7}
label{display:block;margin:10px 0 4px;text-align:left;color:#cbd2da;font-size:13px}
input,select,textarea{width:100%;box-sizing:border-box;background:#11151a;border:1px solid #3a4149;color:#e8eaed;border-radius:6px;padding:8px;font-size:14px}
textarea{height:170px;resize:vertical;font-family:inherit}
button{background:#2f81f7;border:none;color:#fff;font-size:16px;padding:10px 26px;border-radius:8px;cursor:pointer;margin-top:16px}
button:hover{background:#1f6fd9}button:disabled{background:#555;cursor:not-allowed}
pre{text-align:left;background:#11151a;border-radius:8px;padding:12px;font-size:12px;overflow:auto;margin-top:14px;min-height:30px}
</style></head><body><div class="card">
<h1>训练日志与感悟</h1>
<p class="desc">日志与感悟按日期分文件保存到：<br>reports/日志与感悟/YYYY-MM-DD.md，标题区分日志/感悟。</p>
<label>日期</label><input id="date" type="date">
<label>类型</label><select id="kind"><option value="note">感悟</option><option value="log">日志</option></select>
<label>关联项目（可留空=综合）</label><select id="scenario"><option value="综合">综合</option></select>
<label>内容</label><textarea id="note" placeholder="日志：今天戴了袖套...；感悟：也许我们可以..."></textarea>
<button id="btn" onclick="submit()">保存</button>
<pre id="out">等待保存&#8230;</pre>
</div><script>
var scenarios=['综合','Centering 90 Easy+ No Strafes','Air Voltaic Close Long Strafes Very Easy','GP Far Long Strafes Easy','GP Close Long Strafes Easy','B90TI Iron','Smoothbot Iron','Pasu Voltaic Iron','Tamspeed 2bp Iron','Wide Wall 3 Targets TE','1w2t TE Reload','B90T Voltaic Easy Very Slow','patTS Voltaic Iron'];
var sel=document.getElementById('scenario');sel.innerHTML='';scenarios.forEach(function(s){var o=document.createElement('option');o.value=s;o.textContent=s;sel.appendChild(o);});
var d=new Date();var dd=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');document.getElementById('date').value=dd;
function submit(){var btn=document.getElementById('btn');var out=document.getElementById('out');btn.disabled=true;out.textContent='正在保存...';var body={date:document.getElementById('date').value,kind:document.getElementById('kind').value,scenario:document.getElementById('scenario').value,note:document.getElementById('note').value};fetch('/add-note',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json().then(function(x){return {status:r.status,body:x};});}).then(function(res){out.textContent='HTTP '+res.status+'\\n'+JSON.stringify(res.body,null,2);if(res.status===200){document.getElementById('note').value='';}}).catch(function(e){out.textContent='请求失败: '+e;}).finally(function(){btn.disabled=false;});}
</script></body></html>`;
module.exports = html;
