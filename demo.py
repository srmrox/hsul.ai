#!/usr/bin/env python3
"""
Policy Manual Generation System - Demo Script
Demonstrates the complete GUI workflow with sample data.
"""

import os
import json
from datetime import datetime

def create_sample_organogram():
    """Create a sample organogram for demonstration."""
    organogram = {
        "company_name": "Demo Corporation",
        "manuals": {
            "hr": {
                "name": "Human Resources Policy Manual",
                "description": "Comprehensive HR policies covering recruitment, benefits, performance management, and workplace conduct",
                "target_roles": ["hr_manager", "managers", "employees"]
            },
            "it": {
                "name": "IT Security Policy Manual", 
                "description": "Information technology security policies including data protection, access control, and incident response",
                "target_roles": ["it_admin", "managers", "all_employees"]
            },
            "finance": {
                "name": "Financial Policies Manual",
                "description": "Financial procedures covering budgeting, expense management, and audit compliance",
                "target_roles": ["finance_manager", "accountants", "managers"]
            }
        },
        "roles": {
            "hr_manager": "Human Resources Manager",
            "it_admin": "IT Administrator", 
            "finance_manager": "Finance Manager",
            "managers": "Department Managers",
            "employees": "All Employees",
            "all_employees": "All Company Staff",
            "accountants": "Accounting Staff"
        }
    }
    
    with open("demo_organogram.json", "w", encoding='utf-8') as f:
        json.dump(organogram, f, indent=2, ensure_ascii=False)
    
    print("✅ Created demo_organogram.json")
    return "demo_organogram.json"

def create_sample_input():
    """Create sample input.txt for batch processing."""
    sample_manuals = [
        "Human Resources Policy Manual - Comprehensive HR policies and procedures",
        "IT Security Policy Manual - Information technology security guidelines", 
        "Financial Procedures Manual - Financial controls and processes"
    ]
    
    with open("input.txt", "w", encoding='utf-8') as f:
        for manual in sample_manuals:
            f.write(manual + "\n")
    
    print("✅ Created input.txt with sample manuals")

def setup_demo_environment():
    """Set up complete demo environment."""
    print("🚀 Setting up Policy Manual Generation Demo")
    print("=" * 60)
    
    # Create sample files
    organogram_file = create_sample_organogram()
    create_sample_input()
    
    # Create output directories
    os.makedirs("generated_documents", exist_ok=True)
    os.makedirs("demo_output", exist_ok=True)
    
    print("✅ Created output directories")
    
    # Show demo instructions
    print(f"\n📋 Demo Setup Complete!")
    print(f"=" * 40)
    print(f"🏢 Company: Demo Corporation")
    print(f"📄 Sample Organogram: {organogram_file}")
    print(f"📚 Available Manuals: HR, IT, Finance")
    print(f"📁 Output Directory: generated_documents/")
    
    print(f"\n🎯 Next Steps:")
    print(f"1. Launch GUI: python gui_app.py")
    print(f"2. Upload organogram: {organogram_file}")
    print(f"3. Select manuals to generate")
    print(f"4. Follow the 4-stage workflow")
    
    print(f"\n💡 Alternative: Command Line Demo")
    print(f"1. Stage 1: python init_project.py --organogram {organogram_file} --manuals hr it")
    print(f"2. Stage 2: python project_expansion.py")
    print(f"3. Stage 3: python generate_content.py (requires LM Studio)")
    print(f"4. Stage 4: python generate_documents.py --output demo_output")
    
    return organogram_file

def run_gui_demo():
    """Launch the GUI with demo data."""
    print("\n🚀 Launching GUI Demo...")
    
    try:
        from gui_app import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Error importing GUI: {e}")
    except Exception as e:
        print(f"❌ Error running GUI: {e}")

def show_system_status():
    """Show current system status and files."""
    print("\n📊 System Status")
    print("=" * 30)
    
    # Check for required files
    files_to_check = [
        ("gui_app.py", "GUI Application"),
        ("init_project.py", "Stage 1 - Project Initiation"),
        ("project_expansion.py", "Stage 2 - Project Expansion"), 
        ("generate_content.py", "Stage 3 - Content Generation"),
        ("generate_documents.py", "Stage 4 - Document Generation"),
        ("demo_organogram.json", "Demo Organogram File")
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - Missing: {filename}")
    
    # Check for dependencies
    print(f"\n📦 Dependencies")
    dependencies = [
        ("tkinter", "GUI Framework"),
        ("docx", "Word Document Generation"),
        ("requests", "HTTP Client for LM Studio")
    ]
    
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {description} ({module})")
        except ImportError:
            print(f"❌ {description} ({module}) - Run: pip install {module}")
    
    # Show project structure
    print(f"\n📁 Project Files")
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]
    
    if py_files:
        print(f"   Python Scripts: {len(py_files)}")
        for f in sorted(py_files)[:5]:  # Show first 5
            print(f"   - {f}")
    
    if json_files:
        print(f"   Configuration Files: {len(json_files)}")
        for f in sorted(json_files):
            print(f"   - {f}")

def main():
    """Main demo function."""
    print("🎯 Policy Manual Generation System - Demo Setup")
    print("=" * 60)
    print("This script sets up a complete demo environment for the")
    print("Policy Manual Generation System with GUI interface.")
    print("")
    
    # Show current status
    show_system_status()
    
    # Setup demo environment
    print("")
    organogram_file = setup_demo_environment()
    
    # Ask user what to do next
    print(f"\n🎮 What would you like to do?")
    print(f"1. Launch GUI Demo")
    print(f"2. Show System Status Only") 
    print(f"3. Create Demo Files Only")
    print(f"4. Exit")
    
    try:
        choice = input(f"\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            run_gui_demo()
        elif choice == "2":
            show_system_status()
        elif choice == "3":
            print("✅ Demo files created successfully!")
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Run the script again.")
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()