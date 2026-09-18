const http = require('http');

function post(body) {
  return new Promise((resolve, reject) => {
    const data = Buffer.from(JSON.stringify(body), 'utf8');
    const req = http.request({
      hostname: 'localhost',
      port: 1881,
      path: '/add-note',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': data.length
      }
    }, res => {
      let s = '';
      res.setEncoding('utf8');
      res.on('data', d => s += d);
      res.on('end', () => resolve({ status: res.statusCode, body: s }));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

(async () => {
  const logText = '今天没有带袖套直接操控的。然后在操控过程中会感觉上斜方肌这块会绷紧，将肩带向上，给一定的承重力。';
  const res = await post({ date: '2026-08-17', kind: 'log', scenario: '综合', note: logText });
  console.log(res.status, res.body);
})();
