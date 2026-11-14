import os
import time
import threading
import subprocess
import argparse
from datetime import datetime
from collections import deque
from typing import Optional
from logcat_parser import parse_logcat_lines
from report_generator import export_reports

SAMPLE_LOGCAT = """11-14 14:20:01.102  2410  2410 I ActivityManager: Start proc com.example.app for activity
11-14 14:20:05.331  2410  2455 D NetworkMonitor: HTTP 200 OK (42ms)
11-14 14:21:12.884  2410  2410 E AndroidRuntime: FATAL EXCEPTION: main
11-14 14:21:12.884  2410  2410 E AndroidRuntime: Process: com.example.app, PID: 2410
11-14 14:21:12.884  2410  2410 E AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference
11-14 14:21:12.885  2410  2410 E AndroidRuntime:     at com.example.app.ui.PaymentActivity.onCheckoutClick(PaymentActivity.java:142)
11-14 14:21:40.100  2590  2590 E AndroidRuntime: FATAL EXCEPTION: main
11-14 14:21:40.100  2590  2590 E AndroidRuntime: Process: com.example.app, PID: 2590
11-14 14:21:40.100  2590  2590 E AndroidRuntime: java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference
11-14 14:21:40.101  2590  2590 E AndroidRuntime:     at com.example.app.ui.PaymentActivity.onCheckoutClick(PaymentActivity.java:142)
11-14 14:22:03.410  1120  1195 E ActivityManager: ANR in com.example.app (com.example.app/.ui.ChatActivity)
11-14 14:22:45.901  3105  3122 E art     : java.lang.OutOfMemoryError: Failed to allocate a 33554448 byte allocation
11-14 14:23:10.015  3200  3240 F libc    : Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0 in tid 3240
"""

CRITICAL_KEYWORDS = ("FATAL EXCEPTION", "ANR in ", "OutOfMemoryError", "Fatal signal", "SIGSEGV")

def check_adb_device() -> Optional[str]:
    try:
        proc = subprocess.run(["adb", "devices"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        print("❌ 'adb'를 찾을 수 없습니다. Android SDK Platform-Tools 설치 및 PATH 등록 후 다시 시도하세요.")
        return None

    lines = [l.strip() for l in proc.stdout.splitlines()[1:] if l.strip()]
    if not lines:
        print("📱 연결된 기기가 없습니다. USB 케이블을 연결하고 스마트폰에서 [USB 디버깅]을 켜주세요.")
        return None

    for line in lines:
        parts = line.split()
        if len(parts) >= 2:
            serial, state = parts[0], parts[1]
            if state == "device":
                print(f"✅ 연결된 Android 기기 확인: {serial}")
                return serial
            elif state == "unauthorized":
                print(f"⚠️ 기기({serial})가 연결되었으나 [USB 디버깅 허용] 팝업 승인이 필요합니다.")
                return None

    print(f"📱 사용 가능한 기기가 없습니다. (현재 상태: {lines})")
    return None

def capture_adb_screenshot(save_path: str) -> bool:
    try:
        proc = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True, timeout=5)
        if proc.returncode == 0 and proc.stdout.startswith(b"\x89PNG"):
            with open(save_path, "wb") as f:
                f.write(proc.stdout)
            return True
    except Exception:
        pass
    return False

def watch_adb_realtime(out_dir: str, package_filter: Optional[str] = None, stop_event: Optional[threading.Event] = None):
    os.makedirs(out_dir, exist_ok=True)
    proc = subprocess.Popen(
        ["adb", "logcat", "-v", "threadtime"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="ignore", bufsize=1
    )
    print(f"👀 [실시간 감시 중] 패키지 필터: {package_filter or '전체'} (종료: Ctrl+C)\n")
    recent_buffer = deque(maxlen=30)
    crash_count = 0

    try:
        for raw_line in proc.stdout:
            if stop_event and stop_event.is_set():
                break
            line = raw_line.rstrip("\r\n")
            if not line:
                continue
            recent_buffer.append(line)

            if package_filter and package_filter not in line:
                continue

            matched_kw = next((kw for kw in CRITICAL_KEYWORDS if kw in line), None)
            if matched_kw:
                crash_count += 1
                now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                human_time = datetime.now().strftime("%H:%M:%S")
                report_file = os.path.join(out_dir, f"realtime_crash_{now_str}_{crash_count}.md")
                shot_file = os.path.join(out_dir, f"realtime_crash_{now_str}_{crash_count}.png")
                shot_ok = capture_adb_screenshot(shot_file)

                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(f"# 🚨 실시간 크래시 감지 보고서 (#{crash_count})\n\n")
                    f.write(f"- **감지 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **감지 패턴**: `{matched_kw}`\n")
                    f.write(f"- **핵심 로그**: `{line}`\n")
                    if shot_ok:
                        f.write(f"- **당시 화면 캡처**: `{os.path.basename(shot_file)}`\n")
                    f.write("\n## 직전 30줄 문맥 로그 (Context)\n```text\n" + "\n".join(recent_buffer) + "\n```\n")

                print(f"🚨 [{human_time}] 치명적 오류 감지! ({matched_kw})")
                print(f"   └─ 내용: {line[:90]}\n   └─ 리포트 저장: {report_file}")
                if shot_ok:
                    print(f"   └─ 📸 화면 캡처 저장: {shot_file}")
                print()
    except KeyboardInterrupt:
        print(f"\n🛑 실시간 감시를 종료했습니다. (총 {crash_count}건 감지)")
    finally:
        proc.terminate()

def run_monkey_stress(package_name: str, event_count: int, out_dir: str):
    if not check_adb_device():
        return
    print(f"🐒 [Monkey 스트레스 테스트 시작] 대상: {package_name} | 이벤트 수: {event_count}회")
    stop_event = threading.Event()
    watcher = threading.Thread(target=watch_adb_realtime, args=(out_dir, package_name, stop_event), daemon=True)
    watcher.start()
    time.sleep(1.0)
    subprocess.run(["adb", "shell", "monkey", "-p", package_name, "-v", str(event_count)], check=False)
    time.sleep(1.5)
    stop_event.set()
    print(f"\n🎉 [Monkey 테스트 완료] {package_name} 대상 {event_count}회 이벤트 수행이 종료되었습니다.")

def main():
    parser = argparse.ArgumentParser(description="Android ADB Logcat Crash & ANR Analyzer")
    parser.add_argument("--file", type=str, default=None, help="분석할 logcat 텍스트 파일 경로")
    parser.add_argument("--adb", action="store_true", help="연결된 Android 단말의 logcat을 덤프해 분석")
    parser.add_argument("--watch", action="store_true", help="실시간 감시 + 크래시 시 화면 자동 스크린샷")
    parser.add_argument("--monkey", type=str, default=None, help="Monkey 스트레스 테스트를 수행할 패키지명")
    parser.add_argument("--events", type=int, default=300, help="Monkey 테스트 이벤트 횟수 (기본: 300)")
    parser.add_argument("--package", type=str, default=None, help="특정 앱 패키지명 필터링")
    parser.add_argument("--out", type=str, default="logcat_reports", help="결과 보고서 저장 폴더")
    args = parser.parse_args()

    print("=" * 65)
    print("📱 [ADB Logcat Analyzer] 모바일 앱 크래시 · ANR 자동 분석기")
    print("=" * 65)

    if args.monkey:
        run_monkey_stress(args.monkey, args.events, args.out)
        return

    if args.watch:
        if check_adb_device():
            watch_adb_realtime(args.out, args.package)
        return

    if args.adb:
        if not check_adb_device():
            return
        proc = subprocess.run(["adb", "logcat", "-d"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
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

    analysis = parse_logcat_lines(lines, package_filter=args.package)
    md_path, csv_path = export_reports(analysis, args.out)
    print(f"📊 분석 완료: 총 {analysis['total_lines']}줄 | 총 결함 {analysis['incident_count']}건 (고유 결함 {analysis['unique_incident_count']}종)")
    print(f"📄 마크다운 보고서: {md_path}\n📊 CSV 요약 파일 : {csv_path}")

if __name__ == "__main__":
    main()