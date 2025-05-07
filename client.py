import socket
import threading
import time
import random
from datetime import datetime
import string

##############################################
# Configuration and Plate Generation
##############################################

SERVER_HOST = socket.gethostbyname("ccscloud.dlsu.edu.ph")  # Adjust to your server's IP when needed
SERVER_PORT = 31199

def generate_plate_ph():
    """
    Generates a random Philippine-style plate number, e.g., ABC-123.
    Adjust as needed for more modern formats.
    """
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices("0123456789", k=3))
    return f"{letters}-{digits}"

def create_message(msg_type, plate, booth_id):
    """
    Constructs a message of the form:
      TYPE;PLATE_NUMBER;TIMESTAMP;BOOTH_ID
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{msg_type};{plate};{timestamp};{booth_id}"

##############################################
# Booth Simulation Logic
##############################################

def simulate_toll_booth(booth_id, transactions_per_booth=5):
    """
    Simulates a single toll booth:
      - Connects to the server.
      - For each transaction: generates a vehicle, sends an ENTRY message using its own booth ID,
        waits, then sends an EXIT message using a randomly selected exit booth (different from entry).
      - Finally sends a disconnect command.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_HOST, SERVER_PORT))
        print(f"[BOOTH {booth_id}] Connected to server at {SERVER_HOST}:{SERVER_PORT}")

        for _ in range(transactions_per_booth):
            plate_number = generate_plate_ph()

            # Send ENTRY using the toll booth's own ID as the entry point
            entry_msg = create_message("ENTRY", plate_number, booth_id)
            sock.sendall(entry_msg.encode("utf-8"))
            print(f"[BOOTH {booth_id}] Sent ENTRY: {entry_msg}")

            # Simulate travel time on the highway
            time.sleep(random.uniform(2, 5))  # Adjust delay for realistic simulation

            # Select a random exit booth (between 1 and 18) that is different from the entry booth
            exit_booth = random.randint(1, 18)
            while exit_booth == booth_id:
                exit_booth = random.randint(1, 18)

            # Send EXIT with the randomly selected exit booth ID
            exit_msg = create_message("EXIT", plate_number, exit_booth)
            sock.sendall(exit_msg.encode("utf-8"))
            print(f"[BOOTH {booth_id}] Sent EXIT: {exit_msg}")

            # Pause before processing the next vehicle
            time.sleep(random.uniform(1, 3))

        # Send a graceful disconnect signal
        sock.sendall("!DISCONNECT".encode("utf-8"))

    except Exception as e:
        print(f"[ERROR] Booth {booth_id}: {e}")
    finally:
        sock.close()
        print(f"[BOOTH {booth_id}] Disconnected.")

##############################################
# Multiple Booth Launcher
##############################################

def start_client_simulation(total_booths=76, transactions_per_booth=5):
    """
    Spawns multiple threads, each simulating a toll booth with a given
    number of transactions. By default, all 76 toll booths are active.
    """
    threads = []
    for booth_id in range(1, total_booths + 1):
        t = threading.Thread(
            target=simulate_toll_booth,
            args=(booth_id, transactions_per_booth),
            daemon=True
        )
        t.start()
        threads.append(t)
        # Stagger booth startup slightly to avoid a connection flood
        time.sleep(0.1)
    
    for t in threads:
        t.join()

if __name__ == "__main__":
    # Example usage: 76 toll booths, each processing 5 transactions
    start_client_simulation(total_booths=76, transactions_per_booth=5)
