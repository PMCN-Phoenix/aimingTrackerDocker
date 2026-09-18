const fs = global.get('fs');
const influx = global.get('influxClient');
const Point = global.get('influxPoint');
const REPORTS_DIR = '/reports';

function pad(n) { return String(n).padStart(2, '0'); }
function fmtDate(ms) { var d = new Date(ms); return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); }

var body = msg.payload;
if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) {}
}
var scenario = (body && body.scenario) ? String(body.scenario).trim() : '综合';
var note = (body && body.note) ? String(body.note).trim() : '';
var date = (body && body.date) ? String(body.date) : null;
if (!note) {
    msg.payload = JSON.stringify({ ok: false, message: '感悟内容不能为空' });
    msg.statusCode = 400;
    return msg;
}
var now = Date.now();
var day = date || fmtDate(now);
var timestamp = date ? new Date(date + 'T00:00:00+08:00').getTime() : now;
if (isNaN(timestamp)) timestamp = now;

var writeApi = influx.getWriteApi('aim-org', 'aim', 'ms');
var p = new Point('aim_note')
    .tag('scenario', scenario)
    .tag('source', 'manual')
    .stringField('note', note)
    .timestamp(timestamp);
writeApi.writePoint(p);
return writeApi.flush(true).then(function () {
    writeApi.dispose();
    var file = REPORTS_DIR + '/训练感悟日志.md';
    var line = '\n## ' + day + (scenario !== '综合' ? ' · ' + scenario : '') + '\n\n' + note + '\n';
    if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR, { recursive: true });
    fs.appendFileSync(file, line, 'utf8');
    msg.payload = JSON.stringify({ ok: true, message: '感悟已保存', date: day, scenario: scenario });
    msg.statusCode = 200;
    return msg;
}).catch(function (e) {
    writeApi.dispose();
    throw new Error('写入失败: ' + (e.message || e));
});