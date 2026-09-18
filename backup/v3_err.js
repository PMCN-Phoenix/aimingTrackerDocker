var detail = msg.error ? (msg.error.message || String(msg.error)) : '';
if (msg.res) {
    msg.payload = JSON.stringify({ ok: false, message: '操作失败', detail: detail });
    msg.statusCode = 500;
} else {
    node.warn('V3 操作失败: ' + detail);
    msg.payload = { ok: false, detail: detail };
}
return msg;