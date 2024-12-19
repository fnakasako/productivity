import sys
import logging.config
import yaml
from pathlib import Path
from ui.main_window import MainWindow

def main():
    """Main entry point for the time tracker application."""
    try:
        # Get the application root directory
        app_dir = Path(__file__).parent.parent
        
        # Load configuration
        config_path = app_dir / 'config' / 'default_config.yaml'
        with config_path.open('r') as f:
            config = yaml.safe_load(f)
            
        # Setup logging
        logging_config_path = app_dir / 'config' / 'logging_config.yaml'
        with logging_config_path.open('r') as f:
            logging_config = yaml.safe_load(f)
            # Expand ~ in log file path
            if 'file' in logging_config['handlers']:
                logging_config['handlers']['file']['filename'] = \
                    str(Path(logging_config['handlers']['file']['filename']).expanduser())
            logging.config.dictConfig(logging_config)
            
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {config['app']['name']} v{config['app']['version']}")
        
        # Create and run main window
        window = MainWindow(config)
        window.run()
        
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
