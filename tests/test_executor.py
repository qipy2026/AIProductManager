"""Harness Executor 单元测试 — Step Limiter."""

from harness.runtime.context import HarnessContext
from harness.runtime.executor import ExecutorConfig, HarnessExecutor


def test_step_limiter_terminates_at_max_steps():
    config = ExecutorConfig(max_steps=2, fallback_message="step limit")
    executor = HarnessExecutor(config)
    ctx = HarnessContext(message="test")

    def step(_ctx):
        _ctx.response = "partial"
        return _ctx

    result = executor.run_chain(ctx, [step, step, step])
    assert result.terminated is True
    assert result.termination_reason == "max_steps_exceeded"
    assert result.steps_executed == 2
    assert result.context.response == "step limit"


def test_executor_stops_on_blocked():
    executor = HarnessExecutor(ExecutorConfig(max_steps=10))

    def block_step(ctx):
        ctx.blocked = True
        ctx.response = "blocked"
        return ctx

    def never(ctx):
        ctx.response = "should not run"
        return ctx

    result = executor.run_chain(
        HarnessContext(message="x"), [block_step, never], step_names=["a", "b"]
    )
    assert result.terminated is True
    assert result.termination_reason == "blocked"
    assert result.steps_executed == 1


def test_retry_succeeds_on_second_attempt():
    executor = HarnessExecutor()
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("fail")
        return "ok"

    ok, value = executor.retry(flaky, max_attempts=3)
    assert ok is True
    assert value == "ok"
