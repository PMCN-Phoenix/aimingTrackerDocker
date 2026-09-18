const fs = require('fs');
const base = 'D:/11.project/iwen-codex/codex-list/aim-tracker-docker/reports';
const oldFile = base + '/训练感悟日志.md';
const newDir = base + '/日志与感悟';
const newFile = newDir + '/2026-08-13.md';

if (fs.existsSync(oldFile)) {
  const s = fs.readFileSync(oldFile, 'utf8').replace(/^\uFEFF/, '');
  const marker = '## 2026-08-13';
  const idx = s.indexOf(marker);
  let note = '';
  if (idx >= 0) {
    note = s.slice(idx + marker.length).trim();
  }
  if (!fs.existsSync(newDir)) fs.mkdirSync(newDir, { recursive: true });
  const content = '# 日志与感悟\n\n## 2026-08-13 · 感悟\n\n' + note + '\n';
  fs.writeFileSync(newFile, content, 'utf8');
  fs.unlinkSync(oldFile);
  console.log('migrated old note file');
} else {
  console.log('old note file not found');
}
