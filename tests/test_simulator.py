
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