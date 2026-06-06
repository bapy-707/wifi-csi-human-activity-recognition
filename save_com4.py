import serial

ser = serial.Serial('COM4', 115200)

with open("csi_com4.txt", "w") as f:
    print("Saving COM4 data... Ctrl+C to stop")

    try:
        while True:
            raw = ser.readline()

            if not raw:
                continue

            line = raw.decode(errors='ignore').strip()

            # 🔥 print everything for debugging
            print(line)

            if "CSI_2" in line:
                f.write(line + "\n")

    except KeyboardInterrupt:
        print("\nSaved COM9 data")