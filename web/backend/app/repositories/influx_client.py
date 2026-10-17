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
        """解析 InfluxDB 返回的 CSV 数据（用标准 csv 模块，正确处理引号内的逗号）

        注意：InfluxDB 返回 CSV 时，**每个不同 schema 的 table 都会重复输出一次表头**。
        pivot 之后如果不同记录缺失某些 field（例如有的感悟有 scenario、有的没有），
        就会出现多段表头。只按第一段表头解析会让后续 table 的列整体错位，
        因此这里按表头行切块，逐块解析后合并。
        """
        lines = csv_data.strip().split("\n")
        header_idxs = [i for i, line in enumerate(lines) if line.startswith(",result,")]
        if not header_idxs:
            return []

        results: List[Dict[str, Any]] = []
        for n, header_idx in enumerate(header_idxs):
            end = header_idxs[n + 1] if n + 1 < len(header_idxs) else len(lines)
            chunk = [ln for ln in lines[header_idx:end] if ln.strip()]
            if not chunk:
                continue
            reader = csv.DictReader(io.StringIO("\n".join(chunk)))
            for row in reader:
                # 跳过空行和结果元数据行
                if not row.get("_value") and not row.get("_time"):
                    continue
                results.append(dict(row))

        return results


    def write(self, line_protocol: str) -> bool:
        """写入 Line Protocol 数据"""
        url = f"{self.url}/api/v2/write?org={self.org}&bucket={self.bucket}"
        req = urllib.request.Request(
            url,
            data=line_protocol.encode("utf-8"),
            method="POST"
        )
        req.add_header("Authorization", f"Token {self.token}")
        req.add_header("Content-Type", "text/plain")

        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status == 204


# 全局客户端实例
db = InfluxDBClient()
