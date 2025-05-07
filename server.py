import socket
import threading
from datetime import datetime

##############################################
# In-Memory Data Structures
##############################################

# Tracks vehicles currently on the highway
# plate_number -> (entry_booth, entry_time)
active_vehicles = {}

# Global statistics
statistics = {
    "current_count": 0,      # Vehicles currently on the highway
    "total_vehicles": 0,     # Vehicles that have used (exited) the highway
    "total_fees": 0.0        # Total fees collected
}

# Lock for concurrency (thread-safe access)
data_lock = threading.Lock()

##############################################
# Fee Calculation (Time + Distance + Base Fee)
##############################################

def calculate_fee(entry_booth, exit_booth, entry_time, exit_time):
    """
    Calculate a toll fee that considers:
      - A small base fee
      - Distance between booths
      - Travel time in minutes
    Returns an integer fee (rounded).
    """
    base_fee = 10           # Starting fee
    per_booth_rate = 5      # Rate per booth difference
    per_minute_rate = 2     # Rate per minute

    booth_distance = abs(int(exit_booth) - int(entry_booth))
    duration_minutes = (exit_time - entry_time).total_seconds() / 60.0

    distance_fee = booth_distance * per_booth_rate
    time_fee = duration_minutes * per_minute_rate

    total_fee = base_fee + distance_fee + time_fee
    return int(round(total_fee))  # Return an integer fee

##############################################
# Transaction Processing
##############################################

def process_entry(plate_number, booth_id, timestamp):
    with data_lock:
        if plate_number in active_vehicles:
            print(f"[Warning] Vehicle {plate_number} already on highway. Overwriting old entry.")
        active_vehicles[plate_number] = (booth_id, timestamp)
        statistics["current_count"] += 1
    print(f"[ENTRY] {plate_number} at booth {booth_id} at {timestamp}")

def process_exit(plate_number, booth_id, timestamp):
    with data_lock:
        if plate_number not in active_vehicles:
            print(f"[Warning] EXIT for unknown vehicle {plate_number}. Ignoring.")
            return
        
        entry_booth, entry_time = active_vehicles.pop(plate_number)
        fee = calculate_fee(entry_booth, booth_id, entry_time, timestamp)
        
        statistics["current_count"] -= 1
        statistics["total_vehicles"] += 1
        statistics["total_fees"] += fee
        
    print(f"[EXIT] {plate_number} from booth {entry_booth} to booth {booth_id} at {timestamp}, Fee: {fee}")

##############################################
# Message Parsing
##############################################

def parse_message(raw_message):
    """
    Parses messages of the form:
      TYPE;PLATE_NUMBER;TIMESTAMP;BOOTH_ID
    Returns (msg_type, plate_number, timestamp, booth_id).
    """
    parts = raw_message.strip().split(";")
    if len(parts) != 4:
        raise ValueError(f"Invalid message format: {raw_message}")
    
    msg_type, plate_number, timestamp_str, booth_id = parts
    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    return msg_type.upper(), plate_number, timestamp, booth_id

##############################################
# Client Connection Handler
##############################################

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break  # Client disconnected
                raw_message = data.decode("utf-8")
                
                # Check for optional disconnect command
                if raw_message.strip() == "!DISCONNECT":
                    print(f"[DISCONNECT] {addr} requested disconnect.")
                    break

                try:
                    msg_type, plate_number, timestamp, booth_id = parse_message(raw_message)
                    if msg_type == "ENTRY":
                        process_entry(plate_number, booth_id, timestamp)
                    elif msg_type == "EXIT":
                        process_exit(plate_number, booth_id, timestamp)
                    else:
                        print(f"[ERROR] Unknown message type: {msg_type}")
                except ValueError as ve:
                    print(f"[ERROR] {ve}")

                # Send optional acknowledgment
                conn.sendall("ACK".encode("utf-8"))
                
                # Display real-time stats
                with data_lock:
                    current_count = statistics["current_count"]
                    total_vehicles = statistics["total_vehicles"]
                    total_fees = statistics["total_fees"]
                print(f"[STATS] Current: {current_count}, Total Vehicles: {total_vehicles}, Total Fees: {int(total_fees)}\n")

            except ConnectionResetError:
                print(f"[INFO] Connection reset by {addr}")
                break
    print(f"[CONNECTION CLOSED] {addr} disconnected.")

##############################################
# Server Initialization
##############################################

def start_server(host="10.2.11.79", port=8080):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[LISTENING] Server is listening on {host}:{port}")

    try:
        while True:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("[SHUTDOWN] Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
