"""Trace 记录模块 — 与 context.HarnessTrace 对齐."""

from harness.runtime.context import HarnessTrace, TraceStep

__all__ = ["HarnessTrace", "TraceStep"]


def new_trace(session_id: str = "", user_id: str = "") -> HarnessTrace:
    trace = HarnessTrace()
    trace.session_id = session_id
    trace.user_id = user_id
    return trace
