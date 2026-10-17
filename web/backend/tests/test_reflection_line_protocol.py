# -*- coding: utf-8 -*-
"""aim_reflection 写入（场景级感悟）Line Protocol 转义测试

修复两个病史 bug：
1) tag 值未转义 → 场景名带空格（Kovaak 场景几乎都带空格，如 "Reflex Flick - Easy"）
   会写出非法 Line Protocol，写入直接 400 失败；
2) 字符串 field 无谓地把空格和 ASCII 逗号转义成 "\\ " / "\\,"，
   反斜杠会作为内容存进库，前端看到的感悟文本带反斜杠。

运行：
    cd web/backend
    python -m unittest tests.test_reflection_line_protocol -v
"""
import re
import unittest

from app.repositories import queries


class CaptureDB:
    def __init__(self):
        self.lines = []
        self.bucket = "aim"
        self.org = "aim-org"

    def write(self, line):
        self.lines.append(line)
        return True

    def query(self, flux):
        return []


class TestReflectionLineProtocol(unittest.TestCase):
    def setUp(self):
        self._orig = queries.db
        self.db = CaptureDB()
        queries.db = self.db

    def tearDown(self):
        queries.db = self._orig

    def _line(self):
        self.assertEqual(len(self.db.lines), 1)
        return self.db.lines[0]

    def test_scenario_with_spaces_is_escaped_in_tag(self):
        queries.create_reflection("Reflex Flick - Easy", "在手腕放松时候更快")
        line = self._line()
        self.assertTrue(
            line.startswith("aim_reflection,scenario=Reflex\\ Flick\\ -\\ Easy "),
            line,
        )
        # 每个空格前必须紧跟反斜杠（否则 tag 会被空格截断）
        tag_part = line.split(' note=')[0]
        self.assertNotIn("  ", tag_part)
        self.assertEqual(tag_part.count(" "), tag_part.count("\\ "), tag_part)

    def test_note_keeps_plain_spaces_and_commas(self):
        """字符串 field 内的空格/逗号必须原样保留，不能出现反斜杠"""
        queries.create_reflection("Reflex Flick - Easy", "放松 了, 更快")
        line = self._line()
        self.assertIn('note="放松 了, 更快"', line)
        self.assertNotIn("\\,", line.split("note=")[1])
        self.assertNotIn("\\ ", line.split("note=")[1])

    def test_double_quote_in_note_is_escaped(self):
        queries.create_reflection("Reflex Flick - Easy", '他说"松一点"')
        line = self._line()
        self.assertIn('note="他说\\"松一点\\""', line)

    def test_daylist_tag_also_escaped(self):
        queries.create_reflection("Reflex Flick - Easy", "x", daylist="Viscose Day6")
        line = self._line()
        self.assertIn("daylist=Viscose\\ Day6", line)

    def test_timestamp_is_nanoseconds(self):
        queries.create_reflection("Reflex Flick - Easy", "x")
        line = self._line()
        ts = line.rsplit(" ", 1)[1]
        self.assertTrue(re.fullmatch(r"\d{19}", ts), ts)


if __name__ == "__main__":
    unittest.main(verbosity=2)
