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
  const noteText = '如果在心里默念小球的运动轨迹是偏左还是偏右，判断得更快，跟得更紧。个人感觉是增强了判断力、专注力。';
  const res = await post({ date: '2026-08-17', kind: 'note', scenario: '综合', note: noteText });
  console.log(res.status, res.body);
})();
