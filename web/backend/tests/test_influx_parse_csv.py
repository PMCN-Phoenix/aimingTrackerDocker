# -*- coding: utf-8 -*-
"""influx_client._parse_csv 多表头（多 schema）解析测试

背景：InfluxDB 在同一个查询结果中，不同 schema 的 table 会各自输出一次表头。
pivot 之后若某些记录缺少某个 field（如感悟有的带 scenario、有的不带），
就会出现两段表头；旧实现只按第一段表头解析，导致后续 table 的列整体错位。
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repositories.influx_client import InfluxDBClient  # noqa: E402


# 真实抓取的样例：两个 table，schema 不同（table 0 无 scenario，table 1 有 scenario）
REAL_CSV = """,result,table,_time,date,game,id,theme,content,tags,title
,_result,0,2026-10-17T14:28:17.751152384Z,2026-10-17,valorant,ref_a,aim,打完闪之后先涣散,"闪光后重置,视角重载",闪光后先涣散重载视角

,result,table,_time,date,game,id,theme,content,scenario,tags,title
,_result,1,2026-10-17T07:34:02Z,2026-10-17,valorant,ref_b,aim,在手腕放松时候更快,Reflex Flick - Easy,"VDIM,静态点击",手腕放松时更快

"""


class TestParseCsvMultiSchema(unittest.TestCase):
    def setUp(self):
        self.client = InfluxDBClient()

    def test_two_tables_both_parsed(self):
        rows = self.client._parse_csv(REAL_CSV)
        self.assertEqual(len(rows), 2)

    def test_first_table_fields_correct(self):
        rows = self.client._parse_csv(REAL_CSV)
        r0 = [r for r in rows if r.get("id") == "ref_a"][0]
        self.assertEqual(r0["title"], "闪光后先涣散重载视角")
        # tags 字段内含逗号，必须完整保留（不能被当成列分隔）
        self.assertEqual(r0["tags"], "闪光后重置,视角重载")
        self.assertEqual(r0.get("scenario"), None)

    def test_second_table_not_misaligned(self):
        """核心回归：第二段表头 schema 多了 scenario，列不能整体错位"""
        rows = self.client._parse_csv(REAL_CSV)
        r1 = [r for r in rows if r.get("id") == "ref_b"][0]
        self.assertEqual(r1["content"], "在手腕放松时候更快")
        self.assertEqual(r1["title"], "手腕放松时更快")
        self.assertEqual(r1["scenario"], "Reflex Flick - Easy")
        self.assertEqual(r1["tags"], "VDIM,静态点击")

    def test_empty_and_meta_rows_skipped(self):
        rows = self.client._parse_csv(REAL_CSV)
        for r in rows:
            self.assertNotEqual(r.get("id"), "")  # 不把空的元数据行当结果

    def test_no_header_returns_empty(self):
        self.assertEqual(self.client._parse_csv(""), [])
        self.assertEqual(self.client._parse_csv("error: something"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
