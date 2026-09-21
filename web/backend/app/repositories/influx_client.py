# -*- coding: utf-8 -*-
"""InfluxDB 客户端"""
import urllib.request
import csv
import io
from typing import List, Dict, Any, Optional

INFLUX_URL = "http://127.0.0.1:8087"
INFLUX_ORG = "aim-org"
INFLUX_BUCKET = "aim"
INFLUX_TOKEN = "aim-super-secret-token-2026"


class InfluxDBClient:
    def __init__(self, url: str = INFLUX_URL, org: str = INFLUX_ORG,
                 bucket: str = INFLUX_BUCKET, token: str = INFLUX_TOKEN):
        self.url = url
        self.org = org
        self.bucket = bucket
        self.token = token

    def query(self, flux_query: str) -> List[Dict[str, Any]]:
        """执行 Flux 查询，返回解析后的行列表"""
        url = f"{self.url}/api/v2/query?org={self.org}"
        req = urllib.request.Request(
            url,
            data=flux_query.encode("utf-8"),
            method="POST"
        )
        req.add_header("Authorization", f"Token {self.token}")
        req.add_header("Content-Type", "application/vnd.flux")
        req.add_header("Accept", "application/csv")

        with urllib.request.urlopen(req, timeout=30) as response:
            csv_data = response.read().decode("utf-8")

        return self._parse_csv(csv_data)

    def _parse_csv(self, csv_data: str) -> List[Dict[str, Any]]:
        """解析 InfluxDB 返回的 CSV 数据（用标准 csv 模块，正确处理引号内的逗号）"""
        # 找到第一个 header 行（以 ,result, 开头）
        lines = csv_data.strip().split("\n")
        header_idx = -1
        for i, line in enumerate(lines):
            if line.startswith(",result,"):
                header_idx = i
                break

        if header_idx == -1:
            return []

        # 从 header 行开始，用 csv 模块解析
        csv_text = "\n".join(lines[header_idx:])
        reader = csv.DictReader(io.StringIO(csv_text))
        results = []
        for row in reader:
            # 跳过空行和结果元数据行
            if not row.get("_value") and not row.get("_time"):
                continue
            results.append(dict(row))

        return results


# 全局客户端实例
db = InfluxDBClient()
