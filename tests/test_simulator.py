

import threading
import allure
from src.ecu_simulator import EngineECU
from src.listener import EngineStatusListener

DBC_PATH = "dbc/powertrain.dbc"
CHANNEL = "vcan0"


@allure.epic("CAN Communication")
@allure.feature("Periodic message broadcasting")
@allure.story("Engine ECU sends EngineStatus at 10 Hz")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Cycle time: 20 frames (±2) received over 2 seconds at 10 Hz")
@allure.description(
    "Verifies that the Engine ECU broadcasts the EngineStatus frame at the "
    "DBC-defined cycle time of 100 ms. The listener counts frames over a "
    "2-second window and asserts the count is within tolerance."
)
def test_cycle_time():
    duration_s = 2.0
    expected_frames = 20  # 2 seconds × 10 Hz
    tolerance = 2

    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(duration_s,))
    listener_thread = threading.Thread(target=listener.listen, args=(duration_s,))

    listener_thread.start()
    sender_thread.start()
    sender_thread.join()
    listener_thread.join()

    allure.attach(
        f"Expected: {expected_frames} ± {tolerance}\nReceived: {listener.received_count}",
        name="Frame count summary",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert abs(listener.received_count - expected_frames) <= tolerance, (
        f"Expected ~{expected_frames} frames (±{tolerance}), "
        f"got {listener.received_count}"
    )


@allure.epic("CAN Communication")
@allure.feature("Signal decoding")
@allure.story("EngineSpeed and CoolantTemperature stay within DBC physical range")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Signal range: EngineSpeed [0..8000] rpm, CoolantTemperature [-40..215] °C")
@allure.description(
    "Boundary value analysis. After decoding frames via the DBC file, every "
    "received EngineSpeed and CoolantTemperature value must lie within the "
    "physical range declared in the DBC. Out-of-range values would indicate "
    "encoding/decoding bugs or DBC drift."
)
def test_signal_range():
    duration_s = 1.0
    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(duration_s,))
    listener_thread = threading.Thread(target=listener.listen, args=(duration_s,))

    listener_thread.start()
    sender_thread.start()
    sender_thread.join()
    listener_thread.join()

    assert listener.decoded_signals, "No frames were decoded — sender or listener failed."

    sample_lines = [
        f"frame {i}: rpm={s['EngineSpeed']}, temp={s['CoolantTemperature']}"
        for i, s in enumerate(listener.decoded_signals[:5])
    ]
    allure.attach(
        "\n".join(sample_lines),
        name="First 5 decoded frames",
        attachment_type=allure.attachment_type.TEXT,
    )

    for i, signals in enumerate(listener.decoded_signals):
        rpm = signals["EngineSpeed"]
        temp = signals["CoolantTemperature"]
        assert 0 <= rpm <= 8000, f"Frame {i}: EngineSpeed out of range: {rpm}"
        assert -40 <= temp <= 215, f"Frame {i}: CoolantTemperature out of range: {temp}"


@allure.epic("CAN Communication")
@allure.feature("Diagnostics")
@allure.story("Listener detects missing messages when ECU stops broadcasting")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Timeout detection: no new frames after sender stops at t=0.5 s")
@allure.description(
    "Diagnostic test. The sender broadcasts for 0.5 s then stops; the listener "
    "continues for 2.0 s. We assert (1) the sender produced the expected frame "
    "count before stopping, and (2) the listener received at most 1 stale frame "
    "after that, proving missing-message detection works."
)
def test_missing_message():
    sender_duration_s = 0.5
    listener_duration_s = 2.0
    cycle_time_s = 0.1

    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(sender_duration_s,))
    listener_thread = threading.Thread(target=listener.listen, args=(listener_duration_s,))

    listener_thread.start()
    sender_thread.start()

    sender_thread.join()
    count_after_sender_stops = listener.received_count
    listener_thread.join()
    final_count = listener.received_count

    expected_frames_before_stop = int(sender_duration_s / cycle_time_s)
    new_frames_after_stop = final_count - count_after_sender_stops

    allure.attach(
        f"Frames before sender stop: {count_after_sender_stops} (expected ~{expected_frames_before_stop})\n"
        f"Frames after sender stop:  {new_frames_after_stop} (expected ≤ 1)",
        name="Timeout detection summary",
        attachment_type=allure.attachment_type.TEXT,
    )

    assert count_after_sender_stops >= expected_frames_before_stop - 2, (
        f"Sender too slow: only {count_after_sender_stops} frames before stop, "
        f"expected ~{expected_frames_before_stop}"
    )
    assert new_frames_after_stop <= 1, (
        f"Listener received {new_frames_after_stop} frames AFTER sender stopped "
        f"— missing-message detection failed."
    )