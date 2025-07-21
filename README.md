# OS CPU Scheduler Visualizer

A Python Tkinter-based GUI application for visualizing and simulating classic CPU scheduling algorithms.  
Developed by: **Lyka Entera & Kea Abaquita**

---

## Features

- **Visualize** the execution of processes using Gantt charts.
- **Simulate** the following scheduling algorithms:
  - First-Come, First-Served (FCFS)
  - Shortest Job First (SJF)
  - Shortest Remaining Time First (SRTF)
  - Round Robin (with configurable quantum)
  - Multilevel Feedback Queue (MLFQ, with configurable quanta and allotments)
- **Add, generate, and clear** process lists easily.
- **View process metrics**: Waiting, Turnaround, and Response times (per process and averages).
- **Modern, colorful UI** with clear labels and status tables.

---

## Requirements

- Python 3.7+
- Tkinter (usually included with Python)
- No external dependencies required

---

## How to Run

1. **Clone or Download** this repository.
2. Open a terminal in the project directory.
3. Run the application:

   ```sh
   python init.py
   ```

---

## Usage

### 1. **Add Processes**
- Enter **Process ID** (PID), **Arrival Time**, and **Execution Time** (Burst).
- Click **"Add ♡"** to add the process to the list.
- Or click **"Generate Random ✩"** to auto-generate random processes.
- Use **"Clear All ♪"** to remove all processes.

### 2. **Select Algorithm**
- Choose from FCFS, SJF, SRTF, Round Robin, or MLFQ.
- For **Round Robin**, set the **Time Quantum**.
- For **MLFQ**, set the **Quanta** and **Allotment** for each queue.

### 3. **Simulation Controls**
- Adjust **Simulation Speed** as desired.
- Click **"★ Simulate ★"** to run the simulation.
- Click **"✩ Reset All ✩"** to clear all results and start over.

### 4. **View Results**
- **Gantt Chart**: Visualizes process execution over time.
- **Status Table**: Shows per-process status, completion, waiting, response, and turnaround times.
- **Averages**: Displays average waiting, turnaround, and response times.


## Screenshots
<img width="1712" height="906" alt="image" src="https://github.com/user-attachments/assets/eaba41b8-5762-4d54-be92-f3466eb25206" />
<img width="1705" height="909" alt="image" src="https://github.com/user-attachments/assets/0dc22ad8-44ee-4015-9dfe-480ed47f3663" />
<img width="1702" height="903" alt="image" src="https://github.com/user-attachments/assets/d78f4931-0210-4c39-8de6-a24a69f9607c" />
<img width="1703" height="899" alt="image" src="https://github.com/user-attachments/assets/e168a46d-0593-449d-9af5-795f634c4f6d" />
<img width="1700" height="900" alt="image" src="https://github.com/user-attachments/assets/f6d88c3c-f3f1-4646-aab4-1af945744927" />
<img width="1698" height="906" alt="image" src="https://github.com/user-attachments/assets/8b40a765-d8aa-4554-b80b-84cc02b4fb64" />


## Customization

- **MLFQ Defaults**: You can change the default quanta and allotments in the code:
  ```python
  self.mlfq_quanta = [tk.IntVar(value=v) for v in [2, 4, 8, 16]]
  self.mlfq_allot = [tk.IntVar(value=4) for _ in range(4)]
  ```
- **UI Colors and Fonts**: Easily adjustable in the `_build_gui` method.


## Packaging as EXE (Optional)

If you want to create a standalone Windows executable:

1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Build the executable:
   ```sh
   pyinstaller --onefile init.py
   ```
   The `.exe` will be in the `dist` folder.


## Authors

- Lyka Entera
- Kea Abaquita

Contributions
- **Kea Abaquita**
  - Implemented the FCFS and SJF scheduling algorithms.
  - Developed the initial GUI layout and applied the custom warm color palette.
  - Contributed to Gantt chart integration and status table layout.

- **Lyka Entera**
  - Implemented and debugged the SRTF, Round Robin, and MLFQ scheduling algorithms.
  - Handled the majority of error checking, simulation fixes, and overall debugging.
  - Developed process flow logic, thread handling, and metric computation.
  - Refined the visual display, animation flow, and ensured simulation accuracy and stability.


## License

This project is for educational purposes.


## Troubleshooting

- If you get a `ModuleNotFoundError` for `tkinter`, install it via your package manager (e.g., `sudo apt-get install python3-tk` on Ubuntu).
- For any issues, ensure you are using Python 3.7 or higher.


## Acknowledgements

- Inspired by classic OS scheduling problems and visualizations.
- Thanks to the Python and Tkinter communities for documentation and support.
