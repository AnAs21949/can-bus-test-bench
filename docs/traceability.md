# Traceability Matrix

This document maps each requirement (from JIRA) to its corresponding
automated test and any related defects. Maintained per ISO 26262 /
Automotive SPICE traceability principles.

| Source | Identifier |
|---|---|
| JIRA project | CAN Bus Test Bench (CBTB) |
| Test suite | `tests/test_simulator.py` |
| Last updated | 2026-05-09 |

## Requirements coverage

| Req ID | Requirement | Test ID | Test File | Test Function | Status | Defect |
|---|---|---|---|---|---|---|
| CBTB-5 | EngineStatus shall be transmitted at 100ms cycle time | TC-001 | `tests/test_simulator.py` | `test_cycle_time` | PASSED | — |
| CBTB-8 | EngineStatus signals shall stay within DBC-specified ranges | TC-002 | `tests/test_simulator.py` | `test_signal_range` | PASSED | — |
| CBTB-9 | Listener shall detect timeout when sender stops broadcasting | TC-003 | `tests/test_simulator.py` | `test_missing_message` | PASSED | CBTB-10 (closed) |

## Defects

| Defect ID | Title | Linked Test | Linked Req | Status | Resolution |
|---|---|---|---|---|---|
| CBTB-10 | Listener counted in-flight frames as post-shutdown | TC-003 | CBTB-9 | Closed | Added 1-frame slack tolerance in assertion to absorb thread scheduling jitter |
