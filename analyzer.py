import os
import subprocess
import argparse
from datetime import datetime
from collections import deque
from logcat_parser import parse_logcat_lines
from report_generator import export_reports

SAMPLE_LOGCAT = """11-14 14:20:01.102  2410  2410 I ActivityManager: Start proc com.example.app for activity
11-14 14:20:05.331  2410  2455 D NetworkMonitor: HTTP 200 OK (42ms)
11-14 14:21:12.884  2410  2410 E AndroidRuntime: FATAL EXCEPTION: main
11-14 14:21:12.884  2410  2410 E AndroidRuntime: Process: com.example.app, PID: 2410
11-14 14:21:12.884  2410  2410 E AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference
11-14 14:21:12.885  2410  2410 E AndroidRuntime:     at com.example.app.ui.PaymentActivity.onCheckoutClick(PaymentActivity.java:142)
11-14 14:22:03.410  1120  1195 E ActivityManager: ANR in com.example.app (com.example.app/.ui.ChatActivity)
11-14 14:22:45.901  3105  3122 E art     : java.lang.OutOfMemoryError: Failed to allocate a 33554448 byte allocation
11-14 14:23:10.015  3200  3240 F libc    : Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0 in tid 3240
"""

CRITICAL_KEYWORDS = ("FATAL EXCEPTION", "ANR in ", "OutOfMemoryError", "Fatal signal", "SIGSEGV")

def watch_adb_realtime(out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    try:
        proc = subprocess.Popen(
            ["adb", "logcat", "-v", "threadtime"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1
        )
    except FileNotFoundError:
        print("❌ 'adb'를 찾을 수 없습니다. Android SDK Platform-Tools 설치 및 PATH 등록 후 다시 시도하세요.")
        return

    print("👀 [실시간 감시 중] Android 단말의 크래시/ANR을 기다리고 있습니다... (종료: Ctrl+C)\n")
    recent_buffer = deque(maxlen=30)
    crash_count = 0

    try:
        for raw_line in proc.stdout:
            line = raw_line.rstrip("\r\n")
            if not line:
                continue
            recent_buffer.append(line)

            matched_kw = next((kw for kw in CRITICAL_KEYWORDS if kw in line), None)
            if matched_kw:
                crash_count += 1
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                human_time = datetime.now().strftime("%H:%M:%S")
                report_file = os.path.join(out_dir, f"realtime_crash_{now_str}_{crash_count}.md")

                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(f"# 🚨 실시간 크래시 감지 보고서 (#{crash_count})\n\n")
                    f.write(f"- **감지 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **감지 패턴**: `{matched_kw}`\n")
                    f.write(f"- **핵심 로그**: `{line}`\n\n")
                    f.write("## 직전 30줄 문맥 로그 (Context)\n```text\n")
                    f.write("\n".join(recent_buffer) + "\n```\n")

                print(f"🚨 [{human_time}] 치명적 오류 감지! ({matched_kw})")
                print(f"   └─ 내용: {line[:90]}")
                print(f"   └─ 자동 저장: {report_file}\n")
    except KeyboardInterrupt:
        print(f"\n🛑 실시간 감시를 종료했습니다. (총 {crash_count}건 감지)")
    finally:
        proc.terminate()

def main():
    parser = argparse.ArgumentParser(description="Android ADB Logcat Crash & ANR Analyzer")
    parser.add_argument("--file", type=str, default=None, help="분석할 logcat 텍스트 파일 경로")
    parser.add_argument("--adb", action="store_true", help="연결된 Android 단말에서 'adb logcat -d'를 직접 수집해 분석")
    parser.add_argument("--watch", action="store_true", help="실시간으로 adb logcat을 감시하며 크래시 발생 즉시 경보 및 저장")
    parser.add_argument("--out", type=str, default="logcat_reports", help="결과 보고서 저장 폴더")
    args = parser.parse_args()

    print("=" * 65)
    print("📱 [ADB Logcat Analyzer] 모바일 앱 크래시 · ANR 자동 분석기")
    print("=" * 65)

    if args.watch:
        watch_adb_realtime(args.out)
        return

    if args.adb:
        try:
            proc = subprocess.run(["adb", "logcat", "-d"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
        except FileNotFoundError:
            print("❌ 'adb'를 찾을 수 없습니다. Android SDK Platform-Tools 설치 및 PATH 등록 후 다시 시도하거나 '--file' 옵션을 사용해 주세요.")
            return
        if proc.returncode != 0:
            print(f"❌ adb 실행 실패: {proc.stderr.strip()}")
            return
        lines = proc.stdout.splitlines()
    elif args.file:
        if not os.path.exists(args.file):
            print(f"❌ 파일을 찾을 수 없습니다: {args.file}")
            return
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    else:
        print("🧪 샘플 Android logcat 데이터를 생성해 데모 분석을 실행합니다...")
        with open("sample_logcat.txt", "w", encoding="utf-8") as f:
            f.write(SAMPLE_LOGCAT)
        lines = SAMPLE_LOGCAT.splitlines()

    analysis = parse_logcat_lines(lines)
    md_path, csv_path = export_reports(analysis, args.out)
    print(f"📊 분석 완료: 총 {analysis['total_lines']}줄 중 치명적 이슈 {analysis['incident_count']}건 탐지")
    print(f"📄 마크다운 보고서: {md_path}\n📊 CSV 요약 파일 : {csv_path}")

if __name__ == "__main__":
    main()