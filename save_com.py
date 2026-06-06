import serial
import time

# 🔹 Set your COM port here
PORT = 'COM3'
BAUDRATE = 115200

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {PORT}")
        time.sleep(2)  # wait for stable connection

    except Exception as e:
        print(f"Error opening {PORT}: {e}")
        return

    # 🔹 Output file
    filename = "csi_com3(2).txt"

    with open(filename, "w") as f:
        print("Saving CSI data... Press Ctrl+C to stop\n")

        try:
            while True:
                line = ser.readline().decode(errors='ignore').strip()

                if line.startswith("CSI_1"):
                    print(line)
                    f.write(line + "\n")

        except KeyboardInterrupt:
            print("\nStopped recording.")
            print(f"Data saved in {filename}")

        finally:
            ser.close()
            print("Serial port closed.")

# 🔹 Run program
if __name__ == "__main__":
    main()