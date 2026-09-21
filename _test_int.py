# -*- coding: utf-8 -*-
import urllib.request

INFLUX = "http://127.0.0.1:8087"
ORG = "aim-org"
TOKEN = "aim-super-secret-token-2026"

def query_flux(flux_query):
    url = INFLUX + "/api/v2/query?org=" + ORG
    req = urllib.request.Request(url, data=flux_query.encode("utf-8"), method="POST")
    req.add_header("Authorization", "Token " + TOKEN)
    req.add_header("Content-Type", "application/vnd.flux")
    req.add_header("Accept", "application/csv")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return "ERROR: " + e.read().decode("utf-8")

# 测试 int() 函数
print("=== 测试 int() 函数 ===")
q = '''
a = int(v: "1789747200")
b = a * 1000000000
c = time(v: b)
from(bucket: "aim")
  |> range(start: c, stop: c + 1000000000)
  |> count()
'''
print(query_flux(q))
