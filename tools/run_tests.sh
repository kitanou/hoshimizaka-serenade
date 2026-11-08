#!/bin/bash
# Ren'Py の自動テストを、テストケースごとに別プロセスで実行する。
# usage: tools/run_tests.sh [RENPY_SDK_DIR]   （既定: ~/renpy-sdk）
SDK="${1:-$HOME/renpy-sdk}"
PROJ="$(cd "$(dirname "$0")/.." && pwd)/hoshimizaka"
CASES="boot prologue_shots route_misaki route_touka route_normal ui_screens prefs_restore save_load"
fail=0
for c in $CASES; do
  if timeout 100 "$SDK/renpy.sh" "$PROJ" test "$c" --hide-header --overwrite-screenshots >/tmp/renpy_test_$c.log 2>&1; \
     grep -q "Status: PASSED" /tmp/renpy_test_$c.log; then
    echo "PASS  $c"
  else
    echo "FAIL  $c   (log: /tmp/renpy_test_$c.log)"; fail=1
  fi
  pkill -f "renpy-sdk" 2>/dev/null
done
exit $fail
