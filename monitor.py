import psutil
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import time

# Function to get CPU and RAM usage
def get_cpu_and_ram_usage():
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    return cpu_usage, ram_usage

# Function to get network details
def get_network_details():
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_io_counters(pernic=True)
    return interfaces, stats

# Function to update network details in the GUI
previous_stats = {}
previous_time = time.time()

def update_network_details():
    global previous_stats, previous_time
    current_time = time.time()
    elapsed_seconds = current_time - previous_time
    previous_time = current_time
    
    interfaces, current_stats = get_network_details()
    for interface in interfaces:
        if interface not in network_labels:
            label = tk.Label(network_frame, text="")
            label.pack()
            network_labels[interface] = label

        # Get previous and current bytes sent and received
        if interface in previous_stats:
            prev_sent = previous_stats[interface].bytes_sent
            prev_recv = previous_stats[interface].bytes_recv
        else:
            prev_sent = prev_recv = 0

        current_sent = current_stats[interface].bytes_sent
        current_recv = current_stats[interface].bytes_recv
        
        # Calculate bytes per second
        sent_per_sec = (current_sent - prev_sent) / elapsed_seconds
        recv_per_sec = (current_recv - prev_recv) / elapsed_seconds
        
        # Convert bytes per second to Mbps
        mbps_sent = (sent_per_sec * 8) / (1024 * 1024)
        mbps_recv = (recv_per_sec * 8) / (1024 * 1024)

        # Update the label with the new speed
        text = f"{interface}: {interfaces[interface][0].address}, Data sent: {mbps_sent:.2f} Mbps, Data received: {mbps_recv:.2f} Mbps"
        network_labels[interface].config(text=text)

    # Save the current stats for the next update
    previous_stats = current_stats
    root.after(1000, update_network_details)  # Update every second

fig, (ax_cpu, ax_ram) = plt.subplots(1, 2, figsize=(10, 4))  # '1, 2' means 1 row, 2 columns of plots

# Initialize two lines, one for each plot
cpu_line, = ax_cpu.plot([0]*60, 'r-', label='CPU Usage')  # CPU usage plot
ram_line, = ax_ram.plot([0]*60, 'b-', label='RAM Usage')  # RAM usage plot

# Function to create futuristic animations
def create_animation():
    cpu_usage, ram_usage = get_cpu_and_ram_usage()
    cpu_data.append(cpu_usage)
    ram_data.append(ram_usage)
    if len(cpu_data) > 60:  # Keep only the latest 60 data points
        cpu_data.pop(0)
        ram_data.pop(0)
    
    # Update CPU plot
    ax_cpu.cla()  # Clear the CPU plot
    ax_cpu.plot(range(len(cpu_data)), cpu_data, 'r-')  # Re-plot CPU line
    ax_cpu.set_title('CPU Usage Over Time')
    ax_cpu.set_xlabel('Time (seconds)')
    ax_cpu.set_ylabel('Usage (%)')
    ax_cpu.set_ylim(0, 100)  # Set the y-axis limits to 0-100 for percentage
    
    # Update RAM plot
    ax_ram.cla()  # Clear the RAM plot
    ax_ram.plot(range(len(ram_data)), ram_data, 'b-')  # Re-plot RAM line
    ax_ram.set_title('RAM Usage Over Time')
    ax_ram.set_xlabel('Time (seconds)')
    ax_ram.set_ylabel('Usage (%)')
    ax_ram.set_ylim(0, 100)  # Set the y-axis limits to 0-100 for percentage
    
    # Redraw the canvas
    canvas.draw()
    
    root.after(1000, create_animation)  # Update every second


# Main GUI setup
root = tk.Tk()
root.title("Advanced System Monitor")
root.geometry("800x600")  # Increase window size

# CPU and RAM usage labels
cpu_label = tk.Label(root, text="")
cpu_label.pack()
ram_label = tk.Label(root, text="")
ram_label.pack()

# Network details frame
network_frame = ttk.LabelFrame(root, text="Network Details")
network_frame.pack(fill="both", expand="yes")

# Placeholder widgets for network details
network_labels = {}

# Animation setup
fig, (ax_cpu, ax_ram) = plt.subplots(1, 2, figsize=(10, 4))  # Correctly create subplots
canvas = FigureCanvasTkAgg(fig, master=root)  # Use the Figure `fig` with subplots
cpu_line, = ax_cpu.plot([0]*60, 'r-', label='CPU Usage')  # CPU usage plot
ram_line, = ax_ram.plot([0]*60, 'b-', label='RAM Usage')  # RAM usage plot
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Data for animation
cpu_data = [0]*60
ram_data = [0]*60

# Update functions
update_network_details()
create_animation()  # This function now handles both CPU and RAM updates

# Tkinter main loop
root.mainloop()