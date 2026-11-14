import os
import csv
from datetime import datetime
from typing import Dict, Any

def export_reports(analysis: Dict[str, Any], output_dir: str = "logcat_reports"):
    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, "logcat_analysis_report.md")
    csv_path = os.path.join(output_dir, "logcat_crash_summary.csv")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📱 Android Logcat 크래시 · ANR 자동 분석 보고서\n\n")
        f.write(f"- **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **총 분석 로그 라인**: {analysis['total_lines']}줄\n")
        f.write(f"- **탐지된 치명적 이슈**: **{analysis['incident_count']}건**\n\n")
        f.write("## 1. 이슈 유형별 집계\n\n| 이슈 유형 | 발생 건수 |\n| :--- | :---: |\n")
        for k, v in analysis["type_counts"].items():
            f.write(f"| `{k}` | **{v}건** |\n")
        f.write("\n## 2. 상세 결함 및 스택 트레이스\n\n")
        for idx, inc in enumerate(analysis["incidents"], start=1):
            f.write(f"### #{idx} [{inc['severity']}] {inc['type']} (Line {inc['line_no']})\n")
            f.write(f"- **발생 시각**: `{inc['timestamp']}` | **PID**: `{inc['pid']}` | **Tag**: `{inc['tag']}`\n")
            f.write("```text\n" + "\n".join(inc["stack_trace"]) + "\n```\n\n")

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["No", "Severity", "Type", "Timestamp", "PID", "Tag", "Line", "Summary"])
        for idx, inc in enumerate(analysis["incidents"], start=1):
            writer.writerow([idx, inc["severity"], inc["type"], inc["timestamp"], inc["pid"], inc["tag"], inc["line_no"], inc["summary"]])

    return md_path, csv_path