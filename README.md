# LearningWorld

A small, static geography learning page. Each date selects a different country from `countries.json`; the selection is deterministic, so everyone sees the same country on the same date. The current temporary rotation has 195 entries, so it repeats each country's fact after 195 days. The page does not save progress or require an account.

## Start with one click

Python 3 is required. On Windows, double-click `launch-learningworld.bat`. It starts the local server and opens the page in your browser. To stop it, double-click `stop-learningworld.bat`.

On Linux, double-click `launch-learningworld.sh` in this folder. If your file manager asks, choose **Run**. It starts the local server and opens the page in your browser. The server stays available at <http://localhost:8000> until stopped.

To stop the Linux launcher server, run:

```sh
./stop-learningworld.sh
```

## Run from a terminal

From this folder, run:

```sh
./run-local.sh
```

Then open <http://localhost:8000>. Stop the server with `Ctrl+C`.

On Windows, you can also start the server from Command Prompt with `py -3 -m http.server 8000 --bind 127.0.0.1` and stop it with `Ctrl+C`.

You can also run `python3 -m http.server 8000 --bind 127.0.0.1` directly. A local server is needed because the page fetches `countries.json`.

The MapLibre map, font, map tiles, and country flags load from online services, so the demo needs an internet connection. No API key is used. Flags try [FlagCDN](https://flagcdn.com/) first and [FlagsAPI](https://flagsapi.com/) as a fallback; if both are blocked, the page displays a flag emoji.

## Country facts

`countries.json` contains one entry for each of the commonly used 195-country set: 193 UN members plus the Holy See and Palestine. Each entry includes the ISO alpha-2 flag code used by FlagCDN. The country overview source in each record is there for follow-up reading. Facts are short, stable, geography-focused, and paired with a gentle recall question. `build_countries.py` regenerates the JSON from the curated country list.
