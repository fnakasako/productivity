#!/usr/bin/env python3
"""
Setup script to initialize TimeTracker configuration.
Creates necessary directories and configuration files in the user's home directory.
"""

import os
import sys
import shutil
from pathlib import Path
import logging

def setup_logging():
    """Setup basic logging for the setup process."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def create_config_directory(logger):
    """Create the configuration directory in user's home."""
    config_dir = Path.home() / '.timetracker'
    config_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created configuration directory: {config_dir}")
    return config_dir

def copy_config_files(src_dir, dest_dir, logger):
    """Copy configuration files from package to user's directory."""
    try:
        # Copy default configuration
        default_config = src_dir / 'config' / 'default_config.yaml'
        user_config = dest_dir / 'config.yaml'
        
        if not user_config.exists():
            shutil.copy2(default_config, user_config)
            logger.info(f"Created user configuration: {user_config}")
        else:
            logger.info(f"User configuration already exists: {user_config}")
        
        # Copy logging configuration
        logging_config = src_dir / 'config' / 'logging_config.yaml'
        user_logging = dest_dir / 'logging.yaml'
        
        if not user_logging.exists():
            shutil.copy2(logging_config, user_logging)
            logger.info(f"Created logging configuration: {user_logging}")
        else:
            logger.info(f"Logging configuration already exists: {user_logging}")
            
    except Exception as e:
        logger.error(f"Error copying configuration files: {e}")
        raise

def create_data_directory(config_dir, logger):
    """Create directory for activity data."""
    data_dir = config_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    logger.info(f"Created data directory: {data_dir}")
    return data_dir

def main():
    """Main setup function."""
    logger = setup_logging()
    logger.info("Starting TimeTracker configuration setup...")
    
    try:
        # Get package directory
        package_dir = Path(__file__).parent.parent
        
        # Create configuration directory
        config_dir = create_config_directory(logger)
        
        # Copy configuration files
        copy_config_files(package_dir, config_dir, logger)
        
        # Create data directory
        data_dir = create_data_directory(config_dir, logger)
        
        logger.info("TimeTracker configuration setup completed successfully!")
        logger.info("\nYou can now:")
        logger.info(f"1. Edit your configuration at: {config_dir}/config.yaml")
        logger.info(f"2. Edit logging settings at: {config_dir}/logging.yaml")
        logger.info("3. Start TimeTracker by running: timetracker")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
