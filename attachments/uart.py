import serial
import sys
import time
import requests

# Function to print the byte stream
def printByteStream(data):
    for byte in data:
        sys.stdout.write(f"{int(byte):d} ")
    sys.stdout.flush()

# Function to list available COM ports
def list_available_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    print("Available COM ports:")
    for port in ports:
        print(port.device)

# Function to get user's selection for COM port and baud rate
def get_user_selection():
    print("\nSelect a COM port (e.g., COM3):")
    port = input()
    print("Enter baud rate (e.g., 4400, 19200, 38400, 57600, 115200):")
    baud_rate = int(input())
    return port, baud_rate

# Function to receive data and send it to the FastAPI server
def receiveAndSendData():
    list_available_ports()
    port, baud_rate = get_user_selection()

    ser = None
    is_connected = False

    required_start_nodes = [115, 116, 97, 114, 116]
    end_nodes = [101, 110, 100]

    received_bytes = bytearray()
    is_data_processing = False
    start_node_index = 0

    while True:
        if not is_connected:
            print(f"Connecting to {port} at baud rate {baud_rate}...")
            while not is_connected:
                try:
                    ser = serial.Serial(port, baud_rate, timeout=1)
                    is_connected = True
                    print("Connected.")
                except serial.SerialException:
                    pass

        try:
            data = ser.read(ser.in_waiting)
            if data:
                for byte in data:
                    if not is_data_processing:
                        if byte == required_start_nodes[start_node_index]:
                            start_node_index += 1
                            if start_node_index == len(required_start_nodes):
                                is_data_processing = True
                                start_node_index = 0
                                received_bytes = bytearray()
                        else:
                            start_node_index = 0
                    else:
                        received_bytes.append(byte)
                        if byte == end_nodes[-1]:
                            if received_bytes[-len(end_nodes):] == bytes(end_nodes):
                                printByteStream(received_bytes[len(required_start_nodes):-len(end_nodes)])
                                print("\n")

                                # Send the received data to the FastAPI server
                                try:
                                    data_to_send = ' '.join(map(str, received_bytes[len(required_start_nodes):-len(end_nodes)]))
                                    requests.get("http://localhost:8000/receive-data", data=data_to_send)
                                except requests.exceptions.RequestException as e:
                                    print(f"Error sending data to FastAPI server: {e}")

                            is_data_processing = False
                            start_node_index = 0
                            received_bytes = bytearray()

        except serial.SerialException:
            print("Connection lost. Retrying...")
            is_connected = False
            ser.close()
            time.sleep(1)

# Call the function to start receiving and sending data
receiveAndSendData()
