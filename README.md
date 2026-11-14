# 📱 ADB Logcat Crash & ANR Analyzer

> **Android 디바이스(`adb logcat`) 실시간 크래시 감시 및 대용량 로그 파일 분석을 통해 FATAL EXCEPTION·ANR·OOM·Native Crash를 자동 추출하고 마크다운·CSV 진단 보고서를 생성하는 모바일 QA 자동화 도구**

---

## 📌 프로젝트 개요 (Overview)

* **문제 배경**:
  * 모바일 앱·AOSP 단말 테스트 중 발생하는 크래시나 프리징 현상을 수만 줄의 `logcat` 텍스트에서 수동으로 검색·정리하는 데 많은 시간이 소요됩니다.
  * 장시간 테스트 시 크래시가 발생한 정확한 시점과 직전 동작 로그가 밀려 유실되기 쉽습니다.
* **해결 방안**:
  * 정규식(`threadtime` 포맷) 기반 파서로 로그를 구조화하고, `FATAL EXCEPTION`의 경우 동일 PID·Tag의 후속 에러 스택 트레이스까지 자동으로 묶어 추출합니다.
  * `--watch` 실시간 감시 모드를 통해 크래시 발생 즉시 터미널 경보를 띄우고 직전 30줄의 문맥 로그를 별도 리포트로 자동 저장합니다.
  * 일괄 분석 결과는 **개발팀 공유용 마크다운(`logcat_analysis_report.md`)**과 **이슈 통계·엑셀 분석용 CSV(`logcat_crash_summary.csv`)** 두 가지 포맷으로 동시 생성합니다.

---

## ✨ 주요 기능 (Key Features)

1. **4대 치명적 Android 결함 자동 탐지 및 심각도 분류**
   * `FATAL EXCEPTION` (`P0 Critical` — Java/Kotlin 런타임 예외 및 스택 트레이스 8줄 추출)
   * `ANR in ...` (`P0 Critical` — Application Not Responding 프리징 감지)
   * `Fatal signal / SIGSEGV` (`P0 Critical` — C/C++ 네이티브 계층 크래시 감지)
   * `OutOfMemoryError` (`P1 High` — 힙 메모리 할당 실패 감지)
2. **4가지 실행 모드 지원**
   * **실시간 크래시 감시(`--watch`)**: `adb logcat -v threadtime` 스트림을 상시 감시하다가 치명적 오류 감지 즉시 경보 출력 및 직전 30줄 문맥 로그(`realtime_crash_*.md`) 자동 저장
   * **실시간 단말 덤프 분석(`--adb`)**: USB/Wi-Fi로 연결된 Android 기기에서 `adb logcat -d`를 수집해 전체 요약 분석
   * **저장 파일 분석(`--file`)**: 사전에 덤프된 대용량 로그 텍스트 파일 분석
   * **내장 데모 모드(기본)**: 단말 연결이나 [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools)가 없는 환경에서도 `sample_logcat.txt`를 생성해 즉시 검증 가능
3. **Zero-Dependency 경량 설계**
   * [Python](https://www.python.org/) 3.8+ 표준 라이브러리(`re`, `csv`, `subprocess`, `argparse`, `collections`)만 사용하여 별도 패키지 설치 없이 Windows·macOS·Linux에서 즉시 실행됩니다.

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language**: [Python](https://www.python.org/) 3.8+ (표준 라이브러리 기반)
* **Mobile Diagnostics**: [Android Debug Bridge (adb)](https://developer.android.com/tools/adb)
* **Output Formats**: Markdown Report (`.md`), UTF-8 BOM CSV (`.csv`)

---

## 🚀 빠른 시작 (Quickstart)

```bash
# 1. 샘플 로그(sample_logcat.txt) 기반 데모 실행
python analyzer.py

# 2. 저장된 대용량 logcat 파일 분석
python analyzer.py --file path/to/device_log.txt

# 3. USB 디버깅이 켜진 Android 실기기 전체 덤프 분석 (adb 설치 필요)
python analyzer.py --adb

# 4. 실시간 크래시 감시 모드 (크래시 발생 즉시 경보 및 직전 30줄 자동 저장)
python analyzer.py --watch
```

---

## 📂 폴더 구조 (Directory Structure)

```text
adb-logcat-analyzer/
├── analyzer.py           # CLI 진입점 (--watch / --adb / --file / 데모 모드)
├── logcat_parser.py      # threadtime 정규식 파싱 및 크래시·스택 트레이스 추출 엔진
├── report_generator.py   # 마크다운 보고서 & UTF-8-SIG CSV 요약 리포트 생성기
├── sample_logcat.txt     # 데모 검증용 샘플 Android 로그
└── logcat_reports/       # 생성된 분석 및 실시간 크래시 보고서 폴더
    ├── logcat_analysis_report.md
    ├── logcat_crash_summary.csv
    └── realtime_crash_*.md
```