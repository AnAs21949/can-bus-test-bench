"""Demo: run EngineECU sender + EngineStatusListener in parallel threads."""

import threading

from src.ecu_simulator import EngineECU
from src.listener import EngineStatusListener

DBC_PATH = "dbc/powertrain.dbc"
CHANNEL = "vcan0"
DURATION_S = 3.0


def main() -> None:
    sender = EngineECU(dbc_path=DBC_PATH, channel=CHANNEL)
    listener = EngineStatusListener(dbc_path=DBC_PATH, channel=CHANNEL)

    sender_thread = threading.Thread(target=sender.run, args=(DURATION_S,))
    listener_thread = threading.Thread(target=listener.listen, args=(DURATION_S,))

    listener_thread.start()
    sender_thread.start()

    sender_thread.join()
    listener_thread.join()

    print(f"\nDemo finished. {listener.received_count} frames received.")


if __name__ == "__main__":
    main()