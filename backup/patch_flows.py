# -*- coding: utf-8 -*-
import json, io, os
base = r"D:\11.project\iwen-codex\codex-list\aim-tracker-docker"
bdir = os.path.join(base, "backup")
flows_path = os.path.join(base, "nodered_data", "flows.json")

def rd(name):
    return io.open(os.path.join(bdir, name), encoding="utf-8").read()

import_main = rd("import_main.js")
influx_fn = rd("influx_fn.js")
import_final = rd("import_final.js")
analyze_fn = rd("analyze_fn.js")
note_fn = rd("note_fn.js")
v3_err = rd("v3_err.js")
weekly_err = rd("weekly_err.js")
analyze_ui = rd("analyze_ui.html")
note_ui = rd("note_ui.html")

d = json.load(io.open(flows_path, encoding="utf-8"))
byid = {n["id"]: n for n in d}
byid["aim-import-main"]["func"] = import_main
byid["aim-influx-fn"]["func"] = influx_fn
byid["aim-import-final"]["func"] = import_final

new_nodes = [
    {"id":"aim-analyze-http","type":"http in","z":"aim-flow","name":"POST /analyze-aim","url":"/analyze-aim","method":"post","upload":False,"swaggerDoc":"","x":120,"y":460,"wires":[["aim-analyze-main"]]},
    {"id":"aim-analyze-main","type":"function","z":"aim-flow","name":"生成训练分析并写 Markdown","func":analyze_fn,"outputs":1,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":340,"y":460,"wires":[["aim-analyze-resp"]]},
    {"id":"aim-analyze-resp","type":"http response","z":"aim-flow","name":"分析响应","statusCode":"200","headers":{"content-type":"application/json"},"x":560,"y":460,"wires":[]},
    {"id":"aim-analyze-ui-http","type":"http in","z":"aim-flow","name":"GET /analyze-aim-ui","url":"/analyze-aim-ui","method":"get","upload":False,"swaggerDoc":"","x":120,"y":560,"wires":[["aim-analyze-ui-template"]]},
    {"id":"aim-analyze-ui-template","type":"template","z":"aim-flow","name":"分析页面","field":"payload","template":analyze_ui,"format":"html","syntax":"mustache","output":"str","x":340,"y":560,"wires":[["aim-analyze-ui-resp"]]},
    {"id":"aim-analyze-ui-resp","type":"http response","z":"aim-flow","name":"分析页面响应","statusCode":"200","headers":{"content-type":"text/html; charset=utf-8"},"x":560,"y":560,"wires":[]},
    {"id":"aim-weekly-cron","type":"inject","z":"aim-flow","name":"周日 09:00 周总结","props":[{"p":"payload"},{"p":"analyzeMode","v":"weekly","vt":"str"}],"repeat":"","crontab":"0 9 * * 0","once":False,"onceDelay":0.1,"topic":"","payload":"","payloadType":"date","x":120,"y":660,"wires":[["aim-weekly-main"]]},
    {"id":"aim-weekly-main","type":"function","z":"aim-flow","name":"周总结生成","func":analyze_fn,"outputs":1,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":340,"y":660,"wires":[["aim-weekly-done"]]},
    {"id":"aim-weekly-done","type":"debug","z":"aim-flow","name":"周总结结果","active":True,"tosidebar":True,"console":False,"tostatus":False,"complete":"payload","targetType":"msg","statusVal":"","statusType":"auto","x":560,"y":660,"wires":[]},
    {"id":"aim-note-http","type":"http in","z":"aim-flow","name":"POST /add-note","url":"/add-note","method":"post","upload":False,"swaggerDoc":"","x":120,"y":760,"wires":[["aim-note-main"]]},
    {"id":"aim-note-main","type":"function","z":"aim-flow","name":"写入感悟","func":note_fn,"outputs":1,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":340,"y":760,"wires":[["aim-note-resp"]]},
    {"id":"aim-note-resp","type":"http response","z":"aim-flow","name":"感悟响应","statusCode":"200","headers":{"content-type":"application/json"},"x":560,"y":760,"wires":[]},
    {"id":"aim-note-ui-http","type":"http in","z":"aim-flow","name":"GET /note-ui","url":"/note-ui","method":"get","upload":False,"swaggerDoc":"","x":120,"y":860,"wires":[["aim-note-ui-template"]]},
    {"id":"aim-note-ui-template","type":"template","z":"aim-flow","name":"感悟页面","field":"payload","template":note_ui,"format":"html","syntax":"mustache","output":"str","x":340,"y":860,"wires":[["aim-note-ui-resp"]]},
    {"id":"aim-note-ui-resp","type":"http response","z":"aim-flow","name":"感悟页面响应","statusCode":"200","headers":{"content-type":"text/html; charset=utf-8"},"x":560,"y":860,"wires":[]},
    {"id":"aim-analyze-catch","type":"catch","z":"aim-flow","name":"分析错误捕获","scope":["aim-analyze-main"],"uncaught":False,"x":560,"y":960,"wires":[["aim-analyze-err"]]},
    {"id":"aim-analyze-err","type":"function","z":"aim-flow","name":"分析错误响应","func":v3_err,"outputs":1,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":760,"y":960,"wires":[["aim-analyze-resp"]]},
    {"id":"aim-note-catch","type":"catch","z":"aim-flow","name":"感悟错误捕获","scope":["aim-note-main"],"uncaught":False,"x":560,"y":1060,"wires":[["aim-note-err"]]},
    {"id":"aim-note-err","type":"function","z":"aim-flow","name":"感悟错误响应","func":v3_err,"outputs":1,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":760,"y":1060,"wires":[["aim-note-resp"]]},
    {"id":"aim-weekly-catch","type":"catch","z":"aim-flow","name":"周总结错误捕获","scope":["aim-weekly-main"],"uncaught":False,"x":560,"y":1160,"wires":[["aim-weekly-err"]]},
    {"id":"aim-weekly-err","type":"function","z":"aim-flow","name":"周总结错误日志","func":weekly_err,"outputs":0,"timeout":"","noerr":0,"initialize":"","finalize":"","libs":[],"x":760,"y":1160,"wires":[]},
]

for idx, n in enumerate(new_nodes):
    if n["id"] in byid:
        for j, old_n in enumerate(d):
            if old_n["id"] == n["id"]:
                d[j] = n
                break
    else:
        d.append(n)

io.open(flows_path, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
print("patched flows.json, total nodes:", len(d))