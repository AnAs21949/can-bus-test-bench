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