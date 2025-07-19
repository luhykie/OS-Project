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
<img width="1711" height="912" alt="image" src="https://github.com/user-attachments/assets/66801abf-cd9a-4716-9a32-7c20dc0013b8" />
<img width="1696" height="892" alt="image" src="https://github.com/user-attachments/assets/df101d48-d1dc-4465-b7d6-e0c66148639e" />
<img width="1715" height="909" alt="image" src="https://github.com/user-attachments/assets/30b4957b-0ef5-4949-af68-a1eb7b767441" />
<img width="1708" height="916" alt="image" src="https://github.com/user-attachments/assets/c7020523-b3ff-4fca-b83a-6e8a833f4e6a" />
<img width="1701" height="903" alt="image" src="https://github.com/user-attachments/assets/44547c55-e854-4e89-a5d9-ecb758c6e1a0" />
<img width="1706" height="899" alt="image" src="https://github.com/user-attachments/assets/caa05bae-abfb-4fab-8223-5b570bbea920" />


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


## License

This project is for educational purposes.


## Troubleshooting

- If you get a `ModuleNotFoundError` for `tkinter`, install it via your package manager (e.g., `sudo apt-get install python3-tk` on Ubuntu).
- For any issues, ensure you are using Python 3.7 or higher.


## Acknowledgements

- Inspired by classic OS scheduling problems and visualizations.
- Thanks to the Python and Tkinter communities for documentation and support.
