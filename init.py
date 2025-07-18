import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time

# -----------------------------
# Data Structures and Utilities
# -----------------------------

class Process:
    # Represents a process in the scheduler
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid # Process ID
        self.arrival = arrival # Arrival Time 
        self.burst = burst # Total Execution Time
        self.priority = priority # Priority Value
        self.remaining = burst # Remaining Time Left to Execute (preemptive)
        self.completion = 0 # Time pf which Process Completes
        self.turnaround = 0 # Turnaround Time = Completion - Arrival
        self.waiting = 0 # Waiting Time = Turnaround - Burst
        self.response = -1 # Response Time = First Run - Arrival
        self.start = -1 # First Run
        self.queue_level = 0  # For MLFQ

    def as_dict(self):
        return {
            'PID': self.pid,
            'Arrival': self.arrival,
            'Burst': self.burst,
            'Priority': self.priority,
            'Completion': self.completion,
            'Turnaround': self.turnaround,
            'Waiting': self.waiting,
            'Response': self.response,
        }
    
# -----------------------------
# Scheduling Algorithms
# -----------------------------
def fcfs(processes):
    # First-Come, First-Served scheduling
    procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    time = 0
    gantt = []
    for p in procs:
        if time < p.arrival:
            gantt.append(('IDLE', p.arrival - time))
            time = p.arrival
        p.start = time
        p.response = time - p.arrival
        time += p.burst
        p.completion = time
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst
        gantt.append((p.pid, p.burst))
    return procs, gantt
    
def sjf(processes):
    # Shortest Job First (non-preemptive) scheduling
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    gantt = []
    ready = []
    procs.sort(key=lambda p: (p.arrival, p.burst, p.pid))
    idx = 0
    while completed < n:
        while idx < n and procs[idx].arrival <= time:
            ready.append(procs[idx])
            idx += 1
        if ready:
            ready.sort(key=lambda p: (p.burst, p.arrival, p.pid))
            p = ready.pop(0)
            if time < p.arrival:
                gantt.append(('IDLE', p.arrival - time))
                time = p.arrival
            p.start = time
            p.response = time - p.arrival
            time += p.burst
            p.completion = time
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            gantt.append((p.pid, p.burst))
            completed += 1
        else:
            if idx < n:
                next_arrival = procs[idx].arrival
                gantt.append(('IDLE', next_arrival - time))
                time = next_arrival
    return procs, gantt

def srtf(processes):
    # Shortest Remaining Time First (preemptive SJF) scheduling
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    gantt = []
    ready = []
    idx = 0
    last_pid = None
    while completed < n:
        while idx < n and procs[idx].arrival <= time:
            ready.append(procs[idx])
            idx += 1
        ready = [p for p in ready if p.remaining > 0]
        if ready:
            ready.sort(key=lambda p: (p.remaining, p.arrival, p.pid))
            p = ready[0]
            if p.start == -1:
                p.start = time
                p.response = time - p.arrival
            if last_pid != p.pid:
                gantt.append((p.pid, 1))
            else:
                gantt[-1] = (p.pid, gantt[-1][1] + 1)
            p.remaining -= 1
            time += 1
            if p.remaining == 0:
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
                completed += 1
            last_pid = p.pid
        else:
            if idx < n:
                next_arrival = procs[idx].arrival
                idle_time = next_arrival - time
                gantt.append(('IDLE', idle_time))
                time = next_arrival
                last_pid = None
    return procs, gantt

def round_robin(processes, quantum):
    # Round Robin scheduling with given time quantum
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    queue = []
    idx = 0
    gantt = []
    last_pid = None
    in_queue = set()
    while completed < n:
        while idx < n and procs[idx].arrival <= time:
            queue.append(procs[idx])
            in_queue.add(procs[idx].pid)
            idx += 1
        if queue:
            p = queue.pop(0)
            in_queue.remove(p.pid)
            if p.start == -1:
                p.start = time
                p.response = time - p.arrival
            run_time = min(quantum, p.remaining)
            if last_pid != p.pid:
                gantt.append((p.pid, run_time))
            else:
                gantt[-1] = (p.pid, gantt[-1][1] + run_time)
            time += run_time
            p.remaining -= run_time
            while idx < n and procs[idx].arrival <= time:
                if procs[idx].pid not in in_queue and procs[idx].remaining > 0:
                    queue.append(procs[idx])
                    in_queue.add(procs[idx].pid)
                idx += 1
            if p.remaining > 0:
                queue.append(p)
                in_queue.add(p.pid)
            else:
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
                completed += 1
            last_pid = p.pid
        else:
            if idx < n:
                next_arrival = procs[idx].arrival
                idle_time = next_arrival - time
                gantt.append(('IDLE', idle_time))
                time = next_arrival
                last_pid = None
    return procs, gantt

def mlfq(processes, quanta, allotments):
    # Multilevel Feedback Queue scheduling with 4 queues
    # 4 queues: Q0 (highest) to Q3 (lowest)
    procs = [Process(p.pid, p.arrival, p.burst, p.priority) for p in processes]
    n = len(procs)
    time = 0
    completed = 0
    queues = [[] for _ in range(4)]
    idx = 0
    gantt = []
    last_pid = None
    in_queue = set()
    # For each process, track time spent at each level
    level_time = {p.pid: [0, 0, 0, 0] for p in procs}
    while completed < n:
        while idx < n and procs[idx].arrival <= time:
            queues[0].append(procs[idx])
            in_queue.add(procs[idx].pid)
            procs[idx].queue_level = 0
            idx += 1
        # Find the highest non-empty queue
        qidx = next((i for i, q in enumerate(queues) if q), None)
        if qidx is not None:
            p = queues[qidx].pop(0)
            in_queue.remove(p.pid)
            quantum = quanta[qidx]
            allot = allotments[qidx]
            run_time = min(quantum, p.remaining, allot - level_time[p.pid][qidx])
            if p.start == -1:
                p.start = time
                p.response = time - p.arrival
            if last_pid != (p.pid, qidx):
                gantt.append((f"{p.pid}(Q{qidx})", run_time))
            else:
                gantt[-1] = (gantt[-1][0], gantt[-1][1] + run_time)
            time += run_time
            p.remaining -= run_time
            level_time[p.pid][qidx] += run_time
            # Add new arrivals during this run
            while idx < n and procs[idx].arrival <= time:
                queues[0].append(procs[idx])
                in_queue.add(procs[idx].pid)
                procs[idx].queue_level = 0
                idx += 1
            if p.remaining == 0:
                p.completion = time
                p.turnaround = p.completion - p.arrival
                p.waiting = p.turnaround - p.burst
                completed += 1
            elif level_time[p.pid][qidx] >= allot:
                # Demote to next queue
                if qidx < 3:
                    p.queue_level = qidx + 1
                    queues[qidx + 1].append(p)
                    in_queue.add(p.pid)
                else:
                    queues[qidx].append(p)
                    in_queue.add(p.pid)
                level_time[p.pid][qidx] = 0
            else:
                queues[qidx].append(p)
                in_queue.add(p.pid)
            last_pid = (p.pid, qidx)
        else:
            if idx < n:
                next_arrival = procs[idx].arrival
                idle_time = next_arrival - time
                gantt.append(('IDLE', idle_time))
                time = next_arrival
                last_pid = None
    return procs, gantt

# -----------------------------
# GUI Application
# -----------------------------
class CPUSchedulerGUI:
    # Main GUI application for CPU scheduling visualization
    def __init__(self, root):
        # Initialize the GUI and variables
        self.root = root  # Store the root window
        self.root.title("CPU Scheduling Visualization")  # Set window title
        self.root.configure(bg="#18120f")  # Set background color
        self.root.geometry("1100x700")  # Set window size
        self.root.resizable(False, False)  # Disable window resizing

        # Initialize variables
        self.processes = []  # List to hold Process objects
        self.selected_algorithm = tk.StringVar()  # Selected algorithm dropdown
        self.quantum = tk.IntVar(value=1)  # Time quantum for Round Robin
        self.sim_speed = tk.DoubleVar(value=0.1)  # Speed of simulation (delay between steps)
        self.mlfq_quanta = [tk.IntVar(value=2) for _ in range(4)]  # Quanta for each MLFQ level
        self.mlfq_allot = [tk.IntVar(value=4) for _ in range(4)]  # Allotment times for MLFQ levels
        self.action_msg = tk.StringVar()  # Status/action message for feedback
        self.gantt_data = []  # Stores tuples of (label, duration) for Gantt chart
        self.sim_thread = None  # Thread used to run simulation
        self.sim_running = False  # Flag to indicate if simulation is active

        self._build_gui()  # Build GUI widgets

    def _build_gui(self):
        # Build all GUI components and layout

        # Top bar label with developers' names
        tk.Label(
            self.root,
            text="Developed by : LYKA ENTERA & KEA ABAQUITA",
            bg="#a05a1c",
            fg="white",
            anchor="w",
            font=("Segoe UI", 10, "bold")
        ).place(x=0, y=0, relwidth=1, height=25)

        # Process input section (Frame with input fields and buttons)
        frame = tk.Frame(self.root, bg="#18120f", highlightbackground="#a05a1c", highlightthickness=2)
        frame.place(x=10, y=35, width=540, height=120)

        # Labels for each field (input fields for processes)
        tk.Label(frame, text="Process", bg="#18120f", fg="white").place(x=10, y=5)
        tk.Label(frame, text="Arrival Time", bg="#18120f", fg="white").place(x=120, y=5)
        tk.Label(frame, text="Exec. Time", bg="#18120f", fg="white").place(x=220, y=5)
        tk.Label(frame, text="Priority", bg="#18120f", fg="white").place(x=320, y=5)

        # Input widgets for adding processes
        self.pid_entry = ttk.Combobox(frame, values=[f"P{i+1}" for i in range(20)], width=5)  # Dropdown for process ID
        self.pid_entry.place(x=10, y=30)
        self.arrival_entry = tk.Entry(frame, width=8)  # Entry for arrival time
        self.arrival_entry.place(x=120, y=30)
        self.burst_entry = tk.Entry(frame, width=8)  # Entry for burst (execution) time
        self.burst_entry.place(x=220, y=30)
        self.priority_entry = tk.Entry(frame, width=5)  # Entry for priority
        self.priority_entry.place(x=320, y=30)

        # Buttons for managing process list
        tk.Button(frame, text="Add", command=self.add_process, width=6, bg="#a05a1c", fg="white").place(x=400, y=28)
        tk.Button(frame, text="Generate Random", command=self.generate_random, width=15, bg="#a05a1c", fg="white").place(x=10, y=70)
        tk.Button(frame, text="Clear All", command=self.clear_processes, width=10, bg="#a05a1c", fg="white").place(x=140, y=70)

        # Table to display added processes
        self.table = ttk.Treeview(self.root, columns=("PID", "Arrival", "Burst", "Priority"), show="headings", height=5)  # Treeview for showing processes
        self.table.place(x=10, y=160, width=540, height=120)
        for col in ("PID", "Arrival", "Burst", "Priority"):
            self.table.heading(col, text=col)
            self.table.column(col, width=120, anchor="center")

        # Style configuration for the process table
        style = ttk.Style()
        style.configure("Treeview", background="#18120f", fieldbackground="#18120f", foreground="white", rowheight=24)
        style.map('Treeview', background=[('selected', '#a05a1c')])

        # Frame for algorithm selection and parameters
        algo_frame = tk.Frame(self.root, bg="#18120f", highlightbackground="#a05a1c", highlightthickness=2)
        algo_frame.place(x=10, y=290, width=540, height=70)

        # Dropdown for selecting scheduling algorithm
        tk.Label(algo_frame, text="Algorithm", bg="#18120f", fg="white").place(x=10, y=5)
        algo_menu = ttk.Combobox(algo_frame, textvariable=self.selected_algorithm, values=["FCFS", "SJF", "SRTF", "Round Robin", "MLFQ"], state="readonly", width=15)
        algo_menu.place(x=10, y=30)
        algo_menu.current(0)

        # Slider for time quantum (used in Round Robin)
        tk.Label(algo_frame, text="Time Quantum (RR)", bg="#18120f", fg="white").place(x=180, y=5)
        tk.Scale(algo_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.quantum, length=120, bg="#18120f", fg="white", highlightthickness=0).place(x=180, y=30)

        # MLFQ input parameters: Quanta and Allotment per level
        tk.Label(algo_frame, text="MLFQ Quanta", bg="#18120f", fg="white").place(x=320, y=5)
        for i in range(4):
            tk.Entry(algo_frame, textvariable=self.mlfq_quanta[i], width=2).place(x=320+40*i, y=30, width=30)

        tk.Label(algo_frame, text="Allot", bg="#18120f", fg="white").place(x=480, y=5)
        for i in range(4):
            tk.Entry(algo_frame, textvariable=self.mlfq_allot[i], width=2).place(x=480+40*i, y=30, width=30)

        # Action/status message label (for user feedback)
        tk.Label(self.root, textvariable=self.action_msg, bg="#18120f", fg="red", font=("Segoe UI", 10, "bold")).place(x=10, y=365, width=540, height=25)

        # Frame for simulation controls (speed + simulate button)
        sim_frame = tk.Frame(self.root, bg="#18120f", highlightbackground="#a05a1c", highlightthickness=2)
        sim_frame.place(x=10, y=400, width=540, height=70)

        # Slider to adjust simulation speed
        tk.Label(sim_frame, text="Simulation Speed", bg="#18120f", fg="white").place(x=10, y=5)
        tk.Scale(sim_frame, from_=0.05, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, variable=self.sim_speed, length=200, bg="#18120f", fg="white", highlightthickness=0).place(x=10, y=30)

        # Buttons to start simulation and reset all inputs
        tk.Button(sim_frame, text="Simulate", command=self.start_simulation, width=10, bg="#a05a1c", fg="white").place(x=250, y=20)
        tk.Button(sim_frame, text="Reset All", command=self.reset_all, width=10, bg="#a05a1c", fg="white").place(x=370, y=20)

        # Gantt chart display canvas
        # The Gantt chart visually represents the timeline of process execution over time
        tk.Label(self.root, text="Gantt Chart (Each box represents a second)", bg="#18120f", fg="white").place(x=10, y=480)
        self.gantt_canvas = tk.Canvas(self.root, bg="#18120f", highlightbackground="#a05a1c", height=40, width=1060)
        self.gantt_canvas.place(x=10, y=510)

        # Frame for process execution status metrics
        metrics_frame = tk.Frame(self.root, bg="#18120f", highlightbackground="#a05a1c", highlightthickness=2)
        metrics_frame.place(x=570, y=35, width=520, height=540)
        tk.Label(metrics_frame, text="Process", bg="#18120f", fg="white").place(x=10, y=5)
        tk.Label(metrics_frame, text="Status", bg="#18120f", fg="white").place(x=100, y=5)
        tk.Label(metrics_frame, text="Completion %", bg="#18120f", fg="white").place(x=200, y=5)
        tk.Label(metrics_frame, text="Remaining", bg="#18120f", fg="white").place(x=320, y=5)
        tk.Label(metrics_frame, text="Waiting", bg="#18120f", fg="white").place(x=420, y=5)

        # Labels for showing individual process metrics
        # These status labels are dynamically updated during the simulation to reflect current process state
        self.status_labels = []
        for i in range(10):
            row = []
            for j, w in enumerate([70, 90, 100, 100, 100]):
                lbl = tk.Label(metrics_frame, text="", bg="#18120f", fg="white", width=10, anchor="center")
                lbl.place(x=10+sum([70,90,100,100,100][:j]), y=30+i*25, width=w, height=22)
                row.append(lbl)
            self.status_labels.append(row)

        # Display labels for average statistics
        self.avg_waiting = tk.StringVar()  # Average waiting time
        self.avg_turnaround = tk.StringVar()  # Average turnaround time
        self.avg_response = tk.StringVar()  # Average response time
        tk.Label(self.root, textvariable=self.avg_waiting, bg="#18120f", fg="white", font=("Segoe UI", 10)).place(x=570, y=590, width=170, height=25)
        tk.Label(self.root, textvariable=self.avg_turnaround, bg="#18120f", fg="white", font=("Segoe UI", 10)).place(x=740, y=590, width=170, height=25)
        tk.Label(self.root, textvariable=self.avg_response, bg="#18120f", fg="white", font=("Segoe UI", 10)).place(x=910, y=590, width=170, height=25)