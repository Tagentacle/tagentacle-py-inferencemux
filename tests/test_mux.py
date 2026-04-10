"""Tests for InferenceMux."""

import asyncio

import pytest

from tagentacle_py_inferencemux import InferenceMux, MuxState, TriggerSignal


@pytest.fixture
def mux():
    return InferenceMux()


def test_initial_state(mux):
    assert mux.state == MuxState.IDLE
    assert mux.has_followup is False


@pytest.mark.asyncio
async def test_trigger_idle_to_busy(mux):
    await mux.trigger(TriggerSignal(topic="/chat/input"))
    assert mux.state == MuxState.BUSY


@pytest.mark.asyncio
async def test_release_returns_to_idle(mux):
    await mux.trigger(TriggerSignal(topic="/chat/input"))
    assert mux.state == MuxState.BUSY
    mux.release()
    assert mux.state == MuxState.IDLE


@pytest.mark.asyncio
async def test_trigger_while_busy_queues_followup(mux):
    await mux.trigger(TriggerSignal(topic="/a"))
    assert mux.state == MuxState.BUSY

    await mux.trigger(TriggerSignal(topic="/b"))
    assert mux.has_followup is True
    assert mux.state == MuxState.BUSY


@pytest.mark.asyncio
async def test_release_with_followup_retriggers(mux):
    await mux.trigger(TriggerSignal(topic="/a"))
    await mux.trigger(TriggerSignal(topic="/b"))

    # Release from /a — /b followup auto-triggers, stays BUSY
    mux.release()
    assert mux.state == MuxState.BUSY

    # Release from /b — no more followups, goes IDLE
    mux.release()
    assert mux.state == MuxState.IDLE


@pytest.mark.asyncio
async def test_wait_returns_on_trigger(mux):
    async def trigger_later():
        await asyncio.sleep(0.01)
        await mux.trigger(TriggerSignal(topic="/test"))

    asyncio.create_task(trigger_later())
    signal = await asyncio.wait_for(mux.wait(), timeout=1.0)
    assert mux.state == MuxState.BUSY
    assert signal.topic == "/test"


@pytest.mark.asyncio
async def test_full_cycle(mux):
    """Simulate: trigger → process → release → trigger again."""
    await mux.trigger(TriggerSignal(topic="/msg1"))
    assert mux.state == MuxState.BUSY

    # Simulate processing
    mux.release()
    assert mux.state == MuxState.IDLE

    # Second trigger
    await mux.trigger(TriggerSignal(topic="/msg2"))
    assert mux.state == MuxState.BUSY
    mux.release()
    assert mux.state == MuxState.IDLE
