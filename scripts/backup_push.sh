#!/usr/bin/env bash
# 双远程备份：add -> commit -> push origin(Gitee) -> push github(GitHub) -> 校验 SHA
#
# 用法：
#   bash scripts/backup_push.sh                     # 自动生成提交说明
#   bash scripts/backup_push.sh "feat(x): 说明"      # 指定提交说明
#   bash scripts/backup_push.sh "" --no-commit      # 不提交，只把已有提交推到两边
#
# 退出码：0 = 两边 SHA 一致；1 = 有远程失败或 SHA 不一致

set -uo pipefail

ORIGIN_REMOTE="origin"
ORIGIN_URL="git@gitee.com:PMCN-Phoenix/aim-tracker-docker.git"
GITHUB_REMOTE="github"
GITHUB_URL="git@github.com:PMCN-Phoenix/aimingTrackerDocker.git"
BRANCH="main"

MSG="${1:-}"
NO_COMMIT=0
for arg in "$@"; do
  [ "$arg" = "--no-commit" ] && NO_COMMIT=1
done

cd "$(git rev-parse --show-toplevel)" || { echo "[FAIL] 不在 git 仓库内"; exit 1; }

echo "== 仓库: $(pwd)"

# 1. 确保两个远程都在
ensure_remote() {
  local name="$1" url="$2"
  if git remote get-url "$name" >/dev/null 2>&1; then
    local cur; cur="$(git remote get-url "$name")"
    if [ "$cur" != "$url" ]; then
      echo "[WARN] 远程 $name 当前为 $cur，改为 $url"
      git remote set-url "$name" "$url"
    fi
  else
    echo "[INFO] 添加远程 $name -> $url"
    git remote add "$name" "$url"
  fi
}
ensure_remote "$ORIGIN_REMOTE" "$ORIGIN_URL"
ensure_remote "$GITHUB_REMOTE" "$GITHUB_URL"

# 2. 提交
if [ "$NO_COMMIT" -eq 0 ]; then
  if [ -n "$(git status --porcelain)" ]; then
    [ -z "$MSG" ] && MSG="chore(backup): 同步 $(date '+%Y-%m-%d %H:%M')"
    echo "== 暂存并提交: $MSG"
    git add -A || { echo "[FAIL] git add 失败"; exit 1; }
    git commit -q -m "$MSG" || { echo "[FAIL] git commit 失败"; exit 1; }
  else
    echo "== 工作区干净，无需提交"
  fi
fi

LOCAL_SHA="$(git rev-parse HEAD)"
echo "== 本地 HEAD: $LOCAL_SHA"

# 3. 依次推送两个远程
RC=0
LOG="$(mktemp)"
for r in "$ORIGIN_REMOTE" "$GITHUB_REMOTE"; do
  echo "-- 推送 $r ..."
  if git push "$r" "$BRANCH" >"$LOG" 2>&1; then
    tail -4 "$LOG"
  else
    tail -20 "$LOG"
    echo "[FAIL] 推送到 $r 失败"
    RC=1
  fi
done
rm -f "$LOG"

# 4. 校验两边 SHA 是否与本地一致
echo "-- 校验远程 SHA"
check_sha() {
  local r="$1"
  local remote_sha
  remote_sha="$(git ls-remote "$r" "refs/heads/$BRANCH" 2>/dev/null | awk '{print $1}')"
  if [ "$remote_sha" = "$LOCAL_SHA" ]; then
    echo "   [OK]   $r = $LOCAL_SHA"
  else
    echo "   [FAIL] $r = ${remote_sha:-<空>}  (期望 $LOCAL_SHA)"
    RC=1
  fi
}
check_sha "$ORIGIN_REMOTE"
check_sha "$GITHUB_REMOTE"

if [ "$RC" -eq 0 ]; then
  echo "== 备份完成：Gitee / GitHub 均与本地一致"
else
  echo "== 备份未完成，请检查上方 [FAIL]"
fi
exit "$RC"
