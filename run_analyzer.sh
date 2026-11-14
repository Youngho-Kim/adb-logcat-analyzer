#!/usr/bin/env bash
cd "$(dirname "$0")"

while true; do
  echo ""
  echo "============================================================"
  echo "📱 [ADB Logcat Analyzer] Mobile QA Diagnostic Launcher"
  echo "============================================================"
  echo "  1. Demo Analysis (Sample Log)"
  echo "  2. Connected Device Log Dump Analysis (--adb)"
  echo "  3. Real-time Crash Watch + Auto Screenshot (--watch)"
  echo "  4. Analyze Specific Log File (--file)"
  echo "  5. Monkey Stress Test + Crash Watch (--monkey)"
  echo "  0. Exit"
  echo "============================================================"
  read -r -p "Select menu (0-5): " choice

  case "$choice" in
    1) python3 analyzer.py ;;
    2)
      read -r -p "Package filter (leave blank for all): " pkg
      if [ -z "$pkg" ]; then python3 analyzer.py --adb; else python3 analyzer.py --adb --package "$pkg"; fi
      ;;
    3)
      read -r -p "Package filter (leave blank for all): " pkg
      if [ -z "$pkg" ]; then python3 analyzer.py --watch; else python3 analyzer.py --watch --package "$pkg"; fi
      ;;
    4)
      read -r -p "Enter log file path: " fpath
      python3 analyzer.py --file "$fpath"
      ;;
    5)
      read -r -p "Target package name (e.g. com.example.app): " pkg
      read -r -p "Event count (default 300): " evts
      evts=${evts:-300}
      python3 analyzer.py --monkey "$pkg" --events "$evts"
      ;;
    0) break ;;
    *) echo "Invalid selection." ;;
  esac
done