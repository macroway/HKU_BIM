#!/usr/bin/env bash
# 最小 Gate 检查：文件存在 + 简单标题计数
# 用法: ./scripts/check-gate.sh <phase> [taskId]
# phase: clarify | prd | ui | tech | code

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PHASE="${1:?phase required: clarify|prd|ui|tech|code}"
TASK_ID="${2:-hku-agent-test}"
STATE="$ROOT/data/state/${TASK_ID}.json"

if [[ ! -f "$STATE" ]]; then
  echo "FAIL: state not found: $STATE"
  exit 1
fi

read_path() {
  python3 -c "
import json, sys
with open('$STATE') as f:
    d = json.load(f)
keys = sys.argv[1].split('.')
v = d
for k in keys:
    v = v[k] if v is not None else None
print(v if v is not None else '')
" "$1" 2>/dev/null || echo ""
}

check_file() {
  local rel="$1"
  local label="$2"
  if [[ -z "$rel" || "$rel" == "null" ]]; then
    echo "FAIL: $label path missing in state"
    return 1
  fi
  if [[ ! -f "$ROOT/$rel" ]]; then
    echo "FAIL: $label not found: $rel"
    return 1
  fi
  echo "OK: $label exists ($rel)"
  return 0
}

count_headings() {
  local file="$1"
  grep -cE '^#{1,3} ' "$ROOT/$file" 2>/dev/null || echo 0
}

FAILED=0

case "$PHASE" in
  clarify)
    REL=$(read_path "artifacts.clarifyReport")
    check_file "$REL" "clarifyReport" || FAILED=1
    if [[ $FAILED -eq 0 ]]; then
      H=$(count_headings "$REL")
      if [[ "$H" -lt 5 ]]; then
        echo "WARN: clarifyReport has few headings ($H), expect ~8 sections"
      else
        echo "OK: clarifyReport structure ($H headings)"
      fi
    fi
    HC=$(read_path "humanConfirmed.clarify")
    [[ "$HC" == "True" || "$HC" == "true" ]] && echo "OK: human confirmed clarify" || echo "PENDING: awaiting humanConfirmed.clarify"
    ;;
  prd)
    REL=$(read_path "artifacts.prd")
    check_file "$REL" "prd" || FAILED=1
    HC=$(read_path "humanConfirmed.prd")
    [[ "$HC" == "True" || "$HC" == "true" ]] && echo "OK: human confirmed prd" || echo "PENDING: awaiting humanConfirmed.prd"
    ;;
  ui)
    check_file "$(read_path artifacts.uiDesignBrief)" "uiDesignBrief" || FAILED=1
    OPTS=$(python3 -c "
import json
with open('$STATE') as f:
    opts = json.load(f)['artifacts'].get('uiOptions') or []
print(len([p for p in opts if p]))
")
    if [[ "$OPTS" -lt 3 ]]; then
      echo "FAIL: uiOptions need 3 files, have $OPTS"
      FAILED=1
    else
      echo "OK: uiOptions count ($OPTS)"
      python3 -c "
import json, os
with open('$STATE') as f:
    for p in json.load(f)['artifacts'].get('uiOptions') or []:
        if p and not os.path.isfile(os.path.join('$ROOT', p)):
            print('FAIL: missing', p); exit(1)
print('OK: all ui option files exist')
" || FAILED=1
    fi
    SEL=$(read_path "artifacts.uiSelected")
    [[ -n "$SEL" && "$SEL" != "null" ]] && echo "OK: uiSelected set" || echo "PENDING: awaiting uiSelected"
    HC=$(read_path "humanConfirmed.ui")
    [[ "$HC" == "True" || "$HC" == "true" ]] && echo "OK: human confirmed ui" || echo "PENDING: awaiting humanConfirmed.ui"
    ;;
  tech)
    REL=$(read_path "artifacts.techPlan")
    check_file "$REL" "techPlan" || FAILED=1
    if [[ $FAILED -eq 0 ]]; then
      if grep -qE '实现计划|Checkpoint|检查点' "$ROOT/$REL" 2>/dev/null; then
        echo "OK: techPlan mentions implementation plan"
      else
        echo "WARN: techPlan may lack 实现计划/checkpoint section"
      fi
    fi
    HC=$(read_path "humanConfirmed.tech")
    [[ "$HC" == "True" || "$HC" == "true" ]] && echo "OK: human confirmed tech" || echo "PENDING: awaiting humanConfirmed.tech"
    ;;
  code)
    CUR=$(read_path "codeCheckpoint.current")
    DONE=$(python3 -c "
import json
with open('$STATE') as f:
    c = json.load(f).get('codeCheckpoint', {})
    print(','.join(c.get('completed') or []))
")
    [[ -n "$CUR" && "$CUR" != "null" ]] && echo "INFO: current checkpoint: $CUR" || echo "PENDING: no current checkpoint"
    [[ -n "$DONE" ]] && echo "INFO: completed: $DONE"
    echo "NOTE: code gate requires tests — run manually per prompts/05"
    ;;
  *)
    echo "Unknown phase: $PHASE"
    exit 1
    ;;
esac

if [[ $FAILED -eq 1 ]]; then
  echo "GATE: FAIL"
  exit 1
fi
echo "GATE: PASS (file checks; human/tests may still pending)"
exit 0
