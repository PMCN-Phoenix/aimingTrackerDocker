$py = "D:\6_code\13_python\1_python3.11.0\python.exe"
$out = "D:\11.project\iwen-codex\codex-list\aim-tracker-docker\docs\问题库\Q009-练枪与上分匹配安排\子问题\Q009.1-休息日精神状态恢复\YouTube原始数据"
$videos = @(
  @{id="VARQNEdQYbw"; name="viscose_new_best_way_to_train_aim"},
  @{id="ZEH4CfytNyo"; name="lg56_vdim"},
  @{id="jqONINYF17M"; name="hg_burnout_dont_know"},
  @{id="mUXmmHoOt04"; name="eathlete_gaming_fatigue"},
  @{id="JaRGJVrJBQ8"; name="huberman_sleep_essentials"},
  @{id="hEypv90GzDE"; name="huberman_20min_nsdr"},
  @{id="dV-HOC5fbHU"; name="eathlete_ronrambo_aim_fast"},
  @{id="xcjNZsFM4es"; name="sammartin_bounce_back_bad_game"},
  @{id="3BCfDHYRWYc"; name="joshbrett_elite_recovery"},
  @{id="qoR72-aM4mI"; name="hg_brain_fog"}
)
foreach ($v in $videos) {
  Write-Host "=== Fetching $($v.name) ($($v.id)) ==="
  & $py -m yt_dlp --no-update --proxy "http://127.0.0.1:7892" `
    --write-subs --write-auto-subs --sub-langs "en.*" `
    --skip-download --sleep-subtitles 2 `
    --output "$out\$($v.name)." "https://www.youtube.com/watch?v=$($v.id)" 2>&1 | Select-String -Pattern "writing|Destination|error|429|warning" | Select-Object -First 5
  Start-Sleep -Seconds 4
}
Write-Host "=== DONE ==="
Get-ChildItem $out -Filter *.vtt | Select-Object Name, Length
