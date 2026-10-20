#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PORT=8000
URL="http://127.0.0.1:$PORT"
USER_ID=$(id -u)
PID_FILE="${TMPDIR:-/tmp}/learningworld-$USER_ID.pid"
LOG_FILE="${TMPDIR:-/tmp}/learningworld-$USER_ID.log"

page_is_learningworld() {
  command -v curl >/dev/null 2>&1 &&
    curl --silent --fail --max-time 1 "$URL/index.html" | grep -q '<title>LearningWorld'
}

open_page() {
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  else
    printf 'LearningWorld is running at %s\n' "$URL"
  fi
}

if page_is_learningworld; then
  open_page
  exit 0
fi

nohup python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$PROJECT_DIR" \
  >"$LOG_FILE" 2>&1 </dev/null &
SERVER_PID=$!
printf '%s\n' "$SERVER_PID" >"$PID_FILE"

attempt=0
while [ "$attempt" -lt 30 ]; do
  if page_is_learningworld; then
    open_page
    exit 0
  fi
  if ! kill -0 "$SERVER_PID" 2>/dev/null; then
    break
  fi
  attempt=$((attempt + 1))
  sleep 0.2
done

rm -f "$PID_FILE"
printf 'Could not start LearningWorld at %s. Check %s for details.\n' "$URL" "$LOG_FILE" >&2
exit 1
