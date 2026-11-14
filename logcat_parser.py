import re
from collections import Counter
from typing import List, Dict, Any, Optional

LOGCAT_LINE_RE = re.compile(
    r"^(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+([^:]+):\s*(.*)$"
)

def parse_logcat_lines(lines: List[str], package_filter: Optional[str] = None) -> Dict[str, Any]:
    total_lines = 0
    level_counts = Counter()
    raw_incidents = []
    current_crash = None
    package_pids = set()

    if package_filter:
        for raw in lines:
            m = LOGCAT_LINE_RE.match(raw.rstrip("\r\n"))
            if m and package_filter in m.group(6):
                package_pids.add(m.group(2))

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

        if package_filter and (package_filter not in line and pid not in package_pids):
            if current_crash and tag == current_crash["tag"] and pid == current_crash["pid"] and level == "E":
                pass
            else:
                if current_crash:
                    raw_incidents.append(current_crash)
                    current_crash = None
                continue

        if current_crash and tag == current_crash["tag"] and pid == current_crash["pid"] and level == "E":
            if len(current_crash["stack_trace"]) < 8:
                current_crash["stack_trace"].append(msg)
            continue
        elif current_crash:
            raw_incidents.append(current_crash)
            current_crash = None

        if "FATAL EXCEPTION" in msg:
            current_crash = {
                "type": "FATAL_EXCEPTION", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            }
        elif "ANR in " in msg:
            raw_incidents.append({
                "type": "ANR", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })
        elif "OutOfMemoryError" in msg:
            raw_incidents.append({
                "type": "OOM", "severity": "P1 (High)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })
        elif "Fatal signal" in msg or "SIGSEGV" in msg:
            raw_incidents.append({
                "type": "NATIVE_CRASH", "severity": "P0 (Critical)",
                "timestamp": ts, "pid": pid, "tag": tag, "summary": msg,
                "line_no": idx, "stack_trace": [msg]
            })

    if current_crash:
        raw_incidents.append(current_crash)

    grouped: Dict[tuple, Dict[str, Any]] = {}
    for inc in raw_incidents:
        top_frame = inc["stack_trace"][1] if len(inc["stack_trace"]) > 1 else inc["summary"]
        norm_frame = re.sub(r"PID:\s*\d+", "PID:*", top_frame)
        fingerprint = (inc["type"], inc["summary"], norm_frame)

        if fingerprint not in grouped:
            grouped[fingerprint] = {
                **inc, "occurrence_count": 1,
                "first_seen": inc["timestamp"], "last_seen": inc["timestamp"],
                "lines": [inc["line_no"]]
            }
        else:
            g = grouped[fingerprint]
            g["occurrence_count"] += 1
            g["last_seen"] = inc["timestamp"]
            g["lines"].append(inc["line_no"])

    dedup_incidents = list(grouped.values())
    return {
        "total_lines": total_lines,
        "package_filter": package_filter,
        "level_counts": dict(level_counts),
        "incident_count": len(raw_incidents),
        "unique_incident_count": len(dedup_incidents),
        "type_counts": dict(Counter(i["type"] for i in raw_incidents)),
        "incidents": dedup_incidents
    }