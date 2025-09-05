"""
Script to create the logs directory.
"""
import os
import sys

def create_logs_dir():
    """
    Create the logs directory if it doesn't exist.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, 'logs')
    
    if not os.path.exists(logs_dir):
        try:
            os.makedirs(logs_dir)
            print(f"Created logs directory at {logs_dir}")
        except Exception as e:
            print(f"Error creating logs directory: {e}")
            return False
    else:
        print(f"Logs directory already exists at {logs_dir}")
    
    return True

if __name__ == '__main__':
    success = create_logs_dir()
    sys.exit(0 if success else 1)
