const fs = global.get('fs');

if (msg.influx_error) {
    throw new Error('InfluxDB 写入失败: ' + (msg.influx_error.errorMessage || msg.influx_error.statusCode || JSON.stringify(msg.influx_error)));
}
var meta = msg.importMeta;
try {
    var state = { files: {} };
    if (fs.existsSync(meta.stateFile)) {
        state = JSON.parse(fs.readFileSync(meta.stateFile, 'utf8'));
        if (!state.files) state.files = {};
    }
    Object.assign(state.files, meta.toSave);
    fs.writeFileSync(meta.stateFile, JSON.stringify(state, null, 2));
} catch (e) {
    throw new Error('保存导入记录失败: ' + e.message);
}
msg.payload = JSON.stringify({
    ok: true,
    message: '导入完成',
    scanned: meta.scanned,
    imported: meta.imported,
    kills: meta.kills,
    skipped: meta.skipped,
    perScenario: meta.perScenario
});
msg.statusCode = 200;
return msg;