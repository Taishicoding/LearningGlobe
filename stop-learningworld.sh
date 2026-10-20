#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
USER_ID=$(id -u)
PID_FILE="${TMPDIR:-/tmp}/learningworld-$USER_ID.pid"

if [ ! -f "$PID_FILE" ]; then
  printf 'No LearningWorld launcher server was recorded.\n'
  exit 0
fi

SERVER_PID=$(cat "$PID_FILE")
SERVER_COMMAND=$(ps -p "$SERVER_PID" -o args= 2>/dev/null || true)
case "$SERVER_COMMAND" in
  *"http.server 8000 --bind 127.0.0.1 --directory $PROJECT_DIR"*)
    kill "$SERVER_PID"
    printf 'Stopped LearningWorld.\n'
    ;;
  *)
    printf 'The recorded server is no longer running.\n'
    ;;
esac
rm -f "$PID_FILE"
