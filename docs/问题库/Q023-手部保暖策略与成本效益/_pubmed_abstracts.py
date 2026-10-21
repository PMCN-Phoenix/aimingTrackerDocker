# -*- coding: utf-8 -*-
"""Q023 关键文献摘要抓取（efetch，取结论句）"""
import urllib.request, urllib.parse, re, time, io, os, sys

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
IDS = [
    ("40343410", "职业性冷应激与复温改变灵巧度下降的皮肤温度阈值"),
    ("32364982", "轻度全身冷应激对握力与捏键等长力控制的影响"),
    ("33074012", "热应激与心理疲劳对灵巧度的独立与交互效应"),
    ("27227009", "手与脚对冷暴露的反应（综述）"),
    ("7093354", "自主暖手训练的保持与迁移（1年后）"),
    ("32885999", "防振手套导致前臂肌肉活动增加"),
    ("27052582", "快适应机械感受器与精细握力控制"),
    ("23722108", "掌部加温/降温延迟抗阻训练疲劳"),
]

def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research-client"})
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                print("  fail:", str(e)[:70]); return None
            time.sleep(2)

out = []
for pid, label in IDS:
    u = E + "?db=pubmed&retmode=xml&id=" + pid
    xml = get(u)
    if not xml:
        out.append(f"\n## {label}（PMID {pid}）\n抓取失败\n"); continue
    title = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", xml, re.S)
    abst = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", xml, re.S)
    journal = re.search(r"<Title>(.*?)</Title>", xml, re.S)
    year = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", xml, re.S)
    def clean(s):
        s = re.sub(r"<[^>]+>", "", s)
        s = (s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
              .replace("&#x2019;", "'").replace("&quot;", '"'))
        return re.sub(r"\s+", " ", s).strip()
    t = clean(title.group(1)) if title else "?"
    a = " ".join(clean(x) for x in abst)
    j = clean(journal.group(1)) if journal else "?"
    y = year.group(1) if year else "?"
    print(f"[OK] {pid} {t[:70]}")
    out.append(f"\n## {label}\n\n- **标题**：{t}\n- **期刊/年**：{j} {y}\n- **PMID**：{pid}\n\n**摘要**：\n\n{a}\n")
    time.sleep(0.5)

path = os.path.join(os.path.dirname(__file__), "关键文献摘要.md")
header = """# Q023 关键文献摘要（PubMed efetch 原文摘要）

> 采集：2026-10-21 ｜ 来源：NCBI efetch（XML 原文摘要，机器抽清洗，未改写）
> 选取标准：与「手温 → 精细运动/灵巧度/力量控制」及「手套 → 触觉与肌肉活动」直接相关

"""
with io.open(path, "w", encoding="utf-8") as f:
    f.write(header + "\n".join(out))
print("saved:", path)
