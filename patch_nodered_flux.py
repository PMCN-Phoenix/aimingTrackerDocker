# -*- coding: utf-8 -*-
"""一次性补丁：Node-RED 分析/周总结节点改读 kovaak_score（新表优先+旧表兜底）

2026-10-16 成绩表迁移：aim_scenario（旧表）数据已 100% 并入 kovaak_score（新表）。
aim-analyze-main / aim-weekly-main 两个 function 节点里的 scenarioRows 查询
原写死读旧表，导致 10-05 之后的数据在分析报告/周总结里看不到。

改法：新表优先查询，新表无数据才回退旧表（与 web 后端 queries.py 同规则）。

注意：flows.json 是 JSON 文件，func 里的 JS 代码中双引号以 \\" 形式存盘、
换行以 \n 形式存盘。因此本脚本的 OLD/NEW 必须用 raw 字符串，逐字符对齐文件文本。
"""
import json
import sys

PATH = "nodered_data/flows.json"

# 文件中的原始文本（raw：保留 \" 与 \n 转义形态）
OLD = (
    r"var scenarioRows = await collect('from(bucket: \"aim\") "
    r"|> range(start: -30d) "
    r"|> filter(fn: (r) => r._measurement == \"aim_scenario\") "
    r"|> filter(fn: (r) => r._field == \"score\" or r._field == \"accuracy\") "
    r"|> group()');"
)

NEW = (
    r"// 2026-10-16 成绩表迁移：aim_scenario（旧表）已弃用（数据 100% 并入 kovaak_score），新表优先、旧表仅兜底\n"
    r"        var scenarioRows = await collect('from(bucket: \"aim\") "
    r"|> range(start: -30d) "
    r"|> filter(fn: (r) => r._measurement == \"kovaak_score\") "
    r"|> filter(fn: (r) => r._field == \"score\" or r._field == \"accuracy\") "
    r"|> group()');\n"
    r"        if (!scenarioRows.length) { scenarioRows = await collect('from(bucket: \"aim\") "
    r"|> range(start: -30d) "
    r"|> filter(fn: (r) => r._measurement == \"aim_scenario\") "
    r"|> filter(fn: (r) => r._field == \"score\" or r._field == \"accuracy\") "
    r"|> group()'); }"
)


def main():
    with open(PATH, encoding="utf-8") as f:
        raw = f.read()

    count = raw.count(OLD)
    print("匹配到 %d 处" % count)
    if count != 2:
        print("预期 2 处（aim-analyze-main + aim-weekly-main），实际 %d 处，终止" % count)
        sys.exit(1)

    raw = raw.replace(OLD, NEW)

    # 校验 JSON 完整性后再落盘
    flows = json.loads(raw)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(raw)
    print("JSON 校验通过，节点数: %d" % len(flows))

    # 验证两个节点都已改到
    for node in flows:
        if node.get("id") in ("aim-analyze-main", "aim-weekly-main"):
            func = node["func"]
            has_new = '_measurement == "kovaak_score"' in func
            has_fallback = "if (!scenarioRows.length)" in func
            main_idx = func.find("var scenarioRows")
            seg = func[main_idx:main_idx + 400]
            main_is_new = "kovaak_score" in seg
            print("%s | 主查询新表: %s | 兜底存在: %s" % (node["id"], main_is_new, has_fallback))
            assert has_new and has_fallback and main_is_new
    print("补丁完成")


if __name__ == "__main__":
    main()
