var detail = msg.error ? (msg.error.message || String(msg.error)) : '';
node.warn('周总结失败: ' + detail);
return null;