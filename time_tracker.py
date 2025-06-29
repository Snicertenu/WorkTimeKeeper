import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import threading
import time

class TimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Time Tracker")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Data storage
        self.data_file = "time_entries.json"
        self.entries = self.load_entries()
        self.description_frequency = self.load_description_frequency()
        self.current_session = None
        self.session_start_time = None
        
        # Create GUI
        self.create_widgets()
        self.update_table()
        
    def load_entries(self):
        """Load existing entries from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def load_description_frequency(self):
        """Load or create description frequency tracking"""
        frequency_file = "description_frequency.json"
        if os.path.exists(frequency_file):
            try:
                with open(frequency_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_entries(self):
        """Save entries to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.entries, f, indent=2)
    
    def save_description_frequency(self):
        """Save description frequency to file"""
        with open("description_frequency.json", 'w') as f:
            json.dump(self.description_frequency, f, indent=2)
    
    def update_description_frequency(self, description):
        """Update the frequency count for a description"""
        if description in self.description_frequency:
            self.description_frequency[description] += 1
        else:
            self.description_frequency[description] = 1
        self.save_description_frequency()
    
    def get_sorted_descriptions(self):
        """Get descriptions sorted by frequency (most used first)"""
        sorted_descriptions = sorted(
            self.description_frequency.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [desc for desc, freq in sorted_descriptions]
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Time Tracker", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Start/Stop button - Make it larger and more prominent
        self.track_button = tk.Button(button_frame, 
                                     text="Start Tracking", 
                                     command=self.toggle_tracking,
                                     font=("Arial", 12, "bold"),
                                     bg="#0078d4",
                                     fg="white",
                                     relief=tk.RAISED,
                                     bd=3,
                                     padx=30,
                                     pady=10,
                                     cursor="hand2")
        self.track_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # Export button - Make it prominent
        self.export_button = tk.Button(button_frame, 
                                      text="Export Data", 
                                      command=self.export_data,
                                      font=("Arial", 12, "bold"),
                                      bg="#107c10",
                                      fg="white",
                                      relief=tk.RAISED,
                                      bd=3,
                                      padx=20,
                                      pady=10,
                                      cursor="hand2")
        self.export_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # Reset button - Make it larger and more prominent
        self.reset_button = tk.Button(button_frame, 
                                     text="Reset All Entries", 
                                     command=self.reset_entries,
                                     font=("Arial", 12, "bold"),
                                     bg="#d13438",
                                     fg="white",
                                     relief=tk.RAISED,
                                     bd=3,
                                     padx=20,
                                     pady=10,
                                     cursor="hand2")
        self.reset_button.pack(side=tk.LEFT)
        
        # Update reset button visibility
        self.update_reset_button()
        
        # Table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Create treeview for table
        columns = ("Date", "Start Time", "End Time", "Duration", "Description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=100)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid table and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to track time")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure button hover effects
        self.setup_button_hover_effects()
    
    def setup_button_hover_effects(self):
        """Setup hover effects for buttons"""
        def on_enter_track(event):
            if self.current_session is None:
                self.track_button.configure(bg="#106ebe")  # Darker blue
            else:
                self.track_button.configure(bg="#b91d47")  # Darker red
        
        def on_leave_track(event):
            if self.current_session is None:
                self.track_button.configure(bg="#0078d4")  # Original blue
            else:
                self.track_button.configure(bg="#d13438")  # Original red
        
        def on_enter_export(event):
            self.export_button.configure(bg="#0e6e0e")  # Darker green
        
        def on_leave_export(event):
            self.export_button.configure(bg="#107c10")  # Original green
        
        def on_enter_reset(event):
            self.reset_button.configure(bg="#b91d47")  # Darker red
        
        def on_leave_reset(event):
            self.reset_button.configure(bg="#d13438")  # Original red
        
        # Bind hover events
        self.track_button.bind("<Enter>", on_enter_track)
        self.track_button.bind("<Leave>", on_leave_track)
        self.export_button.bind("<Enter>", on_enter_export)
        self.export_button.bind("<Leave>", on_leave_export)
        self.reset_button.bind("<Enter>", on_enter_reset)
        self.reset_button.bind("<Leave>", on_leave_reset)
    
    def toggle_tracking(self):
        """Toggle between start and stop tracking"""
        if self.current_session is None:
            # Start tracking
            self.start_tracking()
        else:
            # Stop tracking
            self.stop_tracking()
    
    def start_tracking(self):
        """Start a new tracking session"""
        self.session_start_time = datetime.now()
        self.current_session = self.session_start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.track_button.configure(text="Stop Tracking", bg="#d13438")
        self.status_var.set(f"Tracking started at {self.session_start_time.strftime('%H:%M:%S')}")
        
        # Start a thread to update the status with elapsed time
        self.update_thread = threading.Thread(target=self.update_elapsed_time, daemon=True)
        self.update_thread.start()
    
    def update_elapsed_time(self):
        """Update the status bar with elapsed time"""
        while self.current_session is not None:
            if self.session_start_time:
                elapsed = datetime.now() - self.session_start_time
                hours, remainder = divmod(elapsed.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                elapsed_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                self.status_var.set(f"Tracking... Elapsed: {elapsed_str}")
            time.sleep(1)
    
    def stop_tracking(self):
        """Stop the current tracking session"""
        if self.session_start_time is None:
            return
            
        end_time = datetime.now()
        duration = end_time - self.session_start_time
        
        # Get description from user
        description = self.get_description()
        if description is None:  # User cancelled
            self.current_session = None
            self.session_start_time = None
            self.track_button.configure(text="Start Tracking", bg="#0078d4")
            self.status_var.set("Ready to track time")
            return
        
        # Format times
        start_str = self.session_start_time.strftime("%H:%M:%S")
        end_str = end_time.strftime("%H:%M:%S")
        duration_str = self.format_duration(duration)
        date_str = self.session_start_time.strftime("%Y-%m-%d")
        
        # Save entry
        entry = {
            "date": date_str,
            "start_time": start_str,
            "end_time": end_str,
            "duration": duration_str,
            "description": description
        }
        
        # Add to entries (group by date)
        if date_str not in self.entries:
            self.entries[date_str] = []
        self.entries[date_str].append(entry)
        
        # Save to file
        self.save_entries()
        
        # Update display
        self.update_table()
        self.update_reset_button()
        
        # Reset session
        self.current_session = None
        self.session_start_time = None
        self.track_button.configure(text="Start Tracking", bg="#0078d4")
        self.status_var.set(f"Session completed: {duration_str} - {description}")
        
        # Update description frequency
        self.update_description_frequency(description)
    
    def get_description(self):
        """Get description from user with option to select from previous entries"""
        # Create dialog with sorted descriptions and their frequencies
        dialog = DescriptionDialog(self.root, self.description_frequency)
        self.root.wait_window(dialog.dialog)
        
        return dialog.result
    
    def format_duration(self, duration):
        """Format duration in human readable format"""
        total_seconds = int(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def update_table(self):
        """Update the table with current entries"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add entries to table (sorted by date, newest first)
        all_entries = []
        for date, day_entries in self.entries.items():
            for entry in day_entries:
                all_entries.append((date, entry))
        
        # Sort by date (newest first)
        all_entries.sort(key=lambda x: x[0], reverse=True)
        
        for date, entry in all_entries:
            self.tree.insert("", "end", values=(
                entry["date"],
                entry["start_time"],
                entry["end_time"],
                entry["duration"],
                entry["description"]
            ))
    
    def update_reset_button(self):
        """Show/hide reset button based on whether there are entries"""
        if self.entries:
            self.reset_button.pack(side=tk.LEFT)
        else:
            self.reset_button.pack_forget()
    
    def reset_entries(self):
        """Reset all entries after confirmation"""
        if messagebox.askyesno("Confirm Reset", 
                              "Are you sure you want to delete all time entries? This cannot be undone."):
            self.entries = {}
            self.save_entries()
            self.update_table()
            self.update_reset_button()
            self.status_var.set("All entries cleared")
    
    def export_data(self):
        """Export time entries to TXT or CSV file"""
        if not self.entries:
            messagebox.showinfo("No Data", "No time entries to export.")
            return
        
        # Create export dialog
        export_dialog = ExportDialog(self.root, self.entries)
        self.root.wait_window(export_dialog.dialog)

class DescriptionDialog:
    def __init__(self, parent, description_frequency):
        self.result = None
        self.description_frequency = description_frequency
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Enter Description")
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Focus on entry
        self.entry.focus_set()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        label = ttk.Label(main_frame, text="Enter a description for this time session:", font=("Arial", 10, "bold"))
        label.pack(anchor=tk.W, pady=(0, 10))
        
        # Entry field
        self.entry = ttk.Entry(main_frame, width=60, font=("Arial", 10))
        self.entry.pack(fill=tk.X, pady=(0, 15))
        
        # Previous descriptions section
        if self.description_frequency:
            prev_label = ttk.Label(main_frame, text="Or select from frequently used descriptions:", font=("Arial", 10, "bold"))
            prev_label.pack(anchor=tk.W, pady=(10, 5))
            
            # Dropdown frame
            dropdown_frame = ttk.Frame(main_frame)
            dropdown_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Create dropdown with frequency information
            self.dropdown_var = tk.StringVar()
            self.dropdown = ttk.Combobox(dropdown_frame, 
                                        textvariable=self.dropdown_var,
                                        width=50,
                                        font=("Arial", 10),
                                        state="readonly")
            
            # Create dropdown options with frequency
            dropdown_options = []
            sorted_descriptions = sorted(
                self.description_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for desc, freq in sorted_descriptions:
                if freq > 1:
                    dropdown_options.append(f"{desc} ({freq} times)")
                else:
                    dropdown_options.append(desc)
            
            self.dropdown['values'] = dropdown_options
            self.dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Bind dropdown selection
            self.dropdown.bind('<<ComboboxSelected>>', self.on_dropdown_select)
            
            # Quick select buttons for top 3 most used
            if len(sorted_descriptions) > 0:
                quick_frame = ttk.Frame(main_frame)
                quick_frame.pack(fill=tk.X, pady=(10, 0))
                
                quick_label = ttk.Label(quick_frame, text="Quick select:", font=("Arial", 9))
                quick_label.pack(side=tk.LEFT, padx=(0, 10))
                
                # Create quick select buttons for top 3
                for i, (desc, freq) in enumerate(sorted_descriptions[:3]):
                    btn = ttk.Button(quick_frame, 
                                   text=f"{desc[:20]}{'...' if len(desc) > 20 else ''}", 
                                   command=lambda d=desc: self.quick_select(d))
                    btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Buttons
        ok_button = ttk.Button(button_frame, text="OK", command=self.ok_clicked)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked)
        cancel_button.pack(side=tk.RIGHT)
    
    def on_dropdown_select(self, event):
        """Handle dropdown selection"""
        selected = self.dropdown_var.get()
        if selected:
            # Extract description from "description (X times)" format
            if " (" in selected:
                description = selected.split(" (")[0]
            else:
                description = selected
            self.entry.delete(0, tk.END)
            self.entry.insert(0, description)
    
    def quick_select(self, description):
        """Quick select a description"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, description)
        self.dropdown_var.set("")  # Clear dropdown selection
    
    def ok_clicked(self):
        """Handle OK button click"""
        description = self.entry.get().strip()
        if description:
            self.result = description
            self.dialog.destroy()
        else:
            messagebox.showwarning("Warning", "Please enter a description.")
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.dialog.destroy()

class ExportDialog:
    def __init__(self, parent, entries):
        self.entries = entries
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Export Time Entries")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.export_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def create_widgets(self):
        """Create export dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Export Time Entries", font=("Arial", 14, "bold"))
        title_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Format selection
        format_frame = ttk.LabelFrame(main_frame, text="Export Format", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.format_var = tk.StringVar(value="txt")
        
        txt_radio = ttk.Radiobutton(format_frame, text="Text File (.txt)", 
                                   variable=self.format_var, value="txt")
        txt_radio.pack(anchor=tk.W, pady=2)
        
        csv_radio = ttk.Radiobutton(format_frame, text="CSV File (.csv)", 
                                   variable=self.format_var, value="csv")
        csv_radio.pack(anchor=tk.W, pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Export Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.include_header_var = tk.BooleanVar(value=True)
        header_check = ttk.Checkbutton(options_frame, text="Include header row", 
                                      variable=self.include_header_var)
        header_check.pack(anchor=tk.W, pady=2)
        
        self.sort_by_date_var = tk.BooleanVar(value=True)
        sort_check = ttk.Checkbutton(options_frame, text="Sort by date (newest first)", 
                                    variable=self.sort_by_date_var)
        sort_check.pack(anchor=tk.W, pady=2)
        
        # File name frame
        filename_frame = ttk.LabelFrame(main_frame, text="File Name", padding="10")
        filename_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.filename_var = tk.StringVar(value=f"time_entries_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        filename_entry = ttk.Entry(filename_frame, textvariable=self.filename_var, width=40)
        filename_entry.pack(fill=tk.X)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Buttons
        export_button = ttk.Button(button_frame, text="Export", command=self.export_clicked)
        export_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked)
        cancel_button.pack(side=tk.RIGHT)
    
    def export_clicked(self):
        """Handle export button click"""
        filename = self.filename_var.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a file name.")
            return
        
        format_type = self.format_var.get()
        include_header = self.include_header_var.get()
        sort_by_date = self.sort_by_date_var.get()
        
        try:
            if format_type == "txt":
                self.export_to_txt(filename, include_header, sort_by_date)
            else:
                self.export_to_csv(filename, include_header, sort_by_date)
            
            messagebox.showinfo("Export Successful", 
                              f"Time entries exported successfully to {filename}.{format_type}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def export_to_txt(self, filename, include_header, sort_by_date):
        """Export data to TXT format"""
        filepath = f"{filename}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if include_header:
                f.write("Date\tStart Time\tEnd Time\tDuration\tDescription\n")
                f.write("-" * 80 + "\n")
            
            # Get all entries
            all_entries = []
            for date, day_entries in self.entries.items():
                for entry in day_entries:
                    all_entries.append((date, entry))
            
            # Sort if requested
            if sort_by_date:
                all_entries.sort(key=lambda x: x[0], reverse=True)
            
            # Write entries
            for date, entry in all_entries:
                line = f"{entry['date']}\t{entry['start_time']}\t{entry['end_time']}\t{entry['duration']}\t{entry['description']}\n"
                f.write(line)
    
    def export_to_csv(self, filename, include_header, sort_by_date):
        """Export data to CSV format"""
        import csv
        
        filepath = f"{filename}.csv"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if include_header:
                writer.writerow(["Date", "Start Time", "End Time", "Duration", "Description"])
            
            # Get all entries
            all_entries = []
            for date, day_entries in self.entries.items():
                for entry in day_entries:
                    all_entries.append((date, entry))
            
            # Sort if requested
            if sort_by_date:
                all_entries.sort(key=lambda x: x[0], reverse=True)
            
            # Write entries
            for date, entry in all_entries:
                writer.writerow([
                    entry['date'],
                    entry['start_time'],
                    entry['end_time'],
                    entry['duration'],
                    entry['description']
                ])
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()

def main():
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main() 