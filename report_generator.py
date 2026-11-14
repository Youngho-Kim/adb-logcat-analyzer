import os
import csv
from datetime import datetime
from typing import Dict, Any

def export_reports(analysis: Dict[str, Any], output_dir: str = "logcat_reports"):
    os.makedirs(output_dir, exist_ok=True)
    md_path = os.path.join(output_dir, "logcat_analysis_report.md")
    csv_path = os.path.join(output_dir, "logcat_crash_summary.csv")
    pkg = analysis.get("package_filter") or "전체 (All Packages)"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📱 Android Logcat 크래시 · ANR 자동 분석 보고서\n\n")
        f.write(f"- **분석 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **대상 패키지 필터**: `{pkg}`\n")
        f.write(f"- **총 분석 로그 라인**: {analysis['total_lines']}줄\n")
        f.write(f"- **탐지된 결함**: 총 **{analysis['incident_count']}건** (중복 제거 후 고유 결함 **{analysis['unique_incident_count']}종**)\n\n")
        f.write("## 1. 이슈 유형별 집계\n\n")
        if not analysis["type_counts"]:
            f.write("- 탐지된 치명적 크래시/ANR이 없습니다 (Clean Log).\n\n")
        else:
            f.write("| 이슈 유형 | 총 발생 건수 |\n| :--- | :---: |\n")
            for k, v in analysis["type_counts"].items():
                f.write(f"| `{k}` | **{v}건** |\n")
            f.write("\n")

        f.write("## 2. 고유 결함 및 스택 트레이스 (중복 그룹핑)\n\n")
        for idx, inc in enumerate(analysis["incidents"], start=1):
            f.write(f"### #{idx} [{inc['severity']}] {inc['type']} — 총 {inc['occurrence_count']}회 발생\n")
            f.write(f"- **최초/최근 시각**: `{inc['first_seen']}` ~ `{inc['last_seen']}` | **Tag**: `{inc['tag']}` | **발생 라인**: {inc['lines'][:5]}\n")
            f.write("```text\n" + "\n".join(inc["stack_trace"]) + "\n```\n\n")

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["No", "Severity", "Type", "Occurrences", "FirstSeen", "LastSeen", "Tag", "Lines", "Summary"])
        for idx, inc in enumerate(analysis["incidents"], start=1):
            writer.writerow([
                idx, inc["severity"], inc["type"], inc["occurrence_count"],
                inc["first_seen"], inc["last_seen"], inc["tag"],
                ",".join(map(str, inc["lines"][:5])), inc["summary"]
            ])
    return md_path, csv_path