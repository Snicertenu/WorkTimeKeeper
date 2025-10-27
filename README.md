# Multi-Sheet Time Tracker

A powerful desktop application for tracking time across multiple companies, projects, or activities simultaneously. The application features a tab-based interface allowing you to manage separate time sheets for different entities, with both concurrent and pause-others tracking modes.

## Features

### Multi-Sheet Management
- **Tab Interface**: Switch between different companies/projects using tabs
- **Add/Remove Sheets**: Create new sheets or remove existing ones as needed
- **Per-Sheet Data**: Each sheet maintains separate time entries and description frequency
- **Visual Indicators**: Tabs show tracking status (⏱ for active, ⏸ for paused)

### Dual Tracking Modes
- **Pause Others Mode**: When you start tracking on one sheet, all other sheets are automatically paused
- **Concurrent Mode**: Track time on multiple sheets simultaneously
- **Pause/Resume**: Individual sheets can be paused and resumed while maintaining elapsed time

### Smart Time Management
- **Smart Descriptions**: Per-sheet description frequency tracking with dropdown selection
- **Real-time Updates**: See elapsed time while tracking with live status updates
- **Human Readable Format**: Time durations displayed as "2h 15m 30s"
- **Data Persistence**: All data saved to `sheets_config.json` and persists between sessions

### Advanced Export System
- **Organized Folders**: Exports automatically organized by sheet name and week
- **Week-Based Naming**: Files named as `sheet_W24_2025.txt` (week 24, year 2025)
- **Multiple Formats**: Export to TXT or CSV format
- **Folder Structure**: `exports/Company_A/sheet_W24_2025.txt`

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

#### Sheet Management
1. **Add Sheet**: Click "➕ Add Sheet" to create a new company/project sheet
2. **Remove Sheet**: Click "➖ Remove Sheet" to delete the current sheet (requires at least 1 sheet)
3. **Switch Sheets**: Click on different tabs to switch between sheets

#### Time Tracking
1. **Pause Others Mode**: Click "Start (Pause Others)" to start tracking and pause all other sheets
2. **Concurrent Mode**: Click "Start (Concurrent)" to track multiple sheets simultaneously
3. **Stop Tracking**: Click the stop button to end the current session
4. **Pause/Resume**: Sheets can be paused and resumed individually

#### Data Management
1. **Enter Description**: When stopping, enter a description or select from frequently used ones
2. **View Entries**: Each sheet shows its own time entries in the table
3. **Reset Sheet**: Use "Reset Sheet" to clear all entries for the current sheet
4. **Export Data**: Export current sheet data to organized folders by week

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

The application stores all data in a `sheets_config.json` file in the same directory as the executable. The data structure includes:

### Per-Sheet Data
- **Entries**: Time entries organized by date
- **Frequency**: Description usage frequency for smart suggestions
- **Session State**: Current tracking status and timing information

### Export Organization
- **Folder Structure**: `exports/{Sheet_Name}/sheet_W{Week}_{Year}.{format}`
- **Example**: `exports/Company_A/sheet_W24_2025.txt`
- **Automatic Creation**: Folders are created automatically when exporting

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