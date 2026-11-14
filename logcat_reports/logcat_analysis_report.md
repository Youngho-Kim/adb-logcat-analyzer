# 📱 Android Logcat 크래시 · ANR 자동 분석 보고서

- **분석 일시**: 2026-11-15 05:13:23
- **대상 패키지 필터**: `전체 (All Packages)`
- **총 분석 로그 라인**: 13줄
- **탐지된 결함**: 총 **5건** (중복 제거 후 고유 결함 **4종**)

## 1. 이슈 유형별 집계

| 이슈 유형 | 총 발생 건수 |
| :--- | :---: |
| `FATAL_EXCEPTION` | **2건** |
| `ANR` | **1건** |
| `OOM` | **1건** |
| `NATIVE_CRASH` | **1건** |

## 2. 고유 결함 및 스택 트레이스 (중복 그룹핑)

### #1 [P0 (Critical)] FATAL_EXCEPTION — 총 2회 발생
- **최초/최근 시각**: `11-14 14:21:12.884` ~ `11-14 14:21:40.100` | **Tag**: `AndroidRuntime` | **발생 라인**: [3, 7]
```text
FATAL EXCEPTION: main
Process: com.example.app, PID: 2410
java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference
at com.example.app.ui.PaymentActivity.onCheckoutClick(PaymentActivity.java:142)
```

### #2 [P0 (Critical)] ANR — 총 1회 발생
- **최초/최근 시각**: `11-14 14:22:03.410` ~ `11-14 14:22:03.410` | **Tag**: `ActivityManager` | **발생 라인**: [11]
```text
ANR in com.example.app (com.example.app/.ui.ChatActivity)
```

### #3 [P1 (High)] OOM — 총 1회 발생
- **최초/최근 시각**: `11-14 14:22:45.901` ~ `11-14 14:22:45.901` | **Tag**: `art` | **발생 라인**: [12]
```text
java.lang.OutOfMemoryError: Failed to allocate a 33554448 byte allocation
```

### #4 [P0 (Critical)] NATIVE_CRASH — 총 1회 발생
- **최초/최근 시각**: `11-14 14:23:10.015` ~ `11-14 14:23:10.015` | **Tag**: `libc` | **발생 라인**: [13]
```text
Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0 in tid 3240
```

