const fs = global.get('fs');
const path = global.get('path');

const STATS_DIR = '/stats';
const STATE_FILE = '/data/imported_files.json';
const ALLOWED = ["Centering 90 Easy+ No Strafes","Air Voltaic Close Long Strafes Very Easy","GP Far Long Strafes Easy","GP Close Long Strafes Easy","B90TI Iron","Smoothbot Iron","Pasu Voltaic Iron","Tamspeed 2bp Iron","Wide Wall 3 Targets TE","1w2t TE Reload","B90T Voltaic Easy Very Slow","patTS Voltaic Iron"];
const CLICK_SCENARIOS = ["Pasu Voltaic Iron","Tamspeed 2bp Iron","Wide Wall 3 Targets TE","1w2t TE Reload","B90T Voltaic Easy Very Slow","patTS Voltaic Iron"];
const GAP_MS = 3 * 3600 * 1000;
const TZ_OFFSET_MS = 8 * 3600 * 1000;
const DAY_MS = 24 * 3600 * 1000;

let state = { files: {} };
try {
    if (fs.existsSync(STATE_FILE)) {
        state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
        if (!state.files) state.files = {};
    }
} catch (e) { state = { files: {} }; }

let files;
try {
    files = fs.readdirSync(STATS_DIR).filter(function (f) { return f.toLowerCase().endsWith('.csv'); });
} catch (e) {
    throw new Error('无法访问 stats 目录: ' + e.message);
}

function parseKills(text, time_ms, end_wall_ms) {
    var re = /^(\d+),(\d{2}):(\d{2}):(\d{2})\.(\d{3}),/gm;
    var kills = [];
    var m;
    while ((m = re.exec(text)) !== null) {
        var wall = ((+m[2] * 60 + +m[3]) * 60 + +m[4]) * 1000 + (+m[5]);
        var diff = wall - end_wall_ms;
        if (diff > 12 * 3600 * 1000) diff -= DAY_MS;
        kills.push({ time_ms: time_ms + diff });
    }
    kills.sort(function (a, b) { return a.time_ms - b.time_ms; });
    var first = kills.length ? kills[0].time_ms : time_ms;
    var prev = null;
    for (var i = 0; i < kills.length; i++) {
        var interval = prev === null ? 0 : (kills[i].time_ms - prev) / 1000;
        kills[i].interval = Number(interval.toFixed(3));
        kills[i].offset = Number(((kills[i].time_ms - first) / 1000).toFixed(3));
        prev = kills[i].time_ms;
    }
    return kills;
}

function parseFile(filename) {
    var m = filename.match(/^(.*?) - Challenge - (\d{4})\.(\d{2})\.(\d{2})-(\d{2})\.(\d{2})\.(\d{2}) Stats\.csv$/);
    if (!m) { return null; }
    var scenario = m[1].trim();
    if (ALLOWED.indexOf(scenario) < 0) { return null; }
    var time_ms = Date.UTC(+m[2], +m[3] - 1, +m[4], +m[5], +m[6], +m[7]) - TZ_OFFSET_MS;
    var end_wall_ms = ((+m[5] * 60 + +m[6]) * 60 + +m[7]) * 1000;
    var text;
    try { text = fs.readFileSync(path.join(STATS_DIR, filename), 'utf8'); } catch (e) { return null; }
    var sm = text.match(/^Score:,\s*([\d.]+)\s*$/m);
    if (!sm) { return null; }
    var score = parseFloat(sm[1]);
    var shots = 0, hits = 0, mm;
    var wre = /^[^,\r\n]+,\d+,\d+,\d+(?:\.\d+)?,\d+(?:\.\d+)?,\s*$/gm;
    while ((mm = wre.exec(text)) !== null) {
        var p = mm[0].split(',');
        shots += parseInt(p[1], 10);
        hits += parseInt(p[2], 10);
    }
    var accuracy = shots > 0 ? hits / shots * 100 : 0;
    var kills = CLICK_SCENARIOS.indexOf(scenario) >= 0 ? parseKills(text, time_ms, end_wall_ms) : [];
    return { filename: filename, scenario: scenario, time_ms: time_ms, score: score, accuracy: accuracy, kills: kills };
}

var newRecs = [], skipped = [];
for (var i = 0; i < files.length; i++) {
    var f = files[i];
    if (state.files[f]) { skipped.push(f); continue; }
    var rec = parseFile(f);
    if (!rec) { continue; }
    newRecs.push(rec);
}

var byScenario = {};
for (var j = 0; j < newRecs.length; j++) {
    var r = newRecs[j];
    if (!byScenario[r.scenario]) byScenario[r.scenario] = [];
    byScenario[r.scenario].push(r);
}

var points = [], killPoints = [], toSave = {};
Object.keys(byScenario).forEach(function (scenario) {
    var recs = byScenario[scenario].slice().sort(function (a, b) { return a.time_ms - b.time_ms; });
    var lastTime = null, lastSession = null, lastAttempt = 0;
    var prev = [];
    Object.keys(state.files).forEach(function (fn) {
        var e = state.files[fn];
        if (e.scenario === scenario) prev.push(e);
    });
    prev.sort(function (a, b) { return a.time_ms - b.time_ms; });
    if (prev.length > 0) {
        var last = prev[prev.length - 1];
        lastTime = last.time_ms;
        lastSession = last.session_id;
        lastAttempt = parseInt(last.attempt_no, 10) || 0;
    }
    recs.forEach(function (rec) {
        if (lastTime !== null && rec.time_ms - lastTime <= GAP_MS) {
            rec.session_id = lastSession;
            rec.attempt_no = String(lastAttempt + 1);
        } else {
            rec.session_id = 's' + rec.time_ms;
            rec.attempt_no = '1';
        }
        lastTime = rec.time_ms;
        lastSession = rec.session_id;
        lastAttempt = parseInt(rec.attempt_no, 10);
        points.push({
            measurement: 'aim_scenario',
            tags: { scenario: rec.scenario, session_id: rec.session_id, attempt_no: rec.attempt_no, source: 'stats' },
            fields: { score: rec.score, accuracy: Number(rec.accuracy.toFixed(1)) },
            timestamp: rec.time_ms
        });
        toSave[rec.filename] = { scenario: rec.scenario, time_ms: rec.time_ms, session_id: rec.session_id, attempt_no: rec.attempt_no };
        if (rec.kills && rec.kills.length) {
            for (var k = 0; k < rec.kills.length; k++) {
                killPoints.push({
                    measurement: 'aim_kill',
                    tags: { scenario: rec.scenario, session_id: rec.session_id, attempt_no: rec.attempt_no, source: 'stats' },
                    fields: { interval: rec.kills[k].interval, offset: rec.kills[k].offset },
                    timestamp: rec.kills[k].time_ms
                });
            }
        }
    });
});

msg.payload = points;
msg.killPoints = killPoints;
msg.importMeta = {
    scanned: files.length,
    skipped: skipped.length,
    imported: points.length,
    kills: killPoints.length,
    toSave: toSave,
    stateFile: STATE_FILE,
    perScenario: Object.keys(byScenario).reduce(function (acc, k) { acc[k] = byScenario[k].length; return acc; }, {})
};
return msg;