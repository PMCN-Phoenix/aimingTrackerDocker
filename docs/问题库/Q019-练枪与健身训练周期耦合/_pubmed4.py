# -*- coding: utf-8 -*-
import urllib.request, time, io
ids = [("42692380", "Harroum2026 练前有氧 meta"),
       ("42362574", "Brooks2026 高强度有氧在线学习"),
       ("41101519", "Bjørndal2025 练后运动巩固")]
E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&rettype=abstract&retmode=text&id="
out = []
for pid, lab in ids:
    req = urllib.request.Request(E + pid, headers={"User-Agent": "Mozilla/5.0"})
    t = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace").strip()
    out.append("\n## " + lab + "（PMID " + pid + "）\n\n```\n" + t + "\n```\n")
    print(pid, "ok", len(t))
    time.sleep(0.5)
p = "英文社区与学术原始数据.md"
with io.open(p, "a", encoding="utf-8") as f:
    f.write("\n---\n\n# 关键补充摘要（运动作为技能学习启动器/巩固器）\n" + "".join(out))
print("appended")
