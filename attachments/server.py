from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI()

# Variable to store the received data
received_data = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint to handle GET requests and return the received data
@app.get("/get-data")
async def get_data():
    global received_data
    if received_data is not None:
        return JSONResponse(content={"message": "GET request received successfully", "received_data": received_data})
    else:
        return JSONResponse(content={"message": "No data received yet"})

# Endpoint to handle POST requests and store the received data
@app.post("/receive-data")
async def receive_data(request: Request):
    global received_data
    data = await request.json()  # Parse the request body as JSON
    decoded_data = data.get('data', [])  # Extract the 'data' array
    print("Received data array:", decoded_data)  # Print the data array

    # Store the received data
    received_data = decoded_data
    return {"message": "Data received successfully", "received_data": decoded_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


