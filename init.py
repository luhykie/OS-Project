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