#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
看板生成器（B / C / D + A 的标题与跳转）
=======================================
把三块新看板生成为 Grafana provisioning JSON：
  grafana/provisioning/dashboards/viscose-s2-easier.json  （B：格子填色总表）
  grafana/provisioning/dashboards/aimlab.json             （C：Aim Lab）
  grafana/provisioning/dashboards/viscose-daylist.json    （D：今日清单）
并给 A 看板加清单名与互跳链接。

设计依据：docs/练枪看板-技术方案.md
  数据来源：aim_bench_row（物化行，含 rowJson）/ aim_bench_meta（汇总）/ aim_scenario / aim_daylist
  自绘面板：gapit-htmlgraphics-panel（options: html / css / onRender，数据经 htmlGraphics.data.series）

用法: python build_dashboard.py            # 生成 JSON（覆盖写）
      python build_dashboard.py --check    # 只检查 JSON 合法性
"""
import sys
import os
import json

BASE = os.path.dirname(os.path.abspath(__file__))
DASH_DIR = os.path.join(BASE, "grafana", "provisioning", "dashboards")
DS = {"type": "influxdb", "uid": "influxdb-aim"}
LOC = 'option location = {zone: "Asia/Shanghai", offset: 8h}\n'

TIERS = ["Lemming", "Hare", "Ermine", "Puffin", "Penguin", "Fox", "Mammoth", "Orca", "Seal"]


def q(flux):
    return 'option location = {zone: "Asia/Shanghai", offset: 8h}\n' + flux


def target(ref, flux):
    return {"refId": ref, "datasource": DS, "query": q(flux), "hide": False}


def stat_panel(pid, title, flux, desc, mappings=None, unit="short", step_at=None, x=0, y=0, w=6, h=5):
    steps = [{"color": "text", "value": None}] if step_at is None else [
        {"color": "text", "value": None}, {"color": "green", "value": step_at}]
    return {
        "id": pid, "type": "stat", "title": title, "description": desc, "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "targets": [target("A", flux)],
        "options": {"reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
                    "orientation": "auto", "textMode": "auto", "colorMode": "value",
                    "graphMode": "none", "justifyMode": "auto", "wideLayout": True},
        "fieldConfig": {"defaults": {"unit": unit, "mappings": mappings or [],
                                     "thresholds": {"mode": "absolute", "steps": steps},
                                     "color": {"mode": "thresholds"}},
                        "overrides": []},
    }


def barchart_panel(pid, title, flux, desc, overrides=None, x=0, y=0, w=24, h=9):
    return {
        "id": pid, "type": "barchart", "title": title, "description": desc, "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "targets": [target("A", flux)],
        "options": {"orientation": "horizontal", "xTickLabelRotation": 0, "xTickLabelSpacing": 0,
                    "showValue": "auto", "stacking": "none", "groupWidth": 0.7, "barWidth": 0.97,
                    "barRadius": 0.05, "fullHighlight": False, "tooltip": {"mode": "single", "sort": "none"},
                    "legend": {"showLegend": False, "displayMode": "list", "placement": "bottom", "calcs": []}},
        "fieldConfig": {"defaults": {"unit": "short", "color": {"mode": "fixed", "fixedColor": "blue"},
                                     "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]},
                                     "mappings": []},
                        "overrides": overrides or []},
    }


def html_panel(pid, title, flux, desc, html, css, js, x=0, y=0, w=24, h=44, flux_rows=None):
    """gapit-htmlgraphics-panel：面板内自绘 HTML（B 的格子表 / 分布 / D 的对比卡）
    flux_rows 若给出，则用它替换面板的查询（便于同一数据源画多个面板）"""
    return {
        "id": pid, "type": "gapit-htmlgraphics-panel", "title": title, "description": desc, "datasource": DS,
        "gridPos": {"h": h, "w": w, "x": x, "y": y},
        "targets": [target("A", flux_rows if flux_rows else flux)],
        "options": {
            "html": html, "css": css, "onInit": "", "onRender": js, "onpanelupdate": "",
            "onInitOnResize": False, "panelupdateOnMount": True,
            "reduceOptions": {"calcs": ["lastNotNull"], "fields": "", "values": False},
            "replaceVariables": True, "renderOnMount": True,
            "dynamicData": False, "dynamicProps": False, "dynamicHtmlGraphics": False,
            "dynamicFieldDisplayValues": False,
            "centerAlignContent": "left", "overflow": "visible",
            "rootCSS": "", "SVGBaseFix": False, "useGrafanaScrollbar": False,
            "importPanelOptions": [],
        },
        "fieldConfig": {"defaults": {}, "overrides": []},
    }


# ---------------------------------------------------------------- B：格子表
B_TABLE_HTML = '<div id="bench"></div>'

B_TABLE_CSS = """
#bench { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#bench .lgd { display:flex; gap:16px; flex-wrap:wrap; font-size:11.5px; color:#8b919c; margin:2px 0 10px 2px; }
#bench .lgd i { display:inline-block; width:14px; height:11px; border-radius:3px; margin-right:5px; vertical-align:-1px; }
#bench table { width:100%; border-collapse:collapse; table-layout:fixed; }
#bench th { color:#8b919c; font-weight:400; font-size:11px; padding:4px 5px; text-align:right; white-space:nowrap; }
#bench th.sc { text-align:left; width:24%; }
#bench th.pg { width:13%; text-align:left; }
#bench td { padding:2px 3px; border-top:1px solid rgba(255,255,255,0.06); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
#bench td.sc { text-align:left; color:inherit; }
#bench td.num { text-align:right; font-variant-numeric:tabular-nums; }
#bench tr.cat td { padding-top:9px; padding-bottom:4px; font-weight:500; letter-spacing:.5px; font-size:11.5px; border-top:none; }
#bench tr.sub td { font-size:11px; color:#8b919c; padding-top:4px; padding-bottom:2px; border-top:none; }
#bench .cell { display:block; padding:4px 5px; border-radius:5px; text-align:right; font-size:11px; font-variant-numeric:tabular-nums; }
#bench .cell.ach { background:#C0DD97; color:#173404; }
#bench .cell.cur { background:#B5D4F4; color:#042C53; font-weight:500; }
#bench .cell.fut { background:rgba(140,140,140,0.16); color:#9aa0a6; }
#bench .bar { position:relative; height:9px; border-radius:5px; background:rgba(140,140,140,0.22); overflow:hidden; }
#bench .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:5px; background:#378ADD; }
#bench .bar i.done { background:#639922; }
#bench .bar i.warn { background:#EF9F27; }
#bench .progwrap { display:flex; align-items:center; gap:7px; }
#bench .progwrap .bar { flex:1; }
#bench .pct { font-size:10px; color:#8b919c; }
#bench .tk { font-size:10.5px; color:#8b919c; margin-left:6px; }
"""

B_TABLE_JS = r"""
(function () {
  var TIERS = ['Lemming','Hare','Ermine','Puffin','Penguin','Fox','Mammoth','Orca','Seal'];
  function parseRows() {
    var out = [];
    var series = (htmlGraphics.data && htmlGraphics.data.series) || [];
    series.forEach(function (fr) {
      (fr.fields || []).forEach(function (f) {
        var isStr = f.type === 'string' || f.name === 'Value' || f.name === '_value' || f.name === 'rowJson';
        if (!isStr) return;
        (f.values || []).forEach(function (v) {
          if (typeof v !== 'string') return;
          try { out.push(JSON.parse(v)); } catch (e) {}
        });
      });
    });
    return out;
  }
  function num(v) {
    if (v === null || v === undefined) return '—';
    var n = Math.round(v * 100) / 100;
    return n.toLocaleString('en-US');
  }
  function build(rows) {
    rows.sort(function (a, b) { return a.ord - b.ord; });
    var h = '<div class="lgd">' +
      '<span><i style="background:#C0DD97"></i>已达档</span>' +
      '<span><i style="background:#B5D4F4"></i>下一档（要攻的这格）</span>' +
      '<span><i style="background:rgba(140,140,140,0.3)"></i>未达</span>' +
      '<span>进度条 = 当前分 ÷ 下一档线</span></div>';
    h += '<table><thead><tr><th class="sc">SCENARIO</th><th class="num" style="width:9%">SCORE</th>' +
         '<th class="pg">进度</th>';
    TIERS.forEach(function (t) { h += '<th>' + t.slice(0, 6).toUpperCase() + '</th>'; });
    h += '</tr></thead><tbody>';
    var lastCat = null, lastSub = null;
    rows.forEach(function (r) {
      if (r.cat !== lastCat) {
        h += '<tr class="cat"><td colspan="12">' + r.cat + '</td></tr>';
        lastCat = r.cat; lastSub = null;
      }
      if (r.sub !== lastSub) {
        var subRows = rows.filter(function (x) { return x.sub === r.sub && x.cat === r.cat; });
        var sidx = TIERS.indexOf(r.subRank);
        h += '<tr class="sub"><td colspan="2">' + r.sub + '</td>';
        h += '<td colspan="9">' + r.subRank +
             (r.subPct !== null && r.subPct !== undefined ? ' · 进度 +' + r.subPct + '%' : '') +
             ' <span class="tk">' + subRows.length + ' 个场景</span></td></tr>';
        lastSub = r.sub;
      }
      var nextLine = r.full ? r.targets[TIERS.length - 1] : r.targets[r.achIdx];
      var ratio = r.full ? 1 : Math.min(1, r.score / nextLine);
      var cls = r.full || ratio >= 0.95 ? 'done' : (ratio >= 0.85 ? 'warn' : '');
      h += '<tr><td class="sc" title="' + r.scenario + '">' + r.scenario + '</td>';
      h += '<td class="num">' + num(r.score) + '<div class="pct">' + r.pct + '% 到下一档</div></td>';
      h += '<td><div class="progwrap"><div class="bar"><i class="' + cls + '" style="width:' +
           (ratio * 100).toFixed(1) + '%"></i></div><span class="pct">' +
           (r.full ? '满' : Math.round(ratio * 100) + '%') + '</span></div></td>';
      r.targets.forEach(function (t, i) {
        var c = i < r.achIdx ? 'ach' : (i === r.achIdx ? 'cur' : 'fut');
        h += '<td><span class="cell ' + c + '">' + num(t) + '</span></td>';
      });
      h += '</tr>';
    });
    return h + '</tbody></table>';
  }
  var rows = parseRows();
  var host = htmlGraphics.htmlNode.getElementById('bench') || htmlGraphics.htmlNode;
  host.innerHTML = rows.length ? build(rows) : '<div style="color:#9aa0a6;padding:8px">暂无数据（先跑 bench_rows.py 物化）</div>';
})();
"""


B_DIST_HTML = '<div id="dist"></div>'

B_DIST_CSS = """
#dist { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#dist .row { display:flex; align-items:center; gap:10px; margin:3px 0; }
#dist .nm { width:78px; color:#8b919c; font-size:11.5px; text-align:right; }
#dist .bar { flex:0 0 auto; height:16px; border-radius:4px; min-width:2px; }
#dist .ct { color:#8b919c; font-size:11px; }
"""

B_DIST_JS = r"""
(function () {
  var TIERS = ['Lemming','Hare','Ermine','Puffin','Penguin','Fox','Mammoth','Orca','Seal'];
  var COLORS = { Lemming:'#E24B4A', Hare:'#EF9F27', Ermine:'#FAC775', Puffin:'#C0DD97',
                 Penguin:'#97C459', Fox:'#1D9E75', Mammoth:'#185FA5', Orca:'#7F77DD',
                 Seal:'#B4B2A9', Unranked:'#D85A30' };
  var rows = [];
  ((htmlGraphics.data && htmlGraphics.data.series) || []).forEach(function (fr) {
    (fr.fields || []).forEach(function (f) {
      var isStr = f.type === 'string' || f.name === 'Value' || f.name === '_value' || f.name === 'rowJson';
      if (!isStr) return;
      (f.values || []).forEach(function (v) {
        if (typeof v !== 'string') return;
        try { rows.push(JSON.parse(v)); } catch (e) {}
      });
    });
  });
  var order = ['Lemming','Hare','Ermine','Puffin','Penguin','Fox','Mammoth','Orca','Seal','Unranked'];
  var cnt = {}; rows.forEach(function (r) { cnt[r.rank] = (cnt[r.rank] || 0) + 1; });
  var max = Math.max.apply(null, [1].concat(order.map(function (t) { return cnt[t] || 0; })));
  var h = '';
  order.forEach(function (t) {
    var c = cnt[t] || 0;
    if (!c && t !== 'Unranked') { return; }
    var w = Math.round(c / max * 320);
    h += '<div class="row"><div class="nm">' + t + '</div>' +
         '<div class="bar" style="width:' + Math.max(w, 2) + 'px;background:' + (COLORS[t] || '#888') + '"></div>' +
         '<div class="ct">' + c + ' 个场景</div></div>';
  });
  var host = htmlGraphics.htmlNode.getElementById('dist') || htmlGraphics.htmlNode;
  host.innerHTML = h || '<div style="color:#9aa0a6">暂无数据</div>';
})();
"""


CARD_HTML = '<div id="card"></div>'
CARD_CSS = """
#card { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; padding: 2px 0 0 2px; }
#card .k { font-size: 12px; color: #8b919c; margin-bottom: 10px; }
#card .v { font-size: 26px; font-weight: 500; line-height: 1.15; }
"""
CARD_JS = r"""
(function () {
  var v = null;
  ((htmlGraphics.data && htmlGraphics.data.series) || []).forEach(function (fr) {
    (fr.fields || []).forEach(function (f) {
      if (f.name === 'Time' || f.name === '_time') return;
      if (v === null && f.values && f.values.length) v = f.values[f.values.length - 1];
    });
  });
  var host = htmlGraphics.htmlNode.getElementById('card') || htmlGraphics.htmlNode;
  host.innerHTML = '<div class="v">' + (v === null || v === undefined ? '—' : v) + '</div>';
})();
"""


def card_panel(pid, label, flux, desc, x=0, y=0, w=6, h=5):
    """统计卡（自绘，用于显示字符串值 —— stat 面板渲染不了字符串字段）"""
    js = CARD_JS.replace("htmlGraphics.options.__label", json.dumps(label, ensure_ascii=False))
    return html_panel(pid, label, flux, desc, CARD_HTML, CARD_CSS, js, x=x, y=y, w=w, h=h)


def build_b():
    meta = lambda f: ('from(bucket: "aim") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) '
                      '|> filter(fn: (r) => r._measurement == "aim_bench_meta" and r._field == "%s") '
                      '|> keep(columns: ["_time", "_value"]) |> last()') % f
    rowsq = ('from(bucket: "aim") |> range(start: v.timeRangeStart, stop: v.timeRangeStop) '
             '|> filter(fn: (r) => r._measurement == "aim_bench_row" and r._field == "rowJson") '
             '|> last() |> keep(columns: ["_time", "_value", "scenario"])')
    panels = [
        stat_panel(600, "当前清单档位", meta("lowestSubIdx"),
                   "4 大类 14 子类中最低的那一档（拿 rank 的卡口）",
                   mappings=[{"type": "value", "options": {str(i): {"text": t, "index": i}
                                                           for i, t in enumerate(TIERS)}}],
                   step_at=1, x=0, y=0),
        card_panel(601, "已上榜", meta("rankedText"),
                   "已拿到至少 Lemming 的场景数 / 总数", x=6, y=0),
        card_panel(602, "卡住的子类", meta("stuckText"),
                   "仍在最低档的子类别（需要优先攻）", x=12, y=0),
        stat_panel(603, "平均离下一档", meta("avgGap"), "39 个场景距各自下一档线的平均差距，越小越接近升档",
                   unit="percent", x=18, y=0),
        html_panel(604, "档位分布", meta("total") + "\n", "每个档位上有多少场景（按场景当前档位统计）",
                   B_DIST_HTML, B_DIST_CSS, B_DIST_JS, y=5, h=9, flux_rows=rowsq),
        html_panel(610, "场景达标线总表（9 档格子填色）", rowsq,
                   "照搬 evxl charts 页：官方 4 大类 / 14 子类分组，每行 9 档达标线；"
                   "已达档=绿格、下一档=蓝格、未达=灰格；进度条=当前分÷下一档线",
                   B_TABLE_HTML, B_TABLE_CSS, B_TABLE_JS, y=14, h=46),
    ]
    dash = {
        "uid": "viscose-s2-easier", "title": "练枪训练 · Viscose S2 Easier",
        "tags": ["aim", "viscose", "list:viscose-s2-easier"], "timezone": "browser",
        "schemaVersion": 39, "version": 1, "refresh": "30s",
        "editable": True, "graphTooltip": 0, "time": {"from": "now-7d", "to": "now"},
        "links": [
            {"title": "← Voltaic Iron", "type": "link", "url": "/d/aim-scenarios-v2", "icon": "external link"},
            {"title": "Aim Lab →", "type": "link", "url": "/d/aimlab", "icon": "external link"},
            {"title": "今日清单 →", "type": "link", "url": "/d/viscose-daylist", "icon": "external link"},
        ],
        "panels": panels,
    }
    return {"annotations": {"list": []}, "editable": True, "graphTooltip": 0, "links": dash["links"],
            "refresh": dash["refresh"], "schemaVersion": 39, "tags": dash["tags"], "time": dash["time"],
            "timezone": "browser", "title": dash["title"], "uid": dash["uid"], "version": 1,
            "panels": panels}


# ---------------------------------------------------------------- D：今日清单
D_PROG_HTML = '<div id="prog"></div>'
D_PROG_CSS = """
#prog { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#prog table { width:100%; border-collapse:collapse; }
#prog th { color:#8b919c; font-weight:400; font-size:11px; padding:4px 6px; text-align:left; }
#prog td { padding:4px 6px; border-top:1px solid rgba(255,255,255,0.06); }
#prog td.num { text-align:right; font-variant-numeric:tabular-nums; }
#prog .chip { display:inline-block; padding:2px 8px; border-radius:7px; font-size:11px; }
#prog .chip.done { background:#27500A; color:#C0DD97; }
#prog .chip.doing { background:#633806; color:#FAC775; }
#prog .chip.none { background:rgba(140,140,140,0.2); color:#9aa0a6; }
#prog .bar { position:relative; height:8px; border-radius:4px; background:rgba(140,140,140,0.22); overflow:hidden; min-width:70px; }
#prog .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:4px; background:#378ADD; }
#prog .bar i.done { background:#639922; }
#prog .bar i.doing { background:#EF9F27; }
"""
D_PROG_JS = r"""
(function () {
  var targets = [], counts = {};
  ((htmlGraphics.data && htmlGraphics.data.series) || []).forEach(function (fr) {
    (fr.fields || []).forEach(function (f) {
      // 字符串字段 = 清单行 JSON
      if (f.type === 'string' || f.name === 'Value' || f.name === '_value' || f.name === 'rowJson') {
        (f.values || []).forEach(function (v) {
          if (typeof v !== 'string') return;
          try { var o = JSON.parse(v); if (o && o.scenario) targets.push(o); } catch (e) {}
        });
      }
      // 数值字段 + scenario 标签 = 当日已打轮数
      if (f.type === 'number' && f.labels && f.labels.scenario) {
        var vals = f.values || [];
        if (vals.length) counts[f.labels.scenario] = vals[vals.length - 1];
      }
    });
  });
  targets.sort(function (a, b) { return a.order - b.order; });
  var h = '<table><thead><tr><th style="width:32px">#</th><th>场景</th><th style="width:58px">角色</th>' +
          '<th style="width:64px">目标分</th><th style="width:60px">门槛</th>' +
          '<th style="width:88px" class="num">已打 / 要求</th><th style="width:120px">进度</th>' +
          '<th style="width:80px">状态</th></tr></thead><tbody>';
  var doneAll = 0;
  targets.forEach(function (t) {
    var done = counts[t.scenario] || 0;
    var ratio = Math.min(1, done / t.rounds);
    var cls = ratio >= 1 ? 'done' : (ratio > 0 ? 'doing' : '');
    var chip = ratio >= 1 ? 'done' : (ratio > 0 ? 'doing' : 'none');
    var txt = ratio >= 1 ? '已完成' : (ratio > 0 ? '进行中' : '未开始');
    if (ratio >= 1) doneAll++;
    h += '<tr><td>' + t.order + '</td><td>' + t.scenario + '</td><td>' + t.role + '</td>' +
         '<td>' + (t.target_score == null ? '—' : t.target_score) + '</td>' +
         '<td>' + (t.target_acc == null ? '—' : t.target_acc + '%') + '</td>' +
         '<td class="num">' + done + ' / ' + t.rounds + '</td>' +
         '<td><div class="bar"><i class="' + cls + '" style="width:' + (ratio * 100).toFixed(1) + '%"></i></div></td>' +
         '<td><span class="chip ' + chip + '">' + txt + '</span></td></tr>';
  });
  h += '</tbody></table>';
  h += '<div style="margin-top:8px;font-size:11.5px;color:#8b919c">已完成 ' + doneAll + ' / ' +
       targets.length + ' 条 · 清单日 ' + (targets[0] ? targets[0].run_date : '') +
       '（' + (targets[0] ? targets[0].daylist + ' · ' + targets[0].label : '') + '）</div>';
  var host = htmlGraphics.htmlNode.getElementById('prog') || htmlGraphics.htmlNode;
  host.innerHTML = targets.length ? h : '<div style="color:#9aa0a6;padding:8px">暂无该清单数据（跑 daylist_sync.py）</div>';
})();
"""

D_CARD_HTML = '<div id="cmp"></div>'
D_CARD_CSS = """
#cmp { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#cmp table { width:100%; border-collapse:collapse; }
#cmp td { padding:4px 6px; border-top:1px solid rgba(255,255,255,0.06); }
#cmp td.num { text-align:right; font-variant-numeric:tabular-nums; }
#cmp .bar { position:relative; height:8px; border-radius:4px; background:rgba(140,140,140,0.22); overflow:hidden; }
#cmp .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:4px; background:#378ADD; }
#cmp .bar i.done { background:#639922; }
#cmp .bar i.warn { background:#EF9F27; }
#cmp .bar i.bad { background:#E24B4A; }
#cmp .rk { font-size:11px; color:#8b919c; margin-bottom:6px; }
"""
D_CARD_JS = r"""
(function () {
  var day = null, bench = null;
  function gulp(o) { if (o && o.scenario) { if (o.role) day = o; else bench = o; } }
  ((htmlGraphics.data && htmlGraphics.data.series) || []).forEach(function (fr) {
    (fr.fields || []).forEach(function (f) {
      if (f.type === 'string' || f.name === 'Value' || f.name === '_value' || f.name === 'rowJson') {
        (f.values || []).forEach(function (v) {
          if (typeof v !== 'string') return;
          try { gulp(JSON.parse(v)); } catch (e) {}
        });
      }
    });
  });
  bench = bench || {};
  day = day || {};
  var score = bench.score, acc = bench.acc;
  var nextLine = (bench.targets && bench.targets.length) ? (bench.full ? bench.targets[bench.targets.length - 1] : bench.targets[bench.achIdx]) : null;
  function row(label, target, cur, isAcc) {
    var unit = isAcc ? '%' : '';
    var ratio = (target && cur != null) ? Math.min(1.05, cur / target) : null;
    var cls = ratio == null ? '' : (ratio >= 1 ? 'done' : (ratio > 0.9 ? 'warn' : 'bad'));
    return '<tr><td style="width:96px">' + label + '</td>' +
           '<td class="num" style="width:74px">' + (target == null ? '—' : target + unit) + '</td>' +
           '<td class="num" style="width:74px">' + (cur == null ? '—' : cur + unit) + '</td>' +
           '<td>' + (ratio == null ? '' : '<div class="bar"><i class="' + cls + '" style="width:' + (ratio * 100).toFixed(1) + '%"></i></div>') + '</td></tr>';
  }
  var h = '<div class="rk">' + (bench.scenario || day.scenario || '') +
          (bench.rank ? ' · 当前档位 ' + bench.rank : '') +
          (bench.subRank && bench.subRank !== '—' ? ' · 子类 ' + bench.subRank : '') + '</div>';
  h += '<table>';
  if (day.target_score != null) h += row('目标分', day.target_score, score, false);
  if (nextLine != null) h += row('下一档线', nextLine, score, false);
  if (day.target_acc != null) h += row('命中率门槛', day.target_acc, acc, true);
  if (day.target_score == null && nextLine == null && day.target_acc == null) {
    h += '<tr><td colspan="4" style="color:#9aa0a6">该场景无目标（热身项）</td></tr>';
  }
  h += '</table><div class="rk" style="margin-top:6px">蓝条=现状 ÷ 目标；绿=达标、橙=接近、红=差距大</div>';
  var host = htmlGraphics.htmlNode.getElementById('cmp') || htmlGraphics.htmlNode;
  host.innerHTML = h;
})();
"""

# 每个场景一张面板：自绘「曲线 + 目标对比卡」（面板级 repeat="scenario"）
D_SCENE_CSS = """
#scene { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#scene .hd { font-size: 12.5px; color:#c7cbd1; margin-bottom:6px; }
#scene .hd .mut { color:#8b919c; font-size:11px; margin-left:6px; }
#scene svg { width:100%; height:132px; display:block; }
#scene table { width:100%; border-collapse:collapse; margin-top:6px; }
#scene td { padding:3px 6px; border-top:1px solid rgba(255,255,255,0.07); }
#scene td.num { text-align:right; font-variant-numeric:tabular-nums; }
#scene .bar { position:relative; height:8px; border-radius:4px; background:rgba(140,140,140,0.22); overflow:hidden; min-width:60px; }
#scene .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:4px; background:#378ADD; }
#scene .bar i.done { background:#639922; }
#scene .bar i.warn { background:#EF9F27; }
#scene .bar i.bad { background:#E24B4A; }
#scene .lg { font-size:10.5px; color:#8b919c; margin-top:4px; }
"""
D_SCENE_JS = r"""
(function () {
  var day = null, bench = null, series = {}, times = {};
  function gulp(o) { if (o && o.scenario) { if (o.role) day = o; else bench = o; } }
  var frames = (htmlGraphics.data && htmlGraphics.data.series) || [];
  frames.forEach(function (fr) {
    var fs = fr.fields || [];
    var tf = null;
    fs.forEach(function (f) { if (f.type === 'time') tf = f; });
    fs.forEach(function (f) {
      if (f.type === 'string' || f.name === 'Value' || f.name === '_value' || f.name === 'rowJson') {
        (f.values || []).forEach(function (v) {
          if (typeof v === 'string') { try { gulp(JSON.parse(v)); } catch (e) {} }
        });
      }
      if (f.type === 'number') {
        var key = (f.labels && f.labels._field) || f.name;
        if (!series[key]) { series[key] = []; times[key] = []; }
        (f.values || []).forEach(function (v, i) {
          if (v == null) return;
          series[key].push(v);
          times[key].push(tf ? tf.values[i] : i);
        });
      }
    });
  });
  function chart() {
    var keys = Object.keys(series).filter(function (k) { return series[k].length; });
    var n = 0;
    keys.forEach(function (k) { n = Math.max(n, series[k].length); });
    if (!n) return '<div style="color:#8aa0a6;font-size:11px;height:132px;display:flex;align-items:center">该场景暂无成绩记录（练完导入后出现）</div>';
    var W = 640, H = 132, PL = 6, PR = 6, PT = 10, PB = 12;
    var all = [];
    keys.forEach(function (k) { all = all.concat(series[k]); });
    var maxV = Math.max.apply(null, all), minV = Math.min.apply(null, all);
    if (maxV === minV) maxV = maxV + 1;
    var yLeft = function (v) { return PT + (H - PT - PB) * (1 - (v - minV) / (maxV - minV)); };
    var yPct = function (v) { return PT + (H - PT - PB) * (1 - v / 100); };
    var x = function (i, len) { return len <= 1 ? W / 2 : PL + (W - PL - PR) * i / (len - 1); };
    var colors = { score: '#378ADD', accuracy: '#EF9F27' };
    var svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none">';
    svg += '<line x1="' + PL + '" y1="' + (H - PB) + '" x2="' + (W - PR) + '" y2="' + (H - PB) + '" stroke="rgba(160,160,160,0.25)"/>';
    keys.forEach(function (k) {
      var yf = (k === 'accuracy') ? yPct : yLeft;
      var pts = series[k].map(function (v, i) { return x(i, series[k].length) + ',' + yf(v); }).join(' ');
      svg += '<polyline fill="none" stroke="' + (colors[k] || '#7F77DD') + '" stroke-width="1.8" points="' + pts + '"/>';
      series[k].forEach(function (v, i) {
        svg += '<circle cx="' + x(i, series[k].length) + '" cy="' + yf(v) + '" r="2.8" fill="' + (colors[k] || '#7F77DD') + '"/>';
      });
    });
    return svg + '</svg>';
  }
  function row(label, target, cur, isAcc) {
    var unit = isAcc ? '%' : '';
    var ratio = (target && cur != null) ? Math.min(1.05, cur / target) : null;
    var cls = ratio == null ? '' : (ratio >= 1 ? 'done' : (ratio > 0.9 ? 'warn' : 'bad'));
    return '<tr><td style="width:92px">' + label + '</td>' +
           '<td class="num" style="width:70px">' + (target == null ? '—' : target + unit) + '</td>' +
           '<td class="num" style="width:70px">' + (cur == null ? '—' : cur + unit) + '</td>' +
           '<td>' + (ratio == null ? '' : '<div class="bar"><i class="' + cls + '" style="width:' + (ratio * 100).toFixed(1) + '%"></i></div>') + '</td></tr>';
  }
  var b = bench || {}, d = day || {};
  var nextLine = (b.targets && b.targets.length) ? (b.full ? b.targets[b.targets.length - 1] : b.targets[b.achIdx]) : null;
  var h = '<div class="hd">' + (b.scenario || d.scenario || '') +
          (b.rank ? '<span class="mut">档位 ' + b.rank + (b.subRank && b.subRank !== '—' ? ' · 子类 ' + b.subRank : '') + '</span>' : '') +
          (d.role ? '<span class="mut">' + d.role + ' · ×' + d.rounds + ' 轮</span>' : '') + '</div>';
  h += chart();
  h += '<table>';
  if (d.target_score != null) h += row('目标分', d.target_score, b.score, false);
  if (nextLine != null) h += row('下一档线', nextLine, b.score, false);
  if (d.target_acc != null) h += row('命中率门槛', d.target_acc, b.acc, true);
  if (d.target_score == null && nextLine == null && d.target_acc == null) {
    h += '<tr><td colspan="4" style="color:#9aa0a6">该场景为热身项，无目标值</td></tr>';
  }
  h += '</table><div class="lg">蓝线=得分 · 橙线=命中率（0–100%）· 蓝条=现状 ÷ 目标</div>';
  var host = htmlGraphics.htmlNode.getElementById('scene') || htmlGraphics.htmlNode;
  host.innerHTML = h;
})();
"""


# 目标对比总表（单面板：每行一个场景，避免插件不支持重复的问题）
D_CMP_HTML = '<div id="cmp2"></div>'
D_CMP_CSS = """
#cmp2 { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 12px; }
#cmp2 table { width:100%; border-collapse:collapse; }
#cmp2 th { color:#8b919c; font-weight:400; font-size:11px; padding:5px 6px; text-align:left; white-space:nowrap; }
#cmp2 td { padding:4px 6px; border-top:1px solid rgba(255,255,255,0.07); white-space:nowrap; }
#cmp2 td.num { text-align:right; font-variant-numeric:tabular-nums; }
#cmp2 .bar { position:relative; height:8px; border-radius:4px; background:rgba(140,140,140,0.22); overflow:hidden; min-width:64px; }
#cmp2 .bar i { position:absolute; left:0; top:0; bottom:0; border-radius:4px; background:#378ADD; }
#cmp2 .bar i.done { background:#639922; }
#cmp2 .bar i.warn { background:#EF9F27; }
#cmp2 .bar i.bad { background:#E24B4A; }
#cmp2 .rk { font-size:11px; color:#8b919c; margin-bottom:6px; }
#cmp2 .pill { display:inline-block; font-size:10.5px; padding:1px 6px; border-radius:5px; background:rgba(140,140,140,0.22); color:#c7cbd1; }
"""
D_CMP_JS = r"""
(function () {
  var items = [], bench = {};
  ((htmlGraphics.data && htmlGraphics.data.series) || []).forEach(function (fr) {
    (fr.fields || []).forEach(function (f) {
      if (f.type !== 'string' && f.name !== 'Value' && f.name !== '_value' && f.name !== 'rowJson') return;
      (f.values || []).forEach(function (v) {
        if (typeof v !== 'string') return;
        var o = null;
        try { o = JSON.parse(v); } catch (e) { return; }
        if (!o || !o.scenario) return;
        if (o.role) items.push(o); else bench[o.scenario] = o;
      });
    });
  });
  items.sort(function (a, b) { return a.order - b.order; });
  function bar(ratio) {
    if (ratio == null) return '';
    var cls = ratio >= 1 ? 'done' : (ratio > 0.9 ? 'warn' : 'bad');
    return '<div class="bar"><i class="' + cls + '" style="width:' + (Math.min(1.05, ratio) * 100).toFixed(1) + '%"></i></div>';
  }
  var h = '<div class="rk">清单日 ' + (items[0] ? items[0].run_date : '') + ' · ' +
          (items[0] ? items[0].daylist + ' ' + items[0].label : '') + ' · 共 ' + items.length + ' 条</div>';
  h += '<table><thead><tr><th style="width:26px">#</th><th>场景</th><th style="width:52px">角色</th>' +
       '<th style="width:66px">目标分</th><th style="width:66px">现状</th><th style="width:110px">达成度</th>' +
       '<th style="width:72px">下一档线</th><th style="width:60px">门槛</th><th style="width:62px">命中率</th>' +
       '<th style="width:110px">达成度</th><th style="width:64px">档位</th></tr></thead><tbody>';
  items.forEach(function (t) {
    var b = bench[t.scenario] || {};
    var nextLine = (b.targets && b.targets.length) ? (b.full ? b.targets[b.targets.length - 1] : b.targets[b.achIdx]) : null;
    var rScore = (t.target_score && b.score != null) ? b.score / t.target_score : null;
    var rAcc = (t.target_acc && b.acc != null) ? b.acc / t.target_acc : null;
    h += '<tr><td>' + t.order + '</td><td>' + t.scenario + '</td><td>' + t.role + '</td>' +
         '<td class="num">' + (t.target_score == null ? '—' : t.target_score) + '</td>' +
         '<td class="num">' + (b.score == null ? '—' : b.score) + '</td><td>' + bar(rScore) + '</td>' +
         '<td class="num">' + (nextLine == null ? '—' : nextLine) + '</td>' +
         '<td class="num">' + (t.target_acc == null ? '—' : t.target_acc + '%') + '</td>' +
         '<td class="num">' + (b.acc == null ? '—' : b.acc + '%') + '</td><td>' + bar(rAcc) + '</td>' +
         '<td><span class="pill">' + (b.rank || '—') + '</span></td></tr>';
  });
  h += '</tbody></table>';
  h += '<div class="rk" style="margin-top:6px">达成度：蓝条 = 现状 ÷ 目标；绿=达标、橙=≥90%、红=差距大。' +
       '下一档线来自榜单（evxl 档位阈值）</div>';
  var host = htmlGraphics.htmlNode.getElementById('cmp2') || htmlGraphics.htmlNode;
  host.innerHTML = items.length ? h : '<div style="color:#9aa0a6;padding:8px">该清单暂无数据</div>';
})();
"""


def influx_csv(flux):
    """直接查 InfluxDB（生成看板时用；失败返回空列表）"""
    import urllib.request, io, csv
    try:
        req = urllib.request.Request("http://127.0.0.1:8087/api/v2/query?org=aim-org",
                                     data=flux.encode("utf-8"), method="POST")
        req.add_header("Authorization", "Token aim-super-secret-token-2026")
        req.add_header("Content-Type", "application/vnd.flux")
        body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:
        return []
    rows, header = [], None
    for line in body.replace(chr(13), "").split(chr(10)):
        if not line or line.startswith("#"):
            continue
        cells = next(csv.reader([line]))
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and (cells[0] == "result" or (len(cells) > 2 and cells[2] == "_time")):
            header = cells
            continue
        if header is None:
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def daylist_scenarios():
    """最新一份每日清单的场景名（按 order）——把多值变量默认设为全选，让面板重复生效"""
    rows = influx_csv('from(bucket: "aim") |> range(start: -1y, stop: 2d) '
                      '|> filter(fn: (r) => r._measurement == "aim_daylist" and r._field == "order") '
                      '|> keep(columns: ["_time", "_value", "scenario"]) |> group() '
                      '|> sort(columns: ["_value"]) |> keep(columns: ["_time", "scenario"])')
    out = []
    for r in rows:
        sc = r.get("scenario")
        if sc and sc not in out:
            out.append(sc)
    return out


def build_d():
    _SC = daylist_scenarios()          # 多值变量默认全选（面板重复需要）
    day_var_flux = ('from(bucket: "aim") |> range(start: -1y, stop: 2d)\n'
                    '  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r._field == "items")\n'
                    '  |> keep(columns: ["_time", "daylist"]) |> sort(columns: ["_time"], desc: true)\n'
                    '  |> rename(columns: {daylist: "_value"}) |> keep(columns: ["_value"])')
    scen_var_flux = ('from(bucket: "aim") |> range(start: -1y, stop: 2d)\n'
                     '  |> filter(fn: (r) => r._measurement == "aim_daylist" and r._field == "order" and r.daylist == "$day")\n'
                     '  |> keep(columns: ["_time", "_value", "scenario"]) |> sort(columns: ["_value"])\n'
                     '  |> map(fn: (r) => ({ r with _value: r.scenario })) |> keep(columns: ["_value"])')
    rundate_var_flux = ('from(bucket: "aim") |> range(start: -1y, stop: 2d)\n'
                        '  |> filter(fn: (r) => r._measurement == "aim_daylist_meta" and r._field == "run_date" and r.daylist == "$day")\n'
                        '  |> keep(columns: ["_time", "_value"])')

    diag = "--diag" in sys.argv
    templating = {"list": [
        {"name": "day", "label": "清单", "type": "query", "datasource": DS, "query": day_var_flux,
         "refresh": 2, "sort": 0, "hide": 0, "includeAll": False, "multi": False,
         "options": [], "current": {}},
        {"name": "scenario", "label": "场景", "type": "query", "datasource": DS, "query": scen_var_flux,
         "refresh": 2, "sort": 0, "hide": 0 if diag else 2, "includeAll": False, "multi": True,
         "options": [], "current": {"selected": True, "text": _SC, "value": _SC}},
        {"name": "rundate", "label": "清单日", "type": "query", "datasource": DS, "query": rundate_var_flux,
         "refresh": 2, "sort": 0, "hide": 0 if diag else 2, "includeAll": False, "multi": False,
         "options": [], "current": {}},
    ]}

    day_json_flux = ('from(bucket: "aim") |> range(start: -1y, stop: 2d)\n'
                     '  |> filter(fn: (r) => r._measurement == "aim_daylist" and r._field == "rowJson" and r.daylist == "$day")\n'
                     '  |> keep(columns: ["_time", "_value"])')
    count_flux = ('_rd = "${rundate}"\n'
                  '_cs = if _rd == "" then v.timeRangeStart else time(v: _rd + "T00:00:00+08:00")\n'
                  '_ce = if _rd == "" then v.timeRangeStop else time(v: _rd + "T23:59:59+08:00")\n'
                  'from(bucket: "aim")\n'
                  '  |> range(start: _cs, stop: _ce)\n'
                  '  |> filter(fn: (r) => r._measurement == "aim_scenario" and r._field == "score" and r.list == "viscose-s2-easier")\n'
                  '  |> group(columns: ["scenario"]) |> count()')

    prog = html_panel(800, "今日清单 · 完成度（要求轮数 vs 已打）", day_json_flux,
                      "数据源：aim_daylist（清单要求）+ aim_scenario（清单日当天实际次数）",
                      D_PROG_HTML, D_PROG_CSS, D_PROG_JS, y=0, h=12)
    prog["targets"].append(target("B", count_flux))

    # ① 目标对比总表（单面板，插件不支持重复，所以做成"每行一个场景"的总表）
    all_day_flux = day_json_flux
    all_bench_flux = ('from(bucket: "aim") |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n'
                      '  |> filter(fn: (r) => r._measurement == "aim_bench_row" and r._field == "rowJson")\n'
                      '  |> last() |> keep(columns: ["_time", "_value", "scenario"])')
    cmp_panel = html_panel(810, "今日清单 · 目标对比（清单目标 vs 现状）", all_day_flux,
                           "每行一个场景：清单目标分 / 下一档线 / 命中率门槛 vs 现状（蓝条=现状÷目标）",
                           D_CMP_HTML, D_CMP_CSS, D_CMP_JS, y=12, h=15)
    cmp_panel["targets"].append(target("B", all_bench_flux))

    # ② 每场景历史曲线（原生 timeseries + 面板重复；插件面板不支持 repeat）
    ts_flux = ('from(bucket: "aim") |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n'
               '  |> filter(fn: (r) => r._measurement == "aim_scenario" and r.scenario == "$scenario"'
               ' and (r._field == "score" or r._field == "accuracy"))\n'
               '  |> keep(columns: ["_time", "_value", "_field"])')
    ts = {
        "id": 830, "type": "timeseries", "title": "$scenario", "datasource": DS,
        "gridPos": {"h": 6, "w": 12, "x": 0, "y": 28},
        "targets": [target("A", ts_flux)],
        "repeat": "scenario", "maxPerRow": 2, "repeatDirection": "h",
        "options": {"legend": {"displayMode": "list", "placement": "bottom", "showLegend": True, "calcs": []},
                    "tooltip": {"mode": "multi", "sort": "none"}},
        "fieldConfig": {"defaults": {
            "custom": {"drawStyle": "line", "lineInterpolation": "linear", "lineWidth": 1.6,
                       "fillOpacity": 0, "showPoints": "always", "pointSize": 4, "spanNulls": True,
                       "axisPlacement": "auto", "scaleDistribution": {"type": "linear"}},
            "color": {"mode": "palette-classic"}, "unit": "short",
            "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}},
            "overrides": [{
                "matcher": {"id": "byName", "options": "accuracy"},
                "properties": [{"id": "custom.axisPlacement", "value": "right"},
                               {"id": "unit", "value": "percent"},
                               {"id": "min", "value": 0}, {"id": "max", "value": 100},
                               {"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}]}]},
    }

    links = [
        {"title": "← Voltaic Iron", "type": "link", "url": "/d/aim-scenarios-v2", "icon": "external link"},
        {"title": "Viscose S2 →", "type": "link", "url": "/d/viscose-s2-easier", "icon": "external link"},
        {"title": "Aim Lab →", "type": "link", "url": "/d/aimlab", "icon": "external link"},
    ]
    return {"editable": True, "graphTooltip": 0, "links": links, "refresh": "30s", "schemaVersion": 39,
            "tags": ["aim", "daylist"], "time": {"from": "now-2d", "to": "now+1d"}, "timezone": "browser",
            "title": "练枪训练 · 今日清单（Day N）", "uid": "viscose-daylist", "version": 1,
            "templating": templating, "annotations": {"list": []}, "panels": [prog, cmp_panel, ts]}


def build_c():
    """看板 C：Aim Lab 三个任务（从看板 A 迁出）"""
    tasks = [("Sixshot", "六目标"), ("Strafetrack", "水平跟枪"), ("Multilinetrace", "多段直线")]
    panels = []
    pid = 700
    y = 0
    for i, (task, cn) in enumerate(tasks):
        flux = ('from(bucket: "aim") |> range(start: v.timeRangeStart, stop: v.timeRangeStop)\n'
                '  |> filter(fn: (r) => r._measurement == "aimlab_task" and r.task == "%s")\n'
                '  |> keep(columns: ["_time", "_value", "_field"])' % task)
        panels.append({
            "id": pid, "type": "timeseries", "title": "%s（%s）· 得分 / 命中率" % (task, cn),
            "description": "来源 Aim Lab Replay（aimlab_task）；蓝=得分（左轴）、橙=命中率（右轴）",
            "datasource": DS, "gridPos": {"h": 8, "w": 12, "x": 0 if i % 2 == 0 else 12, "y": y},
            "targets": [target("A", flux)],
            "options": {"legend": {"displayMode": "list", "placement": "bottom", "showLegend": True, "calcs": []},
                        "tooltip": {"mode": "multi", "sort": "none"}},
            "fieldConfig": {"defaults": {
                "custom": {"drawStyle": "line", "lineInterpolation": "linear", "lineWidth": 1.6,
                           "fillOpacity": 0, "showPoints": "always", "pointSize": 4, "spanNulls": True,
                           "axisPlacement": "auto", "scaleDistribution": {"type": "linear"}},
                "color": {"mode": "palette-classic"}, "unit": "short",
                "thresholds": {"mode": "absolute", "steps": [{"color": "green", "value": None}]}},
                "overrides": [{
                    "matcher": {"id": "byName", "options": "accuracy"},
                    "properties": [{"id": "custom.axisPlacement", "value": "right"},
                                   {"id": "unit", "value": "percent"}, {"id": "min", "value": 0},
                                   {"id": "max", "value": 100},
                                   {"id": "color", "value": {"mode": "fixed", "fixedColor": "orange"}}]}]},
        })
        pid += 1
        if i % 2 == 1:
            y += 8
    links = [
        {"title": "← Voltaic Iron", "type": "link", "url": "/d/aim-scenarios-v2", "icon": "external link"},
        {"title": "Viscose S2 →", "type": "link", "url": "/d/viscose-s2-easier", "icon": "external link"},
        {"title": "今日清单 →", "type": "link", "url": "/d/viscose-daylist", "icon": "external link"},
    ]
    return {"editable": True, "graphTooltip": 0, "links": links, "refresh": "30s", "schemaVersion": 39,
            "tags": ["aim", "aimlab"], "time": {"from": "now-60d", "to": "now"}, "timezone": "browser",
            "title": "练枪训练 · Aim Lab", "uid": "aimlab", "version": 1,
            "annotations": {"list": []}, "panels": panels}


def patch_a():
    """调整看板 A：去掉 Aim Lab 面板、标题加清单名、加互跳链接"""
    path = os.path.join(DASH_DIR, "aim-scenarios.json")
    doc = json.load(open(path, encoding="utf-8"))
    db = doc.get("dashboard", doc)
    before = len(db.get("panels", []))
    db["panels"] = [p for p in db.get("panels", []) if not (400 <= p.get("id", 0) < 410)]
    db["title"] = "练枪训练 · Voltaic Iron"
    db["links"] = [
        {"title": "Viscose S2 →", "type": "link", "url": "/d/viscose-s2-easier", "icon": "external link"},
        {"title": "今日清单 →", "type": "link", "url": "/d/viscose-daylist", "icon": "external link"},
        {"title": "Aim Lab →", "type": "link", "url": "/d/aimlab", "icon": "external link"},
    ]
    if "version" in db:
        db["version"] = db.get("version", 1) + 1
    json.dump(doc, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return before, len(db["panels"])


def main():
    out = {}
    out["viscose-s2-easier.json"] = build_b()
    out["viscose-daylist.json"] = build_d()
    out["aimlab.json"] = build_c()
    if "--check" in sys.argv:
        for name, doc in out.items():
            json.dumps(doc, ensure_ascii=False)
            print(name, "JSON 合法 | 面板数:", len(doc["panels"]))
        return
    if not os.path.isdir(DASH_DIR):
        raise SystemExit("找不到 dashboards 目录: " + DASH_DIR)
    for name, doc in out.items():
        path = os.path.join(DASH_DIR, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=2)
        print("已生成", path, "| 面板数:", len(doc["panels"]))
    b, a = patch_a()
    print("看板 A 已调整：面板 %d → %d（去掉 Aim Lab），标题加清单名，加互跳链接" % (b, a))


if __name__ == "__main__":
    main()
