# -*- coding: utf-8 -*-
"""queries.py 双表迁移期兼容测试（修复 P0-1 轮数双算）

背景：kovaak_score（新表）的 740 个成绩点已 100% 包含 aim_scenario（旧表）。
修复前的问题：计数类函数把两表结果相加 → 迁移期 24 天的轮数虚高 100%。
修复规则：计数类以新表为准，新表无数据才按粒度回退旧表，严禁相加；
          趋势类新表有数据就不查旧表；极值类（max）保持双表取 max（幂等）。

运行方式（纯 mock，不依赖 InfluxDB / Docker）：
    cd web/backend
    python -m unittest tests.test_queries_dedup -v
"""
import unittest

from app.repositories import queries


class FakeDB:
    """按 Flux 语句中的 _measurement 返回预制数据的假 InfluxDB 客户端"""

    def __init__(self, data_by_measurement):
        # data_by_measurement: {measurement: [row_dict, ...]}
        self.data = data_by_measurement
        self.calls = []
        self.bucket = "aim"
        self.org = "aim-org"

    def query(self, flux):
        self.calls.append(flux)
        for measurement, rows in self.data.items():
            if f'_measurement == "{measurement}"' in flux:
                return rows
        return []


# 测试用时间范围（2026-10-01 ~ 2026-10-15，覆盖迁移期）
START_TS = 1780272000   # 2026-10-01T00:00:00Z
END_TS = 1780876800     # 2026-10-08T00:00:00Z


class TestRoundsNoDoubleCount(unittest.TestCase):
    """轮数计数：双表同数据时必须只算一份"""

    def setUp(self):
        self._orig_db = queries.db

    def tearDown(self):
        queries.db = self._orig_db

    def test_scenario_rounds_not_doubled(self):
        """旧表 41 + 新表 41 = 真值 41，不是 82"""
        queries.db = FakeDB({
            "kovaak_score": [{"_value": "41", "scenario": "S1"}],
            "aim_scenario": [{"_value": "41", "scenario": "S1"}],
        })
        self.assertEqual(queries.get_scenario_rounds("S1", START_TS, END_TS), 41)

    def test_all_scenarios_rounds_not_doubled(self):
        """全场景计数：两个场景双表同数据，各自只算一份"""
        queries.db = FakeDB({
            "kovaak_score": [
                {"_value": "41", "scenario": "S1"},
                {"_value": "69", "scenario": "S2"},
            ],
            "aim_scenario": [
                {"_value": "41", "scenario": "S1"},
                {"_value": "67", "scenario": "S2"},
            ],
        })
        self.assertEqual(
            queries.get_all_scenarios_rounds(START_TS, END_TS),
            {"S1": 41, "S2": 69},
        )

    def test_extra_scenario_rounds_not_doubled(self):
        """加练清单轮数：双表同数据不双算"""
        queries.db = FakeDB({
            "kovaak_score": [{"_value": "12", "scenario": "S1"}],
            "aim_scenario": [{"_value": "12", "scenario": "S1"}],
        })
        n = queries.get_extra_scenario_rounds("S1", START_TS, END_TS, created_at=START_TS)
        self.assertEqual(n, 12)

    def test_new_table_queried_first_and_old_skipped(self):
        """新表有数据时只发 1 次查询且查的是新表（修复前是无脑查两张表再相加）"""
        fake = FakeDB({
            "kovaak_score": [{"_value": "3", "scenario": "S1"}],
            "aim_scenario": [{"_value": "3", "scenario": "S1"}],
        })
        queries.db = fake
        queries.get_scenario_rounds("S1", START_TS, END_TS)
        self.assertEqual(len(fake.calls), 1)
        self.assertIn("kovaak_score", fake.calls[0])


class TestFallbackToOldTable(unittest.TestCase):
    """回退逻辑：新表没有数据时才用旧表（保证迁移不全也不丢数据）"""

    def setUp(self):
        self._orig_db = queries.db

    def tearDown(self):
        queries.db = self._orig_db

    def test_scenario_rounds_fallback(self):
        queries.db = FakeDB({
            "kovaak_score": [],
            "aim_scenario": [{"_value": "7", "scenario": "S1"}],
        })
        self.assertEqual(queries.get_scenario_rounds("S1", START_TS, END_TS), 7)

    def test_all_scenarios_rounds_full_fallback(self):
        """新表整体无数据 → 整体回退旧表"""
        queries.db = FakeDB({
            "kovaak_score": [],
            "aim_scenario": [{"_value": "9", "scenario": "S1"}],
        })
        self.assertEqual(queries.get_all_scenarios_rounds(START_TS, END_TS), {"S1": 9})

    def test_all_scenarios_rounds_per_scenario_fallback(self):
        """S1 新表有数据用新表；S2 新表缺失用旧表兜底（按场景粒度，不双算）"""
        queries.db = FakeDB({
            "kovaak_score": [{"_value": "10", "scenario": "S1"}],
            "aim_scenario": [
                {"_value": "10", "scenario": "S1"},
                {"_value": "5", "scenario": "S2"},
            ],
        })
        self.assertEqual(
            queries.get_all_scenarios_rounds(START_TS, END_TS),
            {"S1": 10, "S2": 5},
        )

    def test_history_fallback_to_old(self):
        queries.db = FakeDB({
            "kovaak_score": [],
            "aim_scenario": [
                {"_time": "2026-10-01T00:00:00Z", "_value": "80", "scenario": "S1"},
            ],
        })
        history = queries.get_scenario_history("S1", days=30)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["score"], 80.0)


class TestHistoryNoDuplicatePoints(unittest.TestCase):
    """历史趋势：新表有数据时不得把旧表的同一点再追加一遍"""

    def setUp(self):
        self._orig_db = queries.db

    def tearDown(self):
        queries.db = self._orig_db

    def test_history_no_duplicates(self):
        queries.db = FakeDB({
            "kovaak_score": [
                {"_time": "2026-10-01T00:00:00Z", "_value": "80", "scenario": "S1"},
                {"_time": "2026-10-02T00:00:00Z", "_value": "85", "scenario": "S1"},
            ],
            "aim_scenario": [
                {"_time": "2026-10-01T00:00:00Z", "_value": "80", "scenario": "S1"},
                {"_time": "2026-10-02T00:00:00Z", "_value": "85", "scenario": "S1"},
            ],
        })
        history = queries.get_scenario_history("S1", days=30)
        self.assertEqual(len(history), 2)
        self.assertEqual([h["score"] for h in history], [80.0, 85.0])


class TestBestScoreStillMaxAcrossTables(unittest.TestCase):
    """最佳成绩：双表取 max 是幂等的，且能兜底旧表独有的点"""

    def setUp(self):
        self._orig_db = queries.db

    def tearDown(self):
        queries.db = self._orig_db

    def test_best_takes_max(self):
        queries.db = FakeDB({
            "kovaak_score": [
                {"_field": "score", "_value": "90", "scenario": "S1"},
                {"_field": "accuracy", "_value": "0.25", "scenario": "S1"},
            ],
            "aim_scenario": [
                {"_field": "score", "_value": "95", "scenario": "S1"},
            ],
        })
        best = queries.get_scenario_best("S1", START_TS, END_TS)
        self.assertEqual(best["score"], 95.0)
        self.assertEqual(best["accuracy"], 0.25)


class TestWindowScoresAndRoundStats(unittest.TestCase):
    """时间窗内成绩聚合：测试 round_stats（衰减率）与 session（会话时段）"""

    def setUp(self):
        self._orig_db = queries.db

    def tearDown(self):
        queries.db = self._orig_db

    def test_round_stats_and_session(self):
        # 模拟两轮成绩：第 1 轮 100 分，第 2 轮 80 分 -> 衰减 -20%
        # 时间 01:00:00Z (北京时间 09:00) 到 03:00:00Z (北京时间 11:00) -> 120 分钟 -> overtime
        queries.db = FakeDB({
            "kovaak_score": [
                {"_field": "score", "_value": "100.0", "scenario": "S1", "_time": "2026-10-14T01:00:00Z"},
                {"_field": "hits", "_value": "50.0", "scenario": "S1", "_time": "2026-10-14T01:00:00Z"},
                {"_field": "misses", "_value": "50.0", "scenario": "S1", "_time": "2026-10-14T01:00:00Z"},
                {"_field": "score", "_value": "80.0", "scenario": "S1", "_time": "2026-10-14T03:00:00Z"},
                {"_field": "hits", "_value": "40.0", "scenario": "S1", "_time": "2026-10-14T03:00:00Z"},
                {"_field": "misses", "_value": "60.0", "scenario": "S1", "_time": "2026-10-14T03:00:00Z"},
            ]
        })
        scores, session = queries._get_window_scores(START_TS, END_TS)
        self.assertIn("S1", scores)
        s1 = scores["S1"]
        self.assertEqual(s1["score"], 100.0)
        self.assertEqual(s1["accuracy"], 45.0)
        stats = s1["round_stats"]
        self.assertIsNotNone(stats)
        self.assertEqual(stats["n"], 2)
        self.assertEqual(stats["first"], 100.0)
        self.assertEqual(stats["last"], 80.0)
        self.assertEqual(stats["best"], 100.0)
        self.assertEqual(stats["drop_pct"], -20.0)

        self.assertIsNotNone(session)
        self.assertEqual(session["start"], "09:00")
        self.assertEqual(session["end"], "11:00")
        self.assertEqual(session["duration_min"], 120)
        self.assertTrue(session["is_overtime"])


if __name__ == "__main__":
    unittest.main()
