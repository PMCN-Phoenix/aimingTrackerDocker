const html = `<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>训练分析</title><style>
body{font-family:"Microsoft YaHei",sans-serif;background:#1b1f24;color:#e8eaed;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.card{background:#262b33;border-radius:12px;padding:32px 40px;text-align:center;box-shadow:0 8px 30px rgba(0,0,0,.4);max-width:680px}
h1{font-size:22px;margin:0 0 8px}p.desc{color:#9aa3af;font-size:13px;margin:0 0 16px;line-height:1.7}
label{display:inline-block;margin:0 6px 0 0;color:#cbd2da;font-size:13px}
input{background:#11151a;border:1px solid #3a4149;color:#e8eaed;border-radius:6px;padding:7px;font-size:14px}
button{background:#2f81f7;border:none;color:#fff;font-size:16px;padding:12px 18px;border-radius:8px;cursor:pointer;margin:8px}
button:hover{background:#1f6fd9}button:disabled{background:#555;cursor:not-allowed}
pre{text-align:left;background:#11151a;border-radius:8px;padding:12px;font-size:12px;overflow:auto;margin-top:16px;min-height:40px;max-height:340px}
</style></head><body><div class="card">
<h1>练枪训练分析</h1>
<p class="desc">生成指定日期或今日训练分析、周总结；每日分析按日期写入 reports/场景优化日志/YYYY-MM-DD.md。<br>命令行：curl -XPOST http://localhost:1881/analyze-aim<br>指定日期：curl -XPOST "http://localhost:1881/analyze-aim?date=2026-08-13"</p>
<label>日期</label><input id="date" type="date">
<button id="btn1" onclick="runDate()">生成该日分析</button><button id="btn2" onclick="run('')">生成今日分析</button><button id="btn3" onclick="run('?mode=weekly')">生成周总结</button>
<pre id="out">等待生成&#8230;</pre>
</div><script>
function run(mode){var out=document.getElementById('out');out.textContent='正在生成...';fetch('/analyze-aim'+mode,{method:'POST'}).then(function(r){return r.json().then(function(d){return {status:r.status,body:d};});}).then(function(res){out.textContent='HTTP '+res.status+'\\n'+JSON.stringify(res.body,null,2);}).catch(function(e){out.textContent='请求失败: '+e;});}
function runDate(){var v=document.getElementById('date').value;if(!v){alert('请选择日期');return;}var out=document.getElementById('out');out.textContent='正在生成...';fetch('/analyze-aim?date='+encodeURIComponent(v),{method:'POST'}).then(function(r){return r.json().then(function(d){return {status:r.status,body:d};});}).then(function(res){out.textContent='HTTP '+res.status+'\\n'+JSON.stringify(res.body,null,2);}).catch(function(e){out.textContent='请求失败: '+e;});}
var d=new Date();var dd=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');document.getElementById('date').value=dd;
</script></body></html>`;
module.exports = html;
