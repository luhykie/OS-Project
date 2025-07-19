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
    # print(processes)
    procs = sorted(processes, key=lambda p: (p.arrival, p.pid))
    time = 0
    gantt = []
    for p in procs:
        # Wait for process to arrive if CPU is idle
        if time < p.arrival:
            gantt.append(('IDLE', p.arrival - time))
            time = p.arrival
        p.start = time
        p.response = time - p.arrival
        p.completion = time + p.burst
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst
        p.remaining = 0
        time = p.completion
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
            p.completion = time + p.burst
            p.turnaround = p.completion - p.arrival
            p.waiting = p.turnaround - p.burst
            p.remaining = 0
            time = p.completion
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
        self.root = root
        self.root.title("OS: CPU Scheduler")
        self.root.configure(bg="#1A1A1A")  # Black background
        self.root.geometry("1370x700")  # Set window size
        self.root.resizable(False, False) # Disable resizing
        self.processes = [] # List to hold Process objects
        self.selected_algorithm = tk.StringVar() # Selected scheduling algorithm
        self.quantum = tk.IntVar(value=1) # Time quantum for Round Robin
        self.sim_speed = tk.DoubleVar(value=0.1) # Simulation speed
        self.mlfq_quanta = [tk.IntVar(value=v) for v in [2, 4, 8, 16]] # Quanta for MLFQ queues
        self.mlfq_allot = [tk.IntVar(value=4) for _ in range(4)] # Allotment for MLFQ queues
        self.action_msg = tk.StringVar() # Action message for user feedback
        self.gantt_data = [] # Data for Gantt chart
        self.sim_thread = None # Thread for running the simulation
        self.sim_running = False # Flag to check if simulation is running
        self._build_gui() 

    def _build_gui(self):
        # Build all GUI components and layout
        # Top bar
        tk.Label(self.root, text="☆彡 Developed by: LYKA ENTERA & KEA ABAQUITA ミ★", bg="#FF1493", fg="white", anchor="w", font=("Arial", 10, "bold")).place(x=0, y=0, relwidth=1, height=25)

        # Process input frame
        frame = tk.Frame(self.root, bg="#1A1A1A", highlightbackground="#FF1493", highlightthickness=2)
        frame.place(x=10, y=35, width=540, height=120)
        tk.Label(frame, text="✧ Process", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=4, y=5)
        tk.Label(frame, text="✧ Arrival Time", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=100, y=5)
        tk.Label(frame, text="✧ Burst Time", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=203, y=5)
        # Removed Priority label and entry
        self.pid_entry = ttk.Combobox(frame, values=[f"P{i+1}" for i in range(20)], width=5)
        self.pid_entry.place(x=10, y=30)
        self.arrival_entry = tk.Entry(frame, width=8, bg="#2A2A2A", fg="#FF69B4")
        self.arrival_entry.place(x=120, y=30)
        self.burst_entry = tk.Entry(frame, width=8, bg="#2A2A2A", fg="#FF69B4")
        self.burst_entry.place(x=220, y=30)
        # Removed Priority entry
        tk.Button(frame, text="Add ♡", command=self.add_process, width=6, bg="#FF1493", fg="white", font=("Arial", 8)).place(x=300, y=28)
        tk.Button(frame, text="Generate Random ✩", command=self.generate_random, width=18, bg="#FF1493", fg="white", font=("Arial", 8)).place(x=10, y=70)
        tk.Button(frame, text="Clear All ♪", command=self.clear_processes, width=10, bg="#FF1493", fg="white", font=("Arial", 8)).place(x=140, y=70)

        # Process table
        self.table = ttk.Treeview(self.root, columns=("PID", "Arrival", "Burst", "Response", "Turnaround"), show="headings", height=5)
        self.table.place(x=10, y=160, width=540, height=120)
        for col, width in zip(("PID", "Arrival", "Burst", "Response", "Turnaround"), (80, 80, 80, 100, 120)):
            self.table.heading(col, text=col)
            self.table.column(col, width=width, anchor="center")
        style = ttk.Style()
        style.configure("Treeview", background="#2A2A2A", fieldbackground="#2A2A2A", foreground="#FF69B4", rowheight=24, font=("Arial", 8))
        style.map('Treeview', background=[('selected', '#FF1493')])

        # Algorithm selection
        algo_frame = tk.Frame(self.root, bg="#1A1A1A", highlightbackground="#FF1493", highlightthickness=2)
        algo_frame.place(x=10, y=290, width=635, height=70)
        tk.Label(algo_frame, text="♪ Algorithm", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=10, y=5)
        algo_menu = ttk.Combobox(algo_frame, textvariable=self.selected_algorithm, values=["FCFS", "SJF", "SRTF", "Round Robin", "MLFQ"], state="readonly", width=15)
        algo_menu.place(x=10, y=30)
        algo_menu.current(0)
        tk.Label(algo_frame, text="♫ Time Quantum (RR)", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=180, y=5)
        tk.Scale(algo_frame, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.quantum, length=120, bg="#1A1A1A", fg="#FF69B4", highlightthickness=0, troughcolor="#2A2A2A").place(x=180, y=30)
        # MLFQ settings
        tk.Label(algo_frame, text="✰ MLFQ Quanta", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=330, y=5)
        for i in range(4):
            tk.Entry(algo_frame, textvariable=self.mlfq_quanta[i], width=2, bg="#2A2A2A", fg="#FF69B4").place(x=320+40*i, y=30, width=30) 
        # Allot label in same style/format as Quanta
        tk.Label(algo_frame, text="✰ MLFQ Allot", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=470, y=5)
        # Allot entry boxes horizontally aligned like Quanta
        for i in range(4):
            tk.Entry(algo_frame, textvariable=self.mlfq_allot[i], width=2, bg="#2A2A2A", fg="#FF69B4").place(x=470+40*i, y=30, width=30)

        # Action message
        tk.Label(self.root, textvariable=self.action_msg, bg="#1A1A1A", fg="#FF69B4", font=("Arial", 10, "bold")).place(x=10, y=365, width=540, height=25)

        # Simulation controls
        sim_frame = tk.Frame(self.root, bg="#1A1A1A", highlightbackground="#FF1493", highlightthickness=2)
        sim_frame.place(x=10, y=400, width=540, height=70)
        tk.Label(sim_frame, text="✧ Simulation Speed ✧", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=10, y=5)
        tk.Scale(sim_frame, from_=0.05, to=1.0, resolution=0.05, orient=tk.HORIZONTAL, variable=self.sim_speed, length=200, bg="#1A1A1A", fg="#FF69B4", highlightthickness=0, troughcolor="#2A2A2A").place(x=10, y=30)
        tk.Button(sim_frame, text="★ Simulate ★", command=self.start_simulation, width=12, bg="#FF1493", fg="white", font=("Arial", 9)).place(x=250, y=20)
        tk.Button(sim_frame, text="✩ Reset All ✩", command=self.reset_all, width=12, bg="#FF1493", fg="white", font=("Arial", 9)).place(x=370, y=20)

        # Gantt chart
        tk.Label(self.root, text="♡ Gantt Chart ♡ (Each box is one time unit)", bg="#1A1A1A", fg="#FF69B4", font=("Arial", 9)).place(x=10, y=480)
        self.gantt_canvas = tk.Canvas(self.root, bg="#1A1A1A", highlightbackground="#FF1493", height=60, width=1235)
        self.gantt_canvas.place(x=10, y=510)
        
        # Metrics and status
        metrics_frame = tk.Frame(self.root, bg="#1A1A1A", highlightbackground="#FF1493", highlightthickness=2)
        metrics_frame.place(x=650, y=35, width=700, height=470)
        # Improved spacing for metrics/status table
        col_widths = [70, 80, 110, 85, 90, 80, 100]  # wider columns
        col_positions = []
        current_pos = 20  # more left margin
        for width in col_widths:
            col_positions.append(current_pos)
            current_pos += width + 10  # add 10px gap between columns
     
        # Place headers with new positions and widths
        headers = [
            "✿ Process", "✿ Status", "✿ Completion %", "✿ Remaining",
            "✿ Waiting", "✿ Response", "✿ Turnaround"
        ]
        for idx, header in enumerate(headers):
            tk.Label(metrics_frame, text=header, bg="#1A1A1A", fg="#FF69B4", font=("Arial", 10, "bold")).place(
                x=col_positions[idx], y=8, width=col_widths[idx], height=28)

        self.status_labels = []
        for i in range(10):
            row = []
            for j in range(len(col_widths)):
                bg_color = "#252525" if i % 2 == 1 else "#1A1A1A"  # alternating row color
                lbl = tk.Label(metrics_frame, text="", bg=bg_color, fg="#FF8DC7", anchor="center", font=("Arial", 10))
                lbl.place(x=col_positions[j], y=45 + i * 32, width=col_widths[j], height=28)
                row.append(lbl)
            self.status_labels.append(row)

        # Averages 
        self.avg_waiting = tk.StringVar(value="★ Avg Wait: -- ★")
        self.avg_turnaround = tk.StringVar(value="♡ Avg Turnaround: -- ♡")
        self.avg_response = tk.StringVar(value="✿ Avg Response: -- ✿")
        
        # Create decorated frames for averages with pink background
        avg_wait_frame = tk.Frame(self.root, bg="#FF69B4", highlightthickness=1, highlightbackground="#FF1493")
        avg_wait_frame.place(x=18, y=585, width=1225, height=25)
        avg_turn_frame = tk.Frame(self.root, bg="#FF69B4", highlightthickness=1, highlightbackground="#FF1493")
        avg_turn_frame.place(x=18, y=625, width=1225, height=25)
        avg_resp_frame = tk.Frame(self.root, bg="#FF69B4", highlightthickness=1, highlightbackground="#FF1493")
        avg_resp_frame.place(x=18, y=665, width=1225, height=25)
        
        # Place labels on colored frames
        tk.Label(avg_wait_frame, textvariable=self.avg_waiting, bg="#FF69B4", fg="#FFD1E0", font=("Arial", 9, "bold")).pack(fill=tk.BOTH, expand=True)
        tk.Label(avg_turn_frame, textvariable=self.avg_turnaround, bg="#FF69B4", fg="#FFD1E0", font=("Arial", 9, "bold")).pack(fill=tk.BOTH, expand=True)
        tk.Label(avg_resp_frame, textvariable=self.avg_response, bg="#FF69B4", fg="#FFD1E0", font=("Arial", 9, "bold")).pack(fill=tk.BOTH, expand=True)

    def add_process(self):
        # Add a process from user input to the process list
        pid = self.pid_entry.get() or f"P{len(self.processes)+1}"
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            # Removed priority input
            # Validate input values
            if burst <= 0:
                self.action_msg.set("✘ Execution time must be greater than 0! ✘")
                return
        except ValueError:
            self.action_msg.set("✘ Invalid input values! Please check! ✘")
            return
        if any(p.pid == pid for p in self.processes):
            self.action_msg.set("✘ Duplicate PID detected! ✘")
            return
        self.processes.append(Process(pid, arrival, burst))  # Removed priority
        self.refresh_table()
        self.action_msg.set("")

    def generate_random(self):
        # Generate random processes for simulation
        n = random.randint(3, 7)
        # print(n)
        # print(self.processes)
        no_process = self.pid_entry.get() or f"P{len(self.processes)+1}"
        num = no_process[1]
        processes = int(num)
        # print(processes)
        self.processes.clear()
        for i in range(processes):
            pid = f"P{i+1}"
            arrival = random.randint(0, 5)
            burst = random.randint(1, 10)  # Ensure minimum burst time of 1
            self.processes.append(Process(pid, arrival, burst))  # Removed priority
        self.refresh_table()
        self.action_msg.set("✧ Random processes generated!")

    def clear_processes(self):
        # Remove all processes from the list
        self.processes.clear()
        self.refresh_table()
        self.action_msg.set("✧ All processes cleared!")

    def refresh_table(self):
        # Update the process table in the GUI
        for row in self.table.get_children():
            self.table.delete(row)
        for p in self.processes:
            response = p.response if p.response != -1 else "-"
            turnaround = p.turnaround if p.turnaround != 0 else "-"
            self.table.insert('', 'end', values=(p.pid, p.arrival, p.burst, response, turnaround))

    def start_simulation(self):
        # Start the simulation in a separate thread
        if not self.processes:
            self.action_msg.set("✘ No processes to simulate! Please add some! ✘")
            return
        if self.sim_running:
            self.action_msg.set("✧ Simulation already running! Please wait~ ✧")
            return
            
        # Validate time quantum values
        if self.selected_algorithm.get() == "Round Robin" and self.quantum.get() <= 0:
            self.action_msg.set("✘ Time quantum must be greater than 0! ✘")
            return
            
        # Validate MLFQ quanta and allotment values
        if self.selected_algorithm.get() == "MLFQ":
            for i, q in enumerate(self.mlfq_quanta):
                if q.get() <= 0:
                    self.action_msg.set(f"✘ Queue {i} quantum must be greater than 0! ✘")
                    return
                    
            for i, a in enumerate(self.mlfq_allot):
                if a.get() <= 0:
                    self.action_msg.set(f"✘ Queue {i} allotment must be greater than 0! ✘")
                    return
        
        self.sim_running = True
        self.sim_thread = threading.Thread(target=self.simulate)
        self.sim_thread.start()

    def simulate(self):
        # Run the selected scheduling algorithm and update the GUI
        algo = self.selected_algorithm.get()
        procs = [Process(p.pid, p.arrival, p.burst) for p in self.processes]
        if algo == "FCFS":
            result, gantt = fcfs(procs)
        elif algo == "SJF":
            result, gantt = sjf(procs)
        elif algo == "SRTF":
            result, gantt = srtf(procs)
        elif algo == "Round Robin":
            result, gantt = round_robin(procs, self.quantum.get())
        elif algo == "MLFQ":
            quanta = [q.get() for q in self.mlfq_quanta]
            allot = [a.get() for a in self.mlfq_allot]
            result, gantt = mlfq(procs, quanta, allot)
        else:
            self.action_msg.set("Unknown algorithm!")
            self.sim_running = False
            return
        self.gantt_data = gantt
        self.update_gantt()
        self.update_status(result)
        self.update_metrics(result)
        self.sim_running = False

    def update_gantt(self):
        # Draw the Gantt chart on the canvas
        self.gantt_canvas.delete("all")
        x = 5
        y = 10
        h = 20
        for label, dur in self.gantt_data:
            color = "#FF1493" if label != "IDLE" else "#2A2A2A"
            self.gantt_canvas.create_rectangle(x, y, x+dur*25, y+h, fill=color, outline="#FF69B4", width=1)
            self.gantt_canvas.create_text(x+dur*12, y+h//2, text=str(label), fill="#FFFFFF", font=("Arial", 8, "bold"))
            x += dur*25

    def update_status(self, procs):
        # Update the status table for each process
        for i in range(10):
            if i < len(procs):
                p = procs[i]
                self.status_labels[i][0].config(text=p.pid)
                # Status: ✓ Done if completed, ✧ Running if started but not done, ✧ Waiting if not started
                if p.completion and p.remaining == 0:
                    status = "✓ Done"
                elif p.start != -1 and p.remaining > 0:
                    status = "✧ Running"
                else:
                    status = "✧ Waiting"
                self.status_labels[i][1].config(text=status)
                percent = int(100 * (p.burst - p.remaining) / p.burst) if p.burst else 0
                if p.completion and p.remaining == 0:
                    percent = 100
                self.status_labels[i][2].config(text=f"{percent}%")
                self.status_labels[i][3].config(text=f"{p.remaining if p.remaining >= 0 else 0}")
                self.status_labels[i][4].config(text=f"{p.waiting}")
                self.status_labels[i][5].config(text=f"{p.response if p.response != -1 else '-'}")
                self.status_labels[i][6].config(text=f"{p.turnaround if p.turnaround != 0 else '-'}")
            else:
                for lbl in self.status_labels[i]:
                    lbl.config(text="")
        # Update the table with response and turnaround times
        for p in procs:
            for item in self.table.get_children():
                values = list(self.table.item(item)['values'])
                if values[0] == p.pid:
                    # PID, Arrival, Burst, Response, Turnaround
                    values[3] = p.response if p.response != -1 else "-"
                    values[4] = p.turnaround if p.turnaround != 0 else "-"
                    self.table.item(item, values=values)

    def update_metrics(self, procs):
        # Calculate and display average metrics
        n = len(procs)
        if n == 0:
            self.avg_waiting.set("★ Avg Wait: -- ★")
            self.avg_turnaround.set("♡ Avg Turnaround: -- ♡")
            self.avg_response.set("✿ Avg Response: -- ✿")
            return
        avg_wait = sum(p.waiting for p in procs) / n
        avg_turn = sum(p.turnaround for p in procs) / n
        avg_resp = sum(p.response for p in procs if p.response != -1) / n
        # Set detailed average metrics with information about each PID
        wait_details = "; ".join([f"{p.pid}: {p.waiting}" for p in procs])
        turn_details = "; ".join([f"{p.pid}: {p.turnaround}" for p in procs])
        resp_details = "; ".join([f"{p.pid}: {p.response if p.response != -1 else '-'}" for p in procs])
        self.avg_waiting.set(f"✧ Avg Wait: {avg_wait:.2f} ({wait_details})")
        self.avg_turnaround.set(f"♡ Avg Turnaround: {avg_turn:.2f} ({turn_details})")
        self.avg_response.set(f"✿ Avg Response: {avg_resp:.2f} ({resp_details})")

    def reset_all(self):
        # Reset all fields and clear the GUI
        self.clear_processes()
        self.gantt_canvas.delete("all")
        for i in range(10):
            for lbl in self.status_labels[i]:
                lbl.config(text="")
        self.avg_waiting.set("")
        self.avg_turnaround.set("")
        self.avg_response.set("")
        self.action_msg.set("✧ Everything has been reset!")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # Entry point: start the GUI application
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()
