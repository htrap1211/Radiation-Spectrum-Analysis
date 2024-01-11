# Serial Data Receiver and FastAPI Sender

This repository contains a Python script for receiving data from a serial port and sending it to a FastAPI server. The script allows you to select a COM port and baud rate, then continuously listens for incoming data. Once data is received, it is processed and sent to a FastAPI server running locally.

## Features

- **COM Port Selection:** Choose the COM port to listen for serial data.
- **Baud Rate Configuration:** Set the baud rate for serial communication.
- **Data Processing:** Parse incoming data and send it to the FastAPI server.
- **Automatic Reconnection:** If the connection to the serial port is lost, the script attempts to reconnect automatically.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/serial-data-fastapi.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the script:

   ```bash
   python serial_data_fastapi.py
   ```

## Usage

1. The script will prompt you to select a COM port and enter a baud rate.
2. Once connected, it will continuously listen for incoming data.
3. When data is received, it is processed and sent to the FastAPI server.
4. The FastAPI server endpoint is `http://localhost:8000/receive-data`.

## Dependencies

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Requests](https://docs.python-requests.org/en/master/)
- [PySerial](https://pythonhosted.org/pyserial/)

## Notes

- Make sure to have FastAPI installed and a FastAPI server running locally before running the script.

Feel free to contribute, report issues, or suggest improvements!
