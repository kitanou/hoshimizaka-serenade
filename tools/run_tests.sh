#!/bin/bash
# Ren'Py の自動テストを、テストケースごとに別プロセスで実行する。
# 注意: 同時実行しないこと。別チェックアウトの renpy テストと競合し、
# セーブ/persistent・GUI の共有でshutdown が止まる（2026-11-09 のハング事故）。
# usage: tools/run_tests.sh [RENPY_SDK_DIR]   （既定: ~/renpy-sdk）
SDK="${1:-$HOME/renpy-sdk}"
PROJ="$(cd "$(dirname "$0")/.." && pwd)/hoshimizaka"
CASES="boot prologue_shots route_misaki route_misaki_bad route_touka route_touka_bad route_normal ui_screens prefs_restore save_load"
fail=0
for c in $CASES; do
  LOG="/tmp/renpy_test_$(basename "$(dirname "$PROJ")")_$c.log"
  timeout 100 "$SDK/renpy.sh" "$PROJ" test "$c" --hide-header --overwrite-screenshots >"$LOG" 2>&1 &
  t=$!
  # テスト完結（Status: 行の出力）後も renpy が shutdown で残り、SIGTERM を無視することがある
  # （macOS GUI 実測 2026-11-09）。timeout の TERM+8s 後にウォッチドッグが该当ケースのみ SIGKILL する。
  # renpy の shutdown は自プロセスグループへ TERM を放つため、watchdog 自身は TERM を無視して生き延びる。
  ( trap '' TERM INT
    i=0
    while [ $i -lt 108 ] && kill -0 $t 2>/dev/null; do sleep 1; i=$((i+1)); done
    pkill -9 -f "$PROJ test $c" 2>/dev/null
    kill -9 $t 2>/dev/null ) &
  w=$!
  wait $t 2>/dev/null
  wait $w 2>/dev/null
  if grep -q "Status: PASSED" "$LOG"; then
    echo "PASS  $c"
  else
    echo "FAIL  $c   (log: $LOG)"; fail=1
  fi
  pkill -9 -f "$PROJ test $c" 2>/dev/null   # このチェックアウトの该当年例のみ後始末
done
exit $fail
