import re
from collections import Counter
from typing import List, Dict, Any

LOGCAT_LINE_RE = re.compile(
    r"^(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+([^:]+):\s*(.*)$"
)

def parse_logcat_lines(lines: List[str]) -> Dict[str, Any]:
    total_lines = 0
    level_counts = Counter()
    incidents = []
    current_crash = None

    for idx, raw in enumerate(lines, start=1):
        line = raw.rstrip("\r\n")
        if not line.strip():
            continue
        total_lines += 1

        match = LOGCAT_LINE_RE.match(line)
        if match:
            ts, pid, tid, level, tag, msg = match.groups()
            tag = tag.strip()
            level_counts[level] += 1
        else:
            ts, pid, level, tag, msg = "", "", "I", "Raw", line

        if current_crash and tag == current_crash["tag"] and pid == current_crash["pid"] and level == "E":
            if len(current_crash["stack_trace"]) < 8:
                current_crash["stack_trace"].append(msg)
            continue
        elif current_crash:
            incidents.append(current_crash)
            current_crash = None

        if "FATAL EXCEPTION" in msg:
            current_crash = {
                "type": "FATAL_EXCEPTION", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            }
        elif "ANR in " in msg:
            incidents.append({
                "type": "ANR", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })
        elif "OutOfMemoryError" in msg:
            incidents.append({
                "type": "OOM", "severity": "P1 (High)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })
        elif "Fatal signal" in msg or "SIGSEGV" in msg:
            incidents.append({
                "type": "NATIVE_CRASH", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })

    if current_crash:
        incidents.append(current_crash)

    return {
        "total_lines": total_lines,
        "level_counts": dict(level_counts),
        "incident_count": len(incidents),
        "type_counts": dict(Counter(i["type"] for i in incidents)),
        "incidents": incidents
    }