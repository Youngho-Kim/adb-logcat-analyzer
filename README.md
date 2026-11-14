# 📱 ADB Logcat Crash & ANR Analyzer

> **Android 디바이스 실시간 크래시 감시(자동 스크린샷), Monkey 무인 스트레스 테스트, 중복 크래시 그룹핑, 대용량 로그 분석을 원클릭으로 수행하는 모바일 QA 진단 도구**

---

## 📌 프로젝트 개요 (Overview)

* **문제 배경**:
  * 모바일 앱·AOSP 단말 테스트 중 수만 줄의 `logcat` 로그에서 크래시와 스택 트레이스를 수동으로 찾는 데 많은 시간이 소요됩니다.
  * 동일 결함이 반복 발생하면 리포트가 비대해지고, 장시간 테스트 시 크래시 발생 순간의 화면과 직전 동작 로그를 놓치기 쉽습니다.
* **해결 방안**:
  * **기기 상태 사전 검증 (`check_adb_device`)**: 실행 전 `adb` 설치 여부, USB 연결, 디버깅 승인(`unauthorized`) 상태를 먼저 확인해 명확한 안내를 제공합니다.
  * **실시간 감시 & 자동 스크린샷 (`--watch`)**: 크래시 패턴 감지 즉시 터미널 경보를 울리고 `adb exec-out screencap -p`로 당시 폰 화면 PNG와 직전 30줄 문맥 로그를 자동 저장합니다.
  * **Monkey 스트레스 테스트 연동 (`--monkey`)**: 무작위 터치·이벤트 스트레스 테스트와 실시간 크래시 감시를 백그라운드에서 동시 수행해 앱 안정성을 검증합니다.
  * **중복 크래시 그룹핑 & 패키지 필터 (`--package`)**: 예외·스택 지문 기준으로 동일 크래시 발생 횟수를 묶어 집계하고, 특정 앱 패키지만 필터링해 분석합니다.

---

## 🎯 상황별 사용 가이드 (`run_analyzer.bat` / `run_analyzer.sh` 기준)

| 이런 상황일 때 | 선택 메뉴 | 동작 방식 및 생성 결과 |
| :--- | :---: | :--- |
| **폰 없이 프로그램 동작만 빠르게 확인하고 싶을 때** | **1번** (`Demo`) | 내장 샘플 로그(`sample_logcat.txt`)를 분석해 중복 크래시 그룹핑 및 보고서 생성 테스트 |
| **테스트 중 앱이 이미 튕긴 뒤, 전체 로그 통계를 뽑고 싶을 때** | **2번** (`--adb`) | 연결된 폰의 `adb logcat -d`를 한 번에 덤프해 중복 제거된 마크다운 + CSV 리포트 생성 |
| **직접 폰을 만지며 테스트하다가 크래시 순간을 바로 잡고 싶을 때** | **3번** (`--watch`) | 켜두고 테스트하면 크래시 즉시 터미널 경보 + 당시 폰 화면(`.png`) + 직전 30줄 문맥(`.md`) 자동 저장 |
| **이미 저장해 둔 대용량 로그 파일(`.txt`)이 있을 때** | **4번** (`--file`) | 지정한 로그 파일을 파싱해 치명적 결함과 스택 트레이스만 추출·요약 |
| **손으로 만지지 않고 앱을 무작위 터치해 안정성을 시험할 때** | **5번** (`--monkey`) | PC가 폰 화면을 자동으로 수백 회 터치(`monkey`)하면서 크래시 발생 시 자동 경보·캡처·로그 저장 |

---

## ✨ 주요 기능 (Key Features)

1. **4대 치명적 Android 결함 탐지 & 중복 그룹핑**
   * `FATAL EXCEPTION` (`P0 Critical`), `ANR in ...` (`P0 Critical`), `Fatal signal / SIGSEGV` (`P0 Critical`), `OutOfMemoryError` (`P1 High`)
   * 동일 스택 프레임에서 반복 발생한 크래시는 1건의 고유 결함으로 묶고 총 발생 횟수 및 최초·최근 시각을 기록합니다.
2. **Zero-Dependency 설계**
   * [Python](https://www.python.org/) 3.8+ 표준 라이브러리만 사용하여 별도 `pip install` 없이 즉시 실행됩니다. (실기기 연동 시 [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) 필요)

---

## 🛠️ 기술 스택 (Tech Stack)

* **Language**: [Python](https://www.python.org/) 3.8+ (`re`, `csv`, `subprocess`, `threading`, `collections`, `argparse`)
* **Mobile Diagnostics**: [Android Debug Bridge (adb)](https://developer.android.com/tools/adb), Android `monkey`
* **Launchers & Outputs**: Windows Batch (`.bat`), Bash (`.sh`), Markdown (`.md`), UTF-8 BOM CSV (`.csv`), PNG

---

## 🚀 빠른 시작 (Quickstart)

### 원클릭 메뉴 런처 실행
* **Windows 11**: `run_analyzer.bat` 더블 클릭 후 위 상황별 표에 맞춰 `1~5` 선택
* **macOS / Linux**:
  ```bash
  bash run_analyzer.sh
  ```

### CLI 직접 실행 예시
```bash
# 1. 샘플 로그 데모 실행 (중복 그룹핑 확인)
python analyzer.py

# 2. 특정 앱 패키지 필터링 후 실시간 감시 + 크래시 시 자동 캡처
python analyzer.py --watch --package com.example.app

# 3. Monkey 무인 스트레스 테스트 500회 + 실시간 크래시 감시
python analyzer.py --monkey com.example.app --events 500

# 4. 저장된 로그 파일 분석
python analyzer.py --file device_log.txt --package com.example.app
```

---

## 📂 폴더 구조 (Directory Structure)

```text
adb-logcat-analyzer/
├── analyzer.py           # CLI 진입점 (기기확인 · 실시간 감시 · 스크린샷 · Monkey)
├── logcat_parser.py      # threadtime 정규식 파싱 · 패키지 필터 · 중복 크래시 그룹핑
├── report_generator.py   # 마크다운 보고서 & UTF-8-SIG CSV 요약 생성기
├── run_analyzer.bat      # Windows 원클릭 대화형 런처
├── run_analyzer.sh       # macOS/Linux 대화형 런처
├── sample_logcat.txt     # 데모 검증용 샘플 로그
└── logcat_reports/       # 분석 보고서, CSV, 실시간 크래시 문맥 & PNG 스크린샷
```