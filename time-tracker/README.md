# TimeTracker

A productivity-focused time tracking application that automatically monitors and logs your computer activities.

## Features

- Automatic activity tracking based on active windows and applications
- Idle detection with configurable thresholds
- Clean and simple user interface
- Activity history with duration tracking
- JSON or SQLite storage options
- Configurable logging
- macOS support (with plans for cross-platform support)

## Requirements

- Python 3.8 or higher
- macOS (current version)
- Required Python packages (installed automatically):
  - PyYAML
  - psutil
  - pyobjc-framework-Quartz (macOS)
  - pyobjc-framework-AppKit (macOS)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/timetracker.git
cd timetracker
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Usage

1. Start the application:
```bash
timetracker
```

2. The main window will appear with:
   - Current activity display
   - Start/Stop tracking button
   - Recent activities list

3. Click "Start Tracking" to begin monitoring your activities

4. The application will automatically:
   - Track active windows and applications
   - Record activity durations
   - Detect idle periods
   - Save activity history

## Configuration

The application can be configured by editing the YAML files in the `config` directory:

### default_config.yaml
- Application settings
- Monitoring thresholds
- Storage options
- UI preferences

### logging_config.yaml
- Logging levels
- Log file location
- Log rotation settings

## Development

1. Install development dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Code formatting:
```bash
black .
isort .
```

4. Type checking:
```bash
mypy src
```

5. Linting:
```bash
pylint src
```

## Project Structure

```
time-tracker/
├── src/
│   ├── core/           # Core tracking functionality
│   ├── monitors/       # System and input monitoring
│   ├── ui/            # User interface
│   └── utils/         # Utilities and helpers
├── tests/             # Test suite
├── config/            # Configuration files
└── docs/             # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure code quality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Python and Tkinter
- Uses PyObjC for macOS integration
- Inspired by various time tracking tools

## Future Plans

- Cross-platform support (Windows, Linux)
- Activity categorization
- Data visualization
- Export capabilities
- Plugin system
