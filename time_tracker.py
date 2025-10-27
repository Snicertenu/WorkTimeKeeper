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
        self.root.title("Time Tracker - Multi-Sheet")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Multi-sheet data storage
        self.sheets_config_file = "sheets_config.json"
        self.sheets = {}  # {"Sheet Name": {"entries": {}, "frequency": {}, "session": None, "start_time": None, "paused": False, "paused_elapsed": 0}}
        self.current_sheet = None
        self.sheet_tabs = {}  # Store tab frames
        self.sheet_trees = {}  # Store treeview widgets per sheet
        self.tracking_threads = {}  # Store tracking threads per sheet
        
        # Load sheets configuration
        self.load_sheets_config()
        
        # Create GUI
        self.create_widgets()
        
        # Select first sheet
        if self.sheets:
            first_sheet = list(self.sheets.keys())[0]
            self.current_sheet = first_sheet
            self.notebook.select(0)
            self.update_table()
            self.update_button_states()
    
    def load_sheets_config(self):
        """Load sheets configuration from file"""
        if os.path.exists(self.sheets_config_file):
            try:
                with open(self.sheets_config_file, 'r') as f:
                    data = json.load(f)
                    self.sheets = data.get("sheets", {})
                    
                    # Ensure each sheet has all required keys
                    for sheet_name in self.sheets:
                        if "session" not in self.sheets[sheet_name]:
                            self.sheets[sheet_name]["session"] = None
                        if "start_time" not in self.sheets[sheet_name]:
                            self.sheets[sheet_name]["start_time"] = None
                        if "paused" not in self.sheets[sheet_name]:
                            self.sheets[sheet_name]["paused"] = False
                        if "paused_elapsed" not in self.sheets[sheet_name]:
                            self.sheets[sheet_name]["paused_elapsed"] = 0
            except:
                self.sheets = {}
        
        # Create default sheet if none exist
        if not self.sheets:
            self.sheets["Default"] = {
                "entries": {},
                "frequency": {},
                "session": None,
                "start_time": None,
                "paused": False,
                "paused_elapsed": 0
            }
    
    def save_sheets_config(self):
        """Save sheets configuration to file"""
        # Don't save runtime tracking state
        save_data = {"sheets": {}}
        for sheet_name, sheet_data in self.sheets.items():
            save_data["sheets"][sheet_name] = {
                "entries": sheet_data["entries"],
                "frequency": sheet_data["frequency"],
                "session": None,
                "start_time": None,
                "paused": False,
                "paused_elapsed": 0
            }
        
        with open(self.sheets_config_file, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Time Tracker - Multi-Sheet", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Sheet management frame
        sheet_mgmt_frame = ttk.Frame(main_frame)
        sheet_mgmt_frame.grid(row=1, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Add Sheet button
        self.add_sheet_button = tk.Button(sheet_mgmt_frame,
                                         text="➕ Add Sheet",
                                         command=self.add_sheet_dialog,
                                         font=("Arial", 10, "bold"),
                                         bg="#107c10",
                                         fg="white",
                                         relief=tk.RAISED,
                                         bd=2,
                                         padx=15,
                                         pady=5,
                                         cursor="hand2")
        self.add_sheet_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Remove Sheet button
        self.remove_sheet_button = tk.Button(sheet_mgmt_frame,
                                            text="➖ Remove Sheet",
                                            command=self.remove_sheet_dialog,
                                            font=("Arial", 10, "bold"),
                                            bg="#d13438",
                                            fg="white",
                                            relief=tk.RAISED,
                                            bd=2,
                                            padx=15,
                                            pady=5,
                                            cursor="hand2")
        self.remove_sheet_button.pack(side=tk.LEFT)
        
        # Tab notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
        
        # Create tabs for all sheets
        for sheet_name in self.sheets:
            self.create_sheet_tab(sheet_name)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        # Start (Pause Others) button
        self.track_pause_button = tk.Button(button_frame,
                                           text="Start (Pause Others)",
                                           command=lambda: self.toggle_tracking('pause'),
                                           font=("Arial", 11, "bold"),
                                           bg="#0078d4",
                                           fg="white",
                                           relief=tk.RAISED,
                                           bd=3,
                                           padx=20,
                                           pady=10,
                                           cursor="hand2")
        self.track_pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Start (Concurrent) button
        self.track_concurrent_button = tk.Button(button_frame,
                                                text="Start (Concurrent)",
                                                command=lambda: self.toggle_tracking('concurrent'),
                                                font=("Arial", 11, "bold"),
                                                bg="#5c2d91",
                                                fg="white",
                                                relief=tk.RAISED,
                                                bd=3,
                                                padx=20,
                                                pady=10,
                                                cursor="hand2")
        self.track_concurrent_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        self.export_button = tk.Button(button_frame,
                                      text="Export Data",
                                      command=self.export_data,
                                      font=("Arial", 11, "bold"),
                                      bg="#107c10",
                                      fg="white",
                                      relief=tk.RAISED,
                                      bd=3,
                                      padx=20,
                                      pady=10,
                                      cursor="hand2")
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Reset button
        self.reset_button = tk.Button(button_frame,
                                     text="Reset Sheet",
                                     command=self.reset_entries,
                                     font=("Arial", 11, "bold"),
                                     bg="#d13438",
                                     fg="white",
                                     relief=tk.RAISED,
                                     bd=3,
                                     padx=20,
                                     pady=10,
                                     cursor="hand2")
        self.reset_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to track time")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, font=("Arial", 9))
        status_bar.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Setup hover effects
        self.setup_button_hover_effects()
    
    def create_sheet_tab(self, sheet_name):
        """Create a tab for a sheet"""
        # Create frame for this tab
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=sheet_name)
        self.sheet_tabs[sheet_name] = tab_frame
        
        # Configure frame
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(0, weight=1)
        
        # Create treeview for table
        columns = ("Date", "Start Time", "End Time", "Duration", "Description")
        tree = ttk.Treeview(tab_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=100)
        
        # Scrollbar for table
        scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid table and scrollbar
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store tree reference
        self.sheet_trees[sheet_name] = tree
    
    def setup_button_hover_effects(self):
        """Setup hover effects for buttons"""
        # Add sheet button
        self.add_sheet_button.bind("<Enter>", lambda e: self.add_sheet_button.configure(bg="#0e6e0e"))
        self.add_sheet_button.bind("<Leave>", lambda e: self.add_sheet_button.configure(bg="#107c10"))
        
        # Remove sheet button
        self.remove_sheet_button.bind("<Enter>", lambda e: self.remove_sheet_button.configure(bg="#b91d47"))
        self.remove_sheet_button.bind("<Leave>", lambda e: self.remove_sheet_button.configure(bg="#d13438"))
        
        # Export button
        self.export_button.bind("<Enter>", lambda e: self.export_button.configure(bg="#0e6e0e"))
        self.export_button.bind("<Leave>", lambda e: self.export_button.configure(bg="#107c10"))
        
        # Reset button
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.configure(bg="#b91d47"))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.configure(bg="#d13438"))
    
    def on_tab_changed(self, event):
        """Handle tab change event"""
        try:
            tab_id = self.notebook.select()
            tab_text = self.notebook.tab(tab_id, "text")
            # Remove tracking indicator if present
            self.current_sheet = tab_text.replace(" ⏱", "").replace(" ⏸", "")
            self.update_table()
            self.update_button_states()
            self.update_status()
        except:
            pass
    
    def add_sheet_dialog(self):
        """Show dialog to add a new sheet"""
        dialog = SheetNameDialog(self.root, list(self.sheets.keys()))
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            sheet_name = dialog.result
            self.sheets[sheet_name] = {
                "entries": {},
                "frequency": {},
                "session": None,
                "start_time": None,
                "paused": False,
                "paused_elapsed": 0
            }
            self.create_sheet_tab(sheet_name)
            self.save_sheets_config()
            
            # Select the new tab
            tab_count = len(self.notebook.tabs())
            self.notebook.select(tab_count - 1)
            self.current_sheet = sheet_name
            self.update_button_states()
    
    def remove_sheet_dialog(self):
        """Show dialog to remove current sheet"""
        if len(self.sheets) <= 1:
            messagebox.showwarning("Cannot Remove", "You must have at least one sheet.")
            return
        
        if not self.current_sheet:
            return
        
        # Check if currently tracking
        if self.sheets[self.current_sheet]["session"] is not None:
            messagebox.showwarning("Cannot Remove", "Please stop tracking on this sheet before removing it.")
            return
        
        if messagebox.askyesno("Confirm Removal",
                              f"Are you sure you want to remove the sheet '{self.current_sheet}'?\n\nAll data on this sheet will be permanently deleted."):
            # Get current tab index
            current_tab = self.notebook.index(self.notebook.select())
            
            # Remove sheet data
            del self.sheets[self.current_sheet]
            del self.sheet_trees[self.current_sheet]
            
            # Remove tab
            self.notebook.forget(current_tab)
            del self.sheet_tabs[self.current_sheet]
            
            # Save and select another tab
            self.save_sheets_config()
            
            # Select first available tab
            if self.sheets:
                self.notebook.select(0)
                self.current_sheet = list(self.sheets.keys())[0]
                self.update_table()
                self.update_button_states()
    
    def toggle_tracking(self, mode):
        """Toggle tracking with specified mode"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        
        # Check if paused
        if sheet["paused"]:
            self.resume_tracking()
            return
        
        # Check if currently tracking
        if sheet["session"] is not None:
            self.stop_tracking()
        else:
            self.start_tracking(mode)
    
    def start_tracking(self, mode):
        """Start tracking on current sheet"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        
        # Pause other sheets if mode is 'pause'
        if mode == 'pause':
            for sheet_name in self.sheets:
                if sheet_name != self.current_sheet:
                    if self.sheets[sheet_name]["session"] is not None and not self.sheets[sheet_name]["paused"]:
                        self.pause_sheet(sheet_name)
        
        # Start tracking
        sheet["start_time"] = datetime.now()
        sheet["session"] = sheet["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        sheet["paused"] = False
        sheet["paused_elapsed"] = 0
        
        # Update UI
        self.update_button_states()
        self.update_tab_indicator(self.current_sheet)
        
        # Start tracking thread
        thread = threading.Thread(target=self.update_elapsed_time, args=(self.current_sheet,), daemon=True)
        self.tracking_threads[self.current_sheet] = thread
        thread.start()
    
    def pause_sheet(self, sheet_name):
        """Pause tracking on a sheet"""
        sheet = self.sheets[sheet_name]
        if sheet["session"] is not None and not sheet["paused"]:
            # Calculate elapsed time so far
            if sheet["start_time"]:
                elapsed = (datetime.now() - sheet["start_time"]).total_seconds()
                sheet["paused_elapsed"] = elapsed
            sheet["paused"] = True
            self.update_tab_indicator(sheet_name)
    
    def resume_tracking(self):
        """Resume tracking on current sheet"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        if sheet["paused"]:
            # Adjust start time to account for paused duration
            paused_duration = sheet["paused_elapsed"]
            sheet["start_time"] = datetime.now() - timedelta(seconds=paused_duration)
            sheet["paused"] = False
            
            # Update UI
            self.update_button_states()
            self.update_tab_indicator(self.current_sheet)
            
            # Restart tracking thread
            thread = threading.Thread(target=self.update_elapsed_time, args=(self.current_sheet,), daemon=True)
            self.tracking_threads[self.current_sheet] = thread
            thread.start()
    
    def stop_tracking(self):
        """Stop tracking on current sheet"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        
        if sheet["start_time"] is None:
            return
        
        end_time = datetime.now()
        duration = end_time - sheet["start_time"]
        
        # Get description from user
        description = self.get_description()
        if description is None:  # User cancelled
            sheet["session"] = None
            sheet["start_time"] = None
            sheet["paused"] = False
            sheet["paused_elapsed"] = 0
            self.update_button_states()
            self.update_tab_indicator(self.current_sheet)
            self.update_status()
            return
        
        # Format times
        start_str = sheet["start_time"].strftime("%H:%M:%S")
        end_str = end_time.strftime("%H:%M:%S")
        duration_str = self.format_duration(duration)
        date_str = sheet["start_time"].strftime("%Y-%m-%d")
        
        # Save entry
        entry = {
            "date": date_str,
            "start_time": start_str,
            "end_time": end_str,
            "duration": duration_str,
            "description": description
        }
        
        # Add to entries
        if date_str not in sheet["entries"]:
            sheet["entries"][date_str] = []
        sheet["entries"][date_str].append(entry)
        
        # Update frequency
        if description in sheet["frequency"]:
            sheet["frequency"][description] += 1
        else:
            sheet["frequency"][description] = 1
        
        # Save to file
        self.save_sheets_config()
        
        # Update display
        self.update_table()
        
        # Reset session
        sheet["session"] = None
        sheet["start_time"] = None
        sheet["paused"] = False
        sheet["paused_elapsed"] = 0
        
        # Update UI
        self.update_button_states()
        self.update_tab_indicator(self.current_sheet)
        self.status_var.set(f"[{self.current_sheet}] Session completed: {duration_str} - {description}")
    
    def update_elapsed_time(self, sheet_name):
        """Update the status bar with elapsed time for a sheet"""
        while True:
            try:
                sheet = self.sheets.get(sheet_name)
                if not sheet or sheet["session"] is None or sheet["paused"]:
                    break
                
                if sheet["start_time"] and sheet_name == self.current_sheet:
                    elapsed = datetime.now() - sheet["start_time"]
                    hours, remainder = divmod(elapsed.total_seconds(), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    elapsed_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
                    self.status_var.set(f"[{sheet_name}] Tracking... Elapsed: {elapsed_str}")
                
                time.sleep(1)
            except:
                break
    
    def update_tab_indicator(self, sheet_name):
        """Update tab text to show tracking status"""
        for i, tab_id in enumerate(self.notebook.tabs()):
            tab_text = self.notebook.tab(tab_id, "text")
            # Remove existing indicators
            clean_name = tab_text.replace(" ⏱", "").replace(" ⏸", "")
            
            if clean_name == sheet_name:
                sheet = self.sheets[sheet_name]
                if sheet["session"] is not None:
                    if sheet["paused"]:
                        self.notebook.tab(tab_id, text=f"{clean_name} ⏸")
                    else:
                        self.notebook.tab(tab_id, text=f"{clean_name} ⏱")
                else:
                    self.notebook.tab(tab_id, text=clean_name)
    
    def update_button_states(self):
        """Update button states based on current sheet"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        
        if sheet["paused"]:
            self.track_pause_button.configure(text="Resume", bg="#ff8c00")
            self.track_concurrent_button.configure(text="Resume", bg="#ff8c00")
        elif sheet["session"] is not None:
            self.track_pause_button.configure(text="Stop Tracking", bg="#d13438")
            self.track_concurrent_button.configure(text="Stop Tracking", bg="#d13438")
        else:
            self.track_pause_button.configure(text="Start (Pause Others)", bg="#0078d4")
            self.track_concurrent_button.configure(text="Start (Concurrent)", bg="#5c2d91")
        
        # Update remove sheet button
        if len(self.sheets) <= 1:
            self.remove_sheet_button.configure(state=tk.DISABLED)
        else:
            self.remove_sheet_button.configure(state=tk.NORMAL)
    
    def update_status(self):
        """Update status bar"""
        if not self.current_sheet:
            self.status_var.set("Ready to track time")
            return
        
        sheet = self.sheets[self.current_sheet]
        if sheet["session"] is None:
            self.status_var.set(f"[{self.current_sheet}] Ready to track time")
    
    def get_description(self):
        """Get description from user"""
        if not self.current_sheet:
            return None
        
        sheet = self.sheets[self.current_sheet]
        dialog = DescriptionDialog(self.root, sheet["frequency"])
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
        """Update the table with current sheet entries"""
        if not self.current_sheet or self.current_sheet not in self.sheet_trees:
            return
        
        tree = self.sheet_trees[self.current_sheet]
        sheet = self.sheets[self.current_sheet]
        
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Add entries to table
        all_entries = []
        for date, day_entries in sheet["entries"].items():
            for entry in day_entries:
                all_entries.append((date, entry))
        
        # Sort by date (newest first)
        all_entries.sort(key=lambda x: x[0], reverse=True)
        
        for date, entry in all_entries:
            tree.insert("", "end", values=(
                entry["date"],
                entry["start_time"],
                entry["end_time"],
                entry["duration"],
                entry["description"]
            ))
    
    def reset_entries(self):
        """Reset entries for current sheet"""
        if not self.current_sheet:
            return
        
        if messagebox.askyesno("Confirm Reset",
                              f"Are you sure you want to delete all time entries on sheet '{self.current_sheet}'?\n\nThis cannot be undone."):
            self.sheets[self.current_sheet]["entries"] = {}
            self.save_sheets_config()
            self.update_table()
            self.status_var.set(f"[{self.current_sheet}] All entries cleared")
    
    def export_data(self):
        """Export current sheet data"""
        if not self.current_sheet:
            return
        
        sheet = self.sheets[self.current_sheet]
        if not sheet["entries"]:
            messagebox.showinfo("No Data", f"No time entries to export on sheet '{self.current_sheet}'.")
            return
        
        # Create export dialog
        export_dialog = ExportDialog(self.root, sheet["entries"], self.current_sheet)
        self.root.wait_window(export_dialog.dialog)


class SheetNameDialog:
    def __init__(self, parent, existing_sheets):
        self.result = None
        self.existing_sheets = existing_sheets
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Sheet")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets
        self.create_widgets()
        
        # Focus on entry
        self.entry.focus_set()
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        label = ttk.Label(main_frame, text="Enter name for new sheet:", font=("Arial", 10, "bold"))
        label.pack(anchor=tk.W, pady=(0, 10))
        
        # Entry field
        self.entry = ttk.Entry(main_frame, width=40, font=("Arial", 10))
        self.entry.pack(fill=tk.X, pady=(0, 15))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        # Buttons
        ok_button = ttk.Button(button_frame, text="Create", command=self.ok_clicked)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked)
        cancel_button.pack(side=tk.RIGHT)
    
    def ok_clicked(self):
        """Handle OK button click"""
        sheet_name = self.entry.get().strip()
        if not sheet_name:
            messagebox.showwarning("Warning", "Please enter a sheet name.")
            return
        
        if sheet_name in self.existing_sheets:
            messagebox.showwarning("Warning", "A sheet with this name already exists.")
            return
        
        self.result = sheet_name
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.result = None
        self.dialog.destroy()


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
    def __init__(self, parent, entries, sheet_name):
        self.entries = entries
        self.sheet_name = sheet_name
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
        title_label = ttk.Label(main_frame, text=f"Export: {self.sheet_name}", font=("Arial", 14, "bold"))
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
        
        # Info label
        week_info = datetime.now().isocalendar()
        info_text = f"Will export to: exports/{self.sheet_name.replace(' ', '_')}/sheet_W{week_info[1]:02d}_{week_info[0]}.{{format}}"
        info_label = ttk.Label(main_frame, text=info_text, font=("Arial", 8), foreground="gray")
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
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
        format_type = self.format_var.get()
        include_header = self.include_header_var.get()
        sort_by_date = self.sort_by_date_var.get()
        
        try:
            if format_type == "txt":
                filepath = self.export_to_txt(include_header, sort_by_date)
            else:
                filepath = self.export_to_csv(include_header, sort_by_date)
            
            messagebox.showinfo("Export Successful", 
                              f"Time entries exported successfully to:\n{filepath}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")
    
    def export_to_txt(self, include_header, sort_by_date):
        """Export data to TXT format"""
        # Calculate week and year
        week_info = datetime.now().isocalendar()
        
        # Create folder structure
        folder_path = f"exports/{self.sheet_name.replace(' ', '_')}"
        os.makedirs(folder_path, exist_ok=True)
        
        # Create filename
        filepath = f"{folder_path}/sheet_W{week_info[1]:02d}_{week_info[0]}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if include_header:
                f.write(f"Time Entries - {self.sheet_name}\n")
                f.write(f"Week {week_info[1]}, {week_info[0]}\n")
                f.write("=" * 80 + "\n\n")
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
        
        return filepath
    
    def export_to_csv(self, include_header, sort_by_date):
        """Export data to CSV format"""
        import csv
        
        # Calculate week and year
        week_info = datetime.now().isocalendar()
        
        # Create folder structure
        folder_path = f"exports/{self.sheet_name.replace(' ', '_')}"
        os.makedirs(folder_path, exist_ok=True)
        
        # Create filename
        filepath = f"{folder_path}/sheet_W{week_info[1]:02d}_{week_info[0]}.csv"
        
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
        
        return filepath
    
    def cancel_clicked(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


# Import timedelta for pause/resume functionality
from datetime import timedelta


def main():
    root = tk.Tk()
    app = TimeTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()
