# 📱 Android Logcat 크래시 · ANR 자동 분석 보고서

- **분석 일시**: 2026-11-14 22:57:46
- **총 분석 로그 라인**: 9줄
- **탐지된 치명적 이슈**: **4건**

## 1. 이슈 유형별 집계

| 이슈 유형 | 발생 건수 |
| :--- | :---: |
| `FATAL_EXCEPTION` | **1건** |
| `ANR` | **1건** |
| `OOM` | **1건** |
| `NATIVE_CRASH` | **1건** |

## 2. 상세 결함 및 스택 트레이스

### #1 [P0 (Critical)] FATAL_EXCEPTION (Line 3)
- **발생 시각**: `11-14 14:21:12.884` | **PID**: `2410` | **Tag**: `AndroidRuntime`
```text
FATAL EXCEPTION: main
Process: com.example.app, PID: 2410
java.lang.NullPointerException: Attempt to invoke virtual method on a null object reference
at com.example.app.ui.PaymentActivity.onCheckoutClick(PaymentActivity.java:142)
```

### #2 [P0 (Critical)] ANR (Line 7)
- **발생 시각**: `11-14 14:22:03.410` | **PID**: `1120` | **Tag**: `ActivityManager`
```text
ANR in com.example.app (com.example.app/.ui.ChatActivity)
```

### #3 [P1 (High)] OOM (Line 8)
- **발생 시각**: `11-14 14:22:45.901` | **PID**: `3105` | **Tag**: `art`
```text
java.lang.OutOfMemoryError: Failed to allocate a 33554448 byte allocation
```

### #4 [P0 (Critical)] NATIVE_CRASH (Line 9)
- **발생 시각**: `11-14 14:23:10.015` | **PID**: `3200` | **Tag**: `libc`
```text
Fatal signal 11 (SIGSEGV), code 1 (SEGV_MAPERR), fault addr 0x0 in tid 3240
```

