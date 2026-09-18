const fs = global.get('fs');
const influx = global.get('influxClient');
const Point = global.get('influxPoint');
const REPORTS_DIR = '/reports';
const BENCH_FILE = '/data/benchmarks.json';
const ALLOWED = ["Centering 90 Easy+ No Strafes","Air Voltaic Close Long Strafes Very Easy","GP Far Long Strafes Easy","GP Close Long Strafes Easy","B90TI Iron","Smoothbot Iron","Pasu Voltaic Iron","Tamspeed 2bp Iron","Wide Wall 3 Targets TE","1w2t TE Reload","B90T Voltaic Easy Very Slow","patTS Voltaic Iron"];
const CLICK = ["Pasu Voltaic Iron","Tamspeed 2bp Iron","Wide Wall 3 Targets TE","1w2t TE Reload","B90T Voltaic Easy Very Slow","patTS Voltaic Iron"];
const CATEGORY = {
    "Centering 90 Easy+ No Strafes": "tracking",
    "Air Voltaic Close Long Strafes Very Easy": "tracking",
    "GP Far Long Strafes Easy": "tracking",
    "GP Close Long Strafes Easy": "tracking",
    "B90TI Iron": "tracking",
    "Smoothbot Iron": "tracking",
    "Pasu Voltaic Iron": "clicking",
    "Tamspeed 2bp Iron": "clicking",
    "Wide Wall 3 Targets TE": "clicking",
    "1w2t TE Reload": "clicking",
    "B90T Voltaic Easy Very Slow": "switching",
    "patTS Voltaic Iron": "switching"
};

function pad(n) { return String(n).padStart(2, '0'); }
function fmtDate(ms) { var d = new Date(ms); return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); }
function fmtDateTime(ms) { var d = new Date(ms); return fmtDate(ms) + ' ' + pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes()); }
function toMs(t) { return t instanceof Date ? t.getTime() : new Date(t).getTime(); }
function round(v, n) { var p = Math.pow(10, n || 1); return Math.round(v * p) / p; }
function mean(arr) { if (!arr.length) return 0; var s = 0; for (var i = 0; i < arr.length; i++) s += arr[i]; return s / arr.length; }
function median(arr) { if (!arr.length) return 0; var a = arr.slice().sort(function (x, y) { return x - y; }); var mid = Math.floor(a.length / 2); return a.length % 2 ? a[mid] : (a[mid - 1] + a[mid]) / 2; }
function loadBench() { try { return JSON.parse(fs.readFileSync(BENCH_FILE, 'utf8')); } catch (e) { return { scenarios: {}, ranks: [] }; } }

async function collect(flux) { var qa = influx.getQueryApi('aim-org'); return await qa.collectRows(flux); }

function buildScenarioMap(rows) {
    var map = {};
    rows.forEach(function (r) {
        var s = r.scenario, sid = r.session_id, att = r.attempt_no;
        if (!map[s]) map[s] = { sessions: {} };
        if (!map[s].sessions[sid]) map[s].sessions[sid] = { time: toMs(r._time), attempts: {} };
        if (!map[s].sessions[sid].attempts[att]) map[s].sessions[sid].attempts[att] = { time: toMs(r._time) };
        map[s].sessions[sid].attempts[att][r._field] = r._value;
    });
    return map;
}

function buildKillMap(rows) {
    var map = {};
    rows.forEach(function (r) {
        var s = r.scenario, sid = r.session_id, att = r.attempt_no;
        var t = toMs(r._time);
        if (!map[s]) map[s] = { sessions: {} };
        if (!map[s].sessions[sid]) map[s].sessions[sid] = { attempts: {} };
        if (!map[s].sessions[sid].attempts[att]) map[s].sessions[sid].attempts[att] = [];
        var arr = map[s].sessions[sid].attempts[att];
        var found = null;
        for (var i = 0; i < arr.length; i++) { if (arr[i].time === t) { found = arr[i]; break; } }
        if (!found) { found = { time: t }; arr.push(found); }
        found[r._field] = r._value;
    });
    return map;
}

function voltaicGrade(score, entry, ranks) {
    if (!entry || !entry.thresholds) return null;
    var th = entry.thresholds;
    var idx = -1;
    for (var i = 0; i < th.length; i++) { if (score >= th[i]) idx = i; }
    if (idx < 0) return { rank: 'Below ' + ranks[0], idx: -1, benchmark: entry.benchmark };
    var name = ranks[idx]; name = name.charAt(0).toUpperCase() + name.slice(1);
    return { rank: name, idx: idx, benchmark: entry.benchmark };
}

function histGrade(score, histScores) {
    if (!histScores.length) return { grade: '-', pct: 0 };
    var below = 0;
    histScores.forEach(function (x) { if (x <= score) below++; });
    var pct = below / histScores.length * 100;
    var grade = pct >= 90 ? 'S' : pct >= 75 ? 'A' : pct >= 50 ? 'B' : pct >= 25 ? 'C' : 'D';
    return { grade: grade, pct: Math.round(pct) };
}

function describe(scenario, score, acc, volt, hist, cat) {
    var one = '';
    if (volt) { one = '参考段位 ' + volt.rank + '，今日得分 ' + round(score, 1) + '。'; }
    else { one = '个人历史分位 ' + hist.pct + '%，评级 ' + hist.grade + '。'; }
    var para = '';
    if (cat === 'tracking') {
        para = '从 Voltaic tracking 分类看，跟踪类得分主要受平滑度与目标切换损耗影响。' + (acc < 90 ? ' 命中率偏低说明准星在目标边缘抖动较多，更接近 reactive 型瓶颈。' : ' 命中率尚可，但得分提升需要进一步压缩无效位移与重定位损耗。') + ' 本项仅做诊断，不下达具体训练作业，可参考 Aimer7 平滑跟踪的“先稳后快”思路理解当前瓶颈。';
    } else if (cat === 'clicking') {
        para = '点击类瓶颈通常分确认速度与命中效率两段。' + (acc < 90 ? ' 命中率说明开枪略快，击发前未完成确认。' : ' 命中率尚可，瓶颈更多在目标间切换节奏与回正。') + ' 这与 Voltaic 社区常说的 flick→confirm→micro-correct 链路一致。';
    } else {
        para = '切换类主要看目标获取时间与停驻效率。当前表现说明切换后的停驻稳定性是主要变量，符合 Voltaic switching 分类的常见瓶颈。';
    }
    return { one: one, para: para };
}

function paceOf(killsArr) {
    var arr = killsArr.slice().sort(function (a, b) { return a.offset - b.offset; });
    var intervals = [];
    for (var i = 1; i < arr.length; i++) intervals.push(arr[i].interval);
    var med = median(intervals);
    var maxOffset = arr.length ? arr[arr.length - 1].offset : 0;
    var best = { rate: 0, at: 0, count: 0 };
    var worst = { rate: Infinity, at: 0, count: 0 };
    for (var i = 0; i < arr.length; i++) {
        var start = arr[i].offset;
        if (maxOffset > 10 && start > maxOffset - 10) break;
        var count = 0;
        for (var j = i; j < arr.length && arr[j].offset <= start + 10; j++) count++;
        var rate = count / 10;
        if (rate > best.rate) best = { rate: round(rate, 2), at: round(start, 1), count: count };
        if (rate < worst.rate) worst = { rate: round(rate, 2), at: round(start, 1), count: count };
    }
    return { kills: arr.length, medianInterval: round(med, 3), best: best, worst: worst };
}

return (async function () {
    try {
        var mode = msg.analyzeMode || ((msg.req && msg.req.query && msg.req.query.mode) || 'session');
        var bench = loadBench();
        var scenarioRows = await collect('from(bucket: "aim") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "aim_scenario") |> filter(fn: (r) => r._field == "score" or r._field == "accuracy") |> group()');
        var killRows = await collect('from(bucket: "aim") |> range(start: -30d) |> filter(fn: (r) => r._measurement == "aim_kill") |> group()');
        var scen = buildScenarioMap(scenarioRows);
        var kills = buildKillMap(killRows);
        var now = Date.now();
        var dateStr = fmtDate(now);
        var lines = [];
        lines.push(mode === 'weekly' ? '## ' + dateStr + ' 周总结' : '## ' + dateStr + ' 训练分析');
        var summary = {};
        var total = 0;
        ALLOWED.forEach(function (scenario) {
            if (!scen[scenario]) {
                lines.push('');
                lines.push('### ' + scenario);
                lines.push('- 暂无数据');
                return;
            }
            var sessions = scen[scenario].sessions;
            var sids = Object.keys(sessions);
            sids.sort(function (a, b) { return sessions[a].time - sessions[b].time; });
            var latestSid = sids[sids.length - 1];
            var latest = sessions[latestSid];
            var attNums = Object.keys(latest.attempts).sort(function (a, b) { return parseInt(a, 10) - parseInt(b, 10); });
            var scores = [], accs = [];
            attNums.forEach(function (att) {
                var a = latest.attempts[att];
                if (typeof a.score === 'number') scores.push(a.score);
                if (typeof a.accuracy === 'number') accs.push(a.accuracy);
            });
            var avgScore = mean(scores);
            var bestScore = scores.length ? Math.max.apply(null, scores) : 0;
            var avgAcc = mean(accs);
            var histScores = [];
            sids.forEach(function (sid) {
                var s = sessions[sid];
                var hs = [];
                Object.keys(s.attempts).forEach(function (att) {
                    if (typeof s.attempts[att].score === 'number') hs.push(s.attempts[att].score);
                });
                if (hs.length) histScores.push(mean(hs));
            });
            var histAvg = mean(histScores);
            var histBest = histScores.length ? Math.max.apply(null, histScores) : 0;
            var hist = histGrade(avgScore, histScores);
            var volt = voltaicGrade(avgScore, bench.scenarios[scenario], bench.ranks);
            var cat = CATEGORY[scenario] || 'tracking';
            var txt = describe(scenario, avgScore, avgAcc, volt, hist, cat);
            lines.push('');
            lines.push('### ' + scenario);
            lines.push('- 本次: 得分 ' + round(avgScore, 1) + '（最佳 ' + round(bestScore, 1) + '），命中率 ' + round(avgAcc, 1) + '%');
            if (volt) lines.push('- Voltaic 参考: ' + volt.rank + '（映射基准 ' + volt.benchmark + '）');
            lines.push('- 个人历史: 近30天均值 ' + round(histAvg, 1) + '，最佳 ' + round(histBest, 1) + '，今日分位 ' + hist.pct + '%');
            lines.push('- 评级: ' + (volt ? volt.rank : hist.grade));
            lines.push('- 点评: ' + txt.one);
            lines.push('- 分析: ' + txt.para);
            if (mode === 'weekly' && histAvg > 0) {
                var change = (avgScore - histAvg) / histAvg * 100;
                lines.push('- 本周趋势: 较30天均值 ' + (change >= 0 ? '+' : '') + round(change, 1) + '%');
            }
            if (CLICK.indexOf(scenario) >= 0 && kills[scenario] && kills[scenario].sessions[latestSid]) {
                var katt = kills[scenario].sessions[latestSid].attempts;
                attNums.forEach(function (att) {
                    if (!katt[att] || !katt[att].length) return;
                    var p = paceOf(katt[att]);
                    lines.push('- 速率(第' + att + '次): 击杀 ' + p.kills + '，间隔中位数 ' + p.medianInterval + 's；最快10秒窗 ' + p.best.count + '杀/10s（起始' + p.best.at + 's），最慢10秒窗 ' + p.worst.count + '杀/10s（起始' + p.worst.at + 's）');
                });
            }
            summary[scenario] = { avgScore: round(avgScore, 1), accuracy: round(avgAcc, 1), grade: (volt ? volt.rank : hist.grade) };
            total++;
        });
        if (total === 0) {
            msg.payload = JSON.stringify({ ok: true, message: '暂无可用数据，请先执行导入', mode: mode });
            msg.statusCode = 200;
            return msg;
        }
        var file = mode === 'weekly' ? REPORTS_DIR + '/每周训练总结.md' : REPORTS_DIR + '/场景优化日志.md';
        var content = lines.join('\n') + '\n\n';
        if (!fs.existsSync(REPORTS_DIR)) fs.mkdirSync(REPORTS_DIR, { recursive: true });
        fs.appendFileSync(file, content, 'utf8');
        msg.payload = JSON.stringify({ ok: true, mode: mode, file: file.replace('/reports/', 'reports/'), scenarios: summary, generatedAt: fmtDateTime(now) });
        msg.statusCode = 200;
        return msg;
    } catch (e) {
        throw new Error('分析失败: ' + (e && e.message ? e.message : e));
    }
})();