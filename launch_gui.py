#!/usr/bin/env python3
"""
Policy Manual Generation System - GUI Launcher
Simple launcher script for the GUI application.
"""

import sys
import os

def main():
    """Launch the GUI application"""
    try:
        # Import and run the GUI
        from gui_app import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Error importing GUI application: {e}")
        print("Make sure all required dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting GUI application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🚀 Launching Policy Manual Generation System GUI...")
    main()