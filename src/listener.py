
import threading
import time

import can
import cantools


class EngineStatusListener:
    """Listens on a virtual CAN bus and decodes EngineStatus frames."""

    def __init__(self, dbc_path: str, channel: str = "vcan0"):
        self.db = cantools.database.load_file(dbc_path)
        self.bus = can.Bus(interface="virtual", channel=channel)
        self.received_count = 0

    def listen(self, duration_s: float = 5.0) -> None:
        """Receive frames for a given duration and print decoded signals."""
        start = time.time()
        while time.time() - start < duration_s:
            frame = self.bus.recv(timeout=0.5)
            if frame is None:
                continue
            try:
                decoded = self.db.decode_message(frame.arbitration_id, frame.data)
                self.received_count += 1
                print(f"[{self.received_count:03d}] ID=0x{frame.arbitration_id:03X} {decoded}")
            except KeyError:
                pass
        self.bus.shutdown()


if __name__ == "__main__":
    listener = EngineStatusListener(dbc_path="dbc/powertrain.dbc")
    print("Listener starting — waiting for EngineStatus frames...")
    listener.listen(duration_s=5.0)
    print(f"Done. Received {listener.received_count} frames.")