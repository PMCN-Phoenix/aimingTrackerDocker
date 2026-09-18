var influx = global.get('influxClient');
var Point = global.get('influxPoint');
var writeApi = influx.getWriteApi('aim-org', 'aim', 'ms');
function writeOne(element) {
    var p = new Point(element.measurement);
    Object.keys(element.fields).forEach(function (k) {
        var v = element.fields[k];
        if (typeof v === 'string') { p.stringField(k, v); }
        else { p.floatField(k, v); }
    });
    if (element.tags) {
        Object.keys(element.tags).forEach(function (t) { p.tag(t, String(element.tags[t])); });
    }
    if (element.timestamp) { p.timestamp(element.timestamp); }
    writeApi.writePoint(p);
}
try {
    var arr = (msg.payload || []).concat(msg.killPoints || []);
    arr.forEach(writeOne);
} catch (e) {
    writeApi.dispose();
    throw new Error('写入失败: ' + e.message);
}
return writeApi.flush(true).then(function () {
    writeApi.dispose();
    return msg;
}).catch(function (e) {
    writeApi.dispose();
    throw new Error('InfluxDB 写入失败: ' + (e.message || e));
});