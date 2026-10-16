#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""backup_aim_scenario.py 的单元测试（2026-10-16 决策①：旧表备份CSV+标记弃用）

覆盖：
  - summarize_annotated_csv：annotated CSV 解析统计（纯函数）
  - fetch_annotated_csv：HTTP 请求构造与返回（mock urlopen）
  - main：--dry-run 不落盘、空数据退出码 3（mock fetch）

运行（不依赖 InfluxDB）：
    python -m unittest test_backup_aim_scenario -v
"""
import io
import unittest
from unittest.mock import patch, MagicMock

import backup_aim_scenario as bas

# 一段贴近真实的 InfluxDB annotated CSV（aim_scenario 旧表格式）
SAMPLE_CSV = """\
#datatype,string,long,dateTime:RFC3339,dateTime:RFC3339,dateTime:RFC3339,double,string,string,string,string,long,string
#group,false,false,true,true,false,false,true,true,true,true,false,true
,result,table,_start,_stop,_time,_value,_field,_measurement,scenario,session_id,attempt_no,list
,_result,0,1970-01-01T00:00:00Z,2030-01-01T00:00:00Z,2026-09-20T10:00:00Z,85.5,score,aim_scenario,Centering 90 Easy+ No Strafes,s1,1,viscose-s2-easier
,_result,0,1970-01-01T00:00:00Z,2030-01-01T00:00:00Z,2026-09-20T10:00:00Z,0.32,accuracy,aim_scenario,Centering 90 Easy+ No Strafes,s1,1,viscose-s2-easier
,_result,0,1970-01-01T00:00:00Z,2030-01-01T00:00:00Z,2026-09-21T10:00:00Z,87,score,aim_scenario,Air Voltaic Close Long Strafes Very Easy,s2,1,viscose-s2-easier
"""


class TestSummarize(unittest.TestCase):
    def test_parses_rows_scenarios_fields_timerange(self):
        stats = bas.summarize_annotated_csv(SAMPLE_CSV)
        self.assertTrue(stats["has_header"])
        self.assertEqual(stats["rows"], 3)
        self.assertEqual(stats["scenarios"], 2)
        self.assertEqual(stats["fields"], {"score", "accuracy"})
        self.assertEqual(stats["min_time"], "2026-09-20T10:00:00Z")
        self.assertEqual(stats["max_time"], "2026-09-21T10:00:00Z")

    def test_empty_text_returns_zero_rows(self):
        stats = bas.summarize_annotated_csv("")
        self.assertFalse(stats["has_header"])
        self.assertEqual(stats["rows"], 0)
        self.assertEqual(stats["scenarios"], 0)

    def test_garbage_text_returns_zero_rows(self):
        stats = bas.summarize_annotated_csv("not a csv at all\nsecond line")
        self.assertEqual(stats["rows"], 0)


class TestFetch(unittest.TestCase):
    def test_fetch_sends_flux_and_returns_text(self):
        resp = MagicMock()
        resp.read.return_value = SAMPLE_CSV.encode("utf-8")
        ctx = MagicMock()
        ctx.__enter__.return_value = resp
        with patch("backup_aim_scenario.urllib.request.urlopen", return_value=ctx) as mock_open:
            text = bas.fetch_annotated_csv()
        self.assertIn("aim_scenario", text)
        req = mock_open.call_args[0][0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "Token " + bas.TOKEN)
        self.assertIn("application/csv", req.get_header("Accept"))
        self.assertIn('_measurement == "aim_scenario"', req.data.decode("utf-8"))


class TestMain(unittest.TestCase):
    @patch("backup_aim_scenario.fetch_annotated_csv", return_value=SAMPLE_CSV)
    def test_dry_run_prints_stats_and_writes_nothing(self, _mock):
        with patch("sys.argv", ["backup_aim_scenario.py", "--dry-run"]):
            with patch("sys.stdout", new=io.StringIO()) as out:
                bas.main()  # dry-run 正常返回，不应抛 SystemExit
            output = out.getvalue()
        self.assertIn("3 个数据点", output)
        self.assertIn("--dry-run", output)
        self.assertIn("2 个场景", output)

    @patch("backup_aim_scenario.fetch_annotated_csv", return_value="")
    def test_empty_data_exits_3(self, _mock):
        with patch("sys.argv", ["backup_aim_scenario.py"]):
            with self.assertRaises(SystemExit) as cm:
                bas.main()
        self.assertEqual(cm.exception.code, 3)

    @patch("backup_aim_scenario.fetch_annotated_csv", side_effect=OSError("connection refused"))
    def test_connection_error_exits_2(self, _mock):
        with patch("sys.argv", ["backup_aim_scenario.py"]):
            with self.assertRaises(SystemExit) as cm:
                bas.main()
        self.assertEqual(cm.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
