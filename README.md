# Time Tracker

A simple desktop application for tracking time spent on various activities. The application provides a clean interface with a table view of all time entries and allows you to start/stop tracking sessions with custom descriptions.

## Features

- **Simple Interface**: Clean, modern GUI with a table view and intuitive buttons
- **Time Tracking**: Click to start tracking, click again to stop and record the session
- **Smart Descriptions**: Enter custom descriptions or select from previous entries
- **Data Persistence**: All entries are saved to a JSON file and persist between sessions
- **Human Readable Format**: Time durations are displayed in a user-friendly format (e.g., "2h 15m 30s")
- **Reset Functionality**: Clear all entries with a confirmation dialog
- **Real-time Updates**: See elapsed time while tracking is active

## How to Use

### Running the Application

1. **Option 1: Run from Python source**
   ```bash
   python time_tracker.py
   ```

2. **Option 2: Run the executable (after building)**
   ```bash
   # Navigate to the dist folder
   cd dist
   # Run the executable
   TimeTracker.exe
   ```

### Using the Application

1. **Start Tracking**: Click the "Start Tracking" button to begin a new time session
2. **Stop Tracking**: Click the "Stop Tracking" button to end the current session
3. **Enter Description**: When stopping, you'll be prompted to enter a description for the activity
4. **View Entries**: All time entries are displayed in the table below the buttons
5. **Reset Data**: Use the "Reset All Entries" button to clear all recorded data

### Description Dialog

When you stop tracking, a dialog will appear where you can:
- Type a new description in the text field
- Select from previous descriptions by double-clicking them in the list
- Press Enter to confirm or Escape to cancel

## Building the Executable

To create a standalone `.exe` file:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the executable**:
   ```bash
   python build.py
   ```

   Or manually:
   ```bash
   pyinstaller --onefile --windowed --name=TimeTracker time_tracker.py
   ```

3. **Find the executable**: The `TimeTracker.exe` file will be created in the `dist/` folder

## File Structure

```
wtk/
├── time_tracker.py      # Main application source code
├── requirements.txt     # Python dependencies
├── build.py            # Build script for creating executable
├── README.md           # This file
├── time_entries.json   # Data file (created automatically)
└── dist/               # Build output folder (created after building)
    └── TimeTracker.exe # Standalone executable
```

## Data Storage

The application stores all time entries in a `time_entries.json` file in the same directory as the executable. The data is organized by date and includes:

- Date
- Start time
- End time
- Duration (in human-readable format)
- Description

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- PyInstaller (for building the executable)

## Troubleshooting

### Common Issues

1. **"PyInstaller not found"**: Install it with `pip install pyinstaller`
2. **Permission errors**: Run the build script as administrator if needed
3. **Missing tkinter**: On some Linux systems, you may need to install `python3-tk`

### Data Recovery

If the `time_entries.json` file becomes corrupted, the application will start with an empty dataset. You can manually edit the JSON file if needed, but be careful to maintain the correct format.

## License

This project is open source and available under the MIT License. 