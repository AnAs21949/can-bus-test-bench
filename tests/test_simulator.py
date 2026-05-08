
import threading

from src.ecu_simulator import EngineECU
from src.listener import EngineStatusListener


DBC_PATH = "dbc/powertrain.dbc"
CHANNEL = "vcan0"


def test_cycle_time():
    duration_s = 2.0
    expected_frames = 20  # 2 seconds × 10 Hz
    tolerance = 2  # allow ±2 frames 

    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(duration_s,))
    listener_thread = threading.Thread(target=listener.listen, args=(duration_s,))

    listener_thread.start()
    sender_thread.start()

    sender_thread.join()
    listener_thread.join()

    assert abs(listener.received_count - expected_frames) <= tolerance, (
        f"Expected ~{expected_frames} frames (±{tolerance}), "
        f"got {listener.received_count}"
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

    for i, signals in enumerate(listener.decoded_signals):
        rpm = signals["EngineSpeed"]
        temp = signals["CoolantTemperature"]

        assert 0 <= rpm <= 8000, f"Frame {i}: EngineSpeed out of range: {rpm}"
        assert -40 <= temp <= 215, f"Frame {i}: CoolantTemperature out of range: {temp}"




def test_missing_message():
    """Listener should detect message timeout when sender stops broadcasting."""
    sender_duration_s = 0.5
    listener_duration_s = 2.0
    cycle_time_s = 0.1

    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(sender_duration_s,))
    listener_thread = threading.Thread(target=listener.listen, args=(listener_duration_s,))

    listener_thread.start()
    sender_thread.start()

    # Wait for sender to finish, then capture frame count
    sender_thread.join()
    count_after_sender_stops = listener.received_count

    # Wait for listener to finish naturally
    listener_thread.join()
    final_count = listener.received_count

    # Assertion 1: sender broadcast at least a few frames before stopping
    expected_frames_before_stop = int(sender_duration_s / cycle_time_s)
    assert count_after_sender_stops >= expected_frames_before_stop - 2, (
        f"Sender too slow: only {count_after_sender_stops} frames before stop, "
        f"expected ~{expected_frames_before_stop}"
    )

    # Assertion 2: no new frames received after sender stopped
    new_frames_after_stop = final_count - count_after_sender_stops
    assert new_frames_after_stop <= 1, (
        f"Listener received {new_frames_after_stop} frames AFTER sender stopped "
        f"— missing-message detection failed."
    )