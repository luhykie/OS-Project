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