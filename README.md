# TollWay Simulator

**A Python-based transaction server and client simulator for Philippine-style road toll services.**

## Overview

This project implements a multi-threaded TCP server that tracks vehicle entries and exits across a network of simulated toll booths. It calculates toll fees based on a base rate, booth-to-booth distance, and travel time, and maintains real-time in-memory statistics. A companion client script simulates multiple toll booths generating ENTRY and EXIT events.

## Features

- **Concurrent Connections**  
  Handles up to 76 simultaneous client (toll booth) connections using Python threads.
- **Custom Protocol**  
  Messages follow the format `TYPE;PLATE_NUMBER;TIMESTAMP;BOOTH_ID`.
- **Fee Calculation**  
  Combines a base fee, distance-based fee, and time-based fee into a rounded integer toll.
- **In-Memory Data Management**  
  Tracks active vehicles and aggregates statistics without a database.
- **Real-Time Statistics**  
  Displays current vehicle count, total vehicles processed, and total fees collected after each transaction.
- **Configurable Simulation**  
  Easily adjust number of booths and transactions per booth.

## Repository Structure

    tollway-simulator/
    ├── client.py                          # Simulates toll booths (ENTRY/EXIT events)
    ├── server.py                          # TCP server that processes transactions
    ├── docs/
    │   └── NSAPDEV Final Project.docx     # Project report and architecture
    ├── README.md                          # This file
    └── LICENSE                            # (Optional) License file

## Getting Started

### Prerequisites

- Python 3.7+
- (Optional) Virtual environment tool (venv, virtualenv, conda)

### Installation

1. **Clone the repository**

        git clone https://github.com/<your-username>/tollway-simulator.git
        cd tollway-simulator

2. **(Optional) Create and activate a virtual environment**

        python3 -m venv venv
        source venv/bin/activate   # Linux/macOS
        venv\Scripts\activate      # Windows

3. **Install dependencies**

        There are no external dependencies beyond the Python Standard Library.

## Usage

### 1. Start the Server

By default, the server listens on `0.0.0.0:8080`. You can override via command-line:

        python server.py
        # or
        python server.py --host 0.0.0.0 --port 31199

### 2. Run the Client Simulation

Adjust the number of booths and transactions per booth as needed:

        python client.py
        # Default: 76 booths, 5 transactions each

        # Example: 10 booths, 3 transactions each
        python client.py --total-booths 10 --transactions-per-booth 3

### 3. View Output

- **Server console**  
  Logs ENTRY/EXIT events, warnings, and real-time statistics after each transaction.
- **Client console**  
  Logs connection status and messages sent.

## Configuration

Inside `client.py` and `server.py`, you can customize:

- **SERVER_HOST / host**  
- **SERVER_PORT / port**  
- **Number of booths**  
- **Simulation delays**  

## Project Report

See the detailed project description, architecture diagrams, and performance analysis in `docs/NSAPDEV Final Project.docx`.

## Contributing

Contributions are welcome! Please:

1. Fork the repository  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m "Add YourFeature"`)  
4. Push to your branch (`git push origin feature/YourFeature`)  
5. Open a Pull Request

## License

This project is released under the MIT License.

## Authors

- **Maria Sarah Althea A. Mata**  
- **Arianne M. Ranada**
