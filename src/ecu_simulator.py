import time
import can
import cantools


class EngineECU:

    def __init__(self, dbc_path: str, channel: str = "vcan0"):
        self.db = cantools.database.load_file(dbc_path)
        self.message = self.db.get_message_by_name("EngineStatus")
        self.bus = can.Bus(interface="virtual", channel=channel)
        self.cycle_time_s = 0.1 
    
    
    def send_once(self, engine_speed: float, coolant_temp: float) -> None:
        data = self.message.encode({
            "EngineSpeed": engine_speed,
            "CoolantTemperature": coolant_temp,
        })

        frame = can.Message(
            arbitration_id=self.message.frame_id,
            data=data,
            is_extended_id=False,
        )
        
        self.bus.send(frame)


    def run(self, duration_s: float = 5.0) -> None:
        start = time.time()
        while time.time() - start < duration_s:
            self.send_once(engine_speed=3000.0, coolant_temp=90.0)
            time.sleep(self.cycle_time_s)
        self.bus.shutdown()


if __name__ == "__main__":
    ecu = EngineECU(dbc_path="dbc/powertrain.dbc")
    print("EngineECU starting — broadcasting EngineStatus for 5 seconds...")
    ecu.run(duration_s=5.0)
    print("Done.")