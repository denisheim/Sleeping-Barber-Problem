# Sleeping Barber Problem Simulation

## Overview

The program implements the "Sleeping Barber" problem—a classic concurrency scenario. The setup includes:

- **Barber**: Has one barber chair and can serve one customer at a time.
- **Waiting Room**: Contains a limited number of chairs for customers to wait if the barber is busy.
- **Customers**: Arrive at random intervals chosen in the config.json file. If the barber is sleeping (no customers are currently waiting or being served), the arriving customer wakes him up and gets served immediately. If the barber is busy and there are free seats in the waiting room, the customer waits. If the waiting room is full, the customer leaves immediately.

**Barber behavior**:
1. Sleeps if there are no customers.
2. When a customer arrives while he is sleeping, the barber wakes and starts cutting immediately.
3. If the barber is busy cutting hair, a new customer either waits (if chairs are free) or leaves (if full).
4. After finishing a haircut, the barber checks the waiting room for another customer to serve. If none, he sleeps again.

### Program Flow

```mermaid
Flowchart

A[Customer Arrives] -->|Check Barber| B{Barber Sleeping?}
B -->|Yes| C[Wake Barber, Cut Hair]
B -->|No, Barber Busy| D{Waiting Room Full?}
D -->|Yes| E[Customer Leaves]
D -->|No| F[Customer Waits]
C -->|Done Cutting| B
F -->|Barber done previous| C
E -->|Simulation Done|
```

## Internal Mechanism
Configuration: The program loads configuration from a config.json file, which specifies:

Number of waiting chairs.
Time ranges for customer arrivals and haircuts.
Total number of customers to arrive.
Logging settings.
GUI and Start Action: A GUI (using PyQt5) displays the barber’s status (sleeping, cutting, or idle), customers waiting, logs of events, and statistics. Start the simulation by pressing the "Start" button. Exit out of the window by pressing the "Quit" button, which also completely stops the simulation.


### Multi-threading:

One thread runs the barber logic (sleeping, waking, cutting).
Another thread generates customers at random intervals.
The simulation records arrival times, start and end of each haircut, enabling the computation of average waiting and cutting times.
Example: If you have 3 waiting chairs, 10 total customers, and a barber who takes 1-2 seconds to cut hair, customers will arrive every 0.5-2 seconds. Some may wait, some may leave if they find the waiting room full, and the barber will go through cycles of sleeping and cutting.

## To start the program:

Use these command in the terminal.

To install PyQt5 use the command:
```mermaid
python -m pip install pyqt5
```

This is essential before launching the simulation.

To launch the simulation use the command:
```mermaid
python src/main.py --config config.json
```


## Sources of Information:

- Python Official Docs: https://docs.python.org/3/
- PyQt5 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt5/
- Coverage Tool Documentation: https://coverage.readthedocs.io/
- Multithreading Programming: https://www.w3schools.in/python/multithreaded-programming
- Artificial Intelligence: https://chatgpt.com/
- Clear Explanation of the Sleeping Barber Problem: https://www.youtube.com/watch?v=cArBsUK1ufQ
