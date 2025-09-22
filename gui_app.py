#!/usr/bin/env python3
"""
Policy Manual Generation GUI Application
A comprehensive graphical interface for the 4-stage policy manual generation system.

This GUI provides:
- Stage-by-stage workflow management
- Progress tracking and status indicators  
- File input/output management
- Real-time process monitoring
- Integration with all backend scripts

Stages:
1. Project Initiation - Organogram upload, manual selection
2. Project Expansion - Section editing, notes management
3. Content Generation - AI content generation with progress tracking
4. Document Generation - Word document creation and download

Author: Policy Manual Generation System
Date: September 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from config_editor_gui import ConfigEditorGUI

class PolicyManualGUI:
    """Main GUI application for policy manual generation system."""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.initialize_variables()
        self.create_widgets()
        self.load_project_state()
        
    def setup_window(self):
        """Configure the main window."""
        self.root.title("Policy Manual Generation System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configure style for modern look
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
    def initialize_variables(self):
        """Initialize application variables and state."""
        self.project_dir = os.getcwd()
        self.config_file = os.path.join(self.project_dir, "config.json")
        self.project_state = {
            "stage": 0,
            "stage_name": "not_started",
            "stages_completed": [],
            "current_files": {},
            "progress": {}
        }
        
        # GUI state variables
        self.organogram_file = tk.StringVar()
        self.selected_manuals = tk.StringVar()
        self.stage_status = [tk.StringVar(value="⏳ Not Started") for _ in range(4)]
        self.current_stage = tk.IntVar(value=0)
        
    def create_widgets(self):
        """Create the main GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="🏢 Policy Manual Generation System", 
            font=('Arial', 18, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Progress overview
        self.create_progress_overview(title_frame)
        
        # Create notebook for stages
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create stage tabs
        self.create_stage_tabs()
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_progress_overview(self, parent):
        """Create the progress overview panel."""
        progress_frame = ttk.LabelFrame(parent, text="📊 Process Overview")
        progress_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        
        # Stage indicators
        stages = [
            ("Stage 1: Project Initiation", "🚀"),
            ("Stage 2: Project Expansion", "📝"),
            ("Stage 3: Content Generation", "🤖"),
            ("Stage 4: Document Generation", "📄")
        ]
        
        self.progress_labels = []
        for i, (stage_name, icon) in enumerate(stages):
            frame = ttk.Frame(progress_frame)
            frame.pack(fill=tk.X, pady=2, padx=5)
            
            icon_label = ttk.Label(frame, text=icon, font=('Arial', 12))
            icon_label.pack(side=tk.LEFT)
            
            status_label = ttk.Label(
                frame, 
                textvariable=self.stage_status[i], 
                font=('Arial', 9)
            )
            status_label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.progress_labels.append(status_label)
        
        # Overall progress bar
        ttk.Label(progress_frame, text="Overall Progress:", font=('Arial', 9, 'bold')).pack(pady=(10, 2))
        self.overall_progress = ttk.Progressbar(
            progress_frame, 
            mode='determinate', 
            length=150
        )
        self.overall_progress.pack(pady=(0, 5))
        
        self.progress_text = ttk.Label(progress_frame, text="0% Complete")
        self.progress_text.pack()
        
    def create_stage_tabs(self):
        """Create tabs for each stage."""
        self.stage_frames = []
        
        # Stage 1: Project Initiation
        stage1_frame = ttk.Frame(self.notebook)
        self.notebook.add(stage1_frame, text="🚀 Stage 1: Project Initiation")
        self.create_stage1_widgets(stage1_frame)
        self.stage_frames.append(stage1_frame)
        
        # Stage 2: Project Expansion
        stage2_frame = ttk.Frame(self.notebook)
        self.notebook.add(stage2_frame, text="📝 Stage 2: Project Expansion")
        self.create_stage2_widgets(stage2_frame)
        self.stage_frames.append(stage2_frame)
        
        # Stage 3: Content Generation
        stage3_frame = ttk.Frame(self.notebook)
        self.notebook.add(stage3_frame, text="🤖 Stage 3: Content Generation")
        self.create_stage3_widgets(stage3_frame)
        self.stage_frames.append(stage3_frame)
        
        # Stage 4: Document Generation
        stage4_frame = ttk.Frame(self.notebook)
        self.notebook.add(stage4_frame, text="📄 Stage 4: Document Generation")
        self.create_stage4_widgets(stage4_frame)
        self.stage_frames.append(stage4_frame)
        
        # Configuration Tab
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configuration")
        self.create_config_widgets(config_frame)
        
    def create_stage1_widgets(self, parent):
        """Create Stage 1: Project Initiation interface."""
        # Main content frame
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        desc_frame = ttk.LabelFrame(content_frame, text="📋 Stage 1 Overview")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = """Stage 1: Project Initiation
        
• Upload organogram JSON file with roles and responsibilities
• Select which policy manuals to generate
• Initialize project structure and generate table of contents
• Set up variables for personalization
        
This stage prepares the foundation for your policy manual generation project."""
        
        ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # File input section
        file_frame = ttk.LabelFrame(content_frame, text="📁 File Input")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Organogram file selection
        organogram_frame = ttk.Frame(file_frame)
        organogram_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(organogram_frame, text="Organogram File:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(organogram_frame)
        file_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.organogram_entry = ttk.Entry(
            file_select_frame, 
            textvariable=self.organogram_file,
            state='readonly'
        )
        self.organogram_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            file_select_frame, 
            text="Browse...", 
            command=self.browse_organogram_file
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Manual selection
        manual_frame = ttk.LabelFrame(content_frame, text="📚 Manual Selection")
        manual_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(
            manual_frame, 
            text="Select policy manuals to generate:", 
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Manual checkboxes (will be populated dynamically)
        self.manual_checkbox_frame = ttk.Frame(manual_frame)
        self.manual_checkbox_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.manual_vars = {}  # Will hold checkbox variables
        
        # Control buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            button_frame,
            text="🔄 Load Available Manuals",
            command=self.load_available_manuals
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="▶️ Start Stage 1",
            command=self.run_stage1,
            style='Accent.TButton'
        ).pack(side=tk.RIGHT)
        
        # Output/log area
        log_frame = ttk.LabelFrame(content_frame, text="📝 Stage 1 Output")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.stage1_log = scrolledtext.ScrolledText(
            log_frame, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.stage1_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_stage2_widgets(self, parent):
        """Create Stage 2: Project Expansion interface."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        desc_frame = ttk.LabelFrame(content_frame, text="📋 Stage 2 Overview")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = """Stage 2: Project Expansion
        
• Review and edit generated section structures
• Add custom notes and requirements for each manual
• Customize content parameters and guidelines
• Prepare detailed specifications for content generation
        
This stage allows you to fine-tune the project before AI content generation."""
        
        ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Manual selection for editing
        select_frame = ttk.LabelFrame(content_frame, text="📚 Manual Selection for Editing")
        select_frame.pack(fill=tk.X, pady=(0, 20))
        
        manual_select_frame = ttk.Frame(select_frame)
        manual_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(manual_select_frame, text="Select Manual to Edit:").pack(anchor=tk.W)
        
        self.stage2_manual_combo = ttk.Combobox(
            manual_select_frame,
            state='readonly',
            width=50
        )
        self.stage2_manual_combo.pack(pady=(5, 0))
        self.stage2_manual_combo.bind('<<ComboboxSelected>>', self.load_manual_sections)
        
        # Section editing area
        edit_frame = ttk.LabelFrame(content_frame, text="✏️ Section Editing")
        edit_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Split into sections list and editor
        edit_paned = ttk.PanedWindow(edit_frame, orient=tk.HORIZONTAL)
        edit_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sections list
        sections_frame = ttk.Frame(edit_paned)
        edit_paned.add(sections_frame, weight=1)
        
        ttk.Label(sections_frame, text="Sections:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.sections_listbox = tk.Listbox(sections_frame, height=15)
        self.sections_listbox.pack(fill=tk.BOTH, expand=True)
        self.sections_listbox.bind('<<ListboxSelect>>', self.on_section_select)
        
        # Section editor
        editor_frame = ttk.Frame(edit_paned)
        edit_paned.add(editor_frame, weight=2)
        
        ttk.Label(editor_frame, text="Section Details:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.section_editor = scrolledtext.ScrolledText(
            editor_frame,
            height=15,
            wrap=tk.WORD
        )
        self.section_editor.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="💾 Save Section Changes",
            command=self.save_section_changes
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="▶️ Complete Stage 2",
            command=self.run_stage2
        ).pack(side=tk.RIGHT)
        
    def create_stage3_widgets(self, parent):
        """Create Stage 3: Content Generation interface."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        desc_frame = ttk.LabelFrame(content_frame, text="📋 Stage 3 Overview")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = """Stage 3: Content Generation
        
• Generate AI-powered content for each policy section
• Apply customizations and notes from Stage 2
• Create structured JSON content files
• Monitor generation progress and quality
        
This stage produces the actual policy content using AI assistance."""
        
        ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Generation controls
        control_frame = ttk.LabelFrame(content_frame, text="⚙️ Generation Controls")
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        controls_grid = ttk.Frame(control_frame)
        controls_grid.pack(padx=10, pady=10)
        
        # Manual selection
        ttk.Label(controls_grid, text="Generate Content For:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.stage3_manual_combo = ttk.Combobox(
            controls_grid,
            values=["All Manuals", "Selected Manual Only"],
            state='readonly',
            width=30
        )
        self.stage3_manual_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        self.stage3_manual_combo.set("All Manuals")
        
        # Progress tracking
        progress_frame = ttk.LabelFrame(content_frame, text="📊 Generation Progress")
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        prog_content = ttk.Frame(progress_frame)
        prog_content.pack(padx=10, pady=10)
        
        self.generation_progress = ttk.Progressbar(
            prog_content,
            mode='determinate',
            length=300
        )
        self.generation_progress.pack(pady=5)
        
        self.generation_status = ttk.Label(prog_content, text="Ready to generate content")
        self.generation_status.pack(pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Button(
            button_frame,
            text="▶️ Start Content Generation",
            command=self.run_stage3
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="⏸️ Pause Generation",
            command=self.pause_stage3,
            state=tk.DISABLED
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Output preview
        preview_frame = ttk.LabelFrame(content_frame, text="👁️ Content Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stage3_preview = scrolledtext.ScrolledText(
            preview_frame,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.stage3_preview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_stage4_widgets(self, parent):
        """Create Stage 4: Document Generation interface."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Description
        desc_frame = ttk.LabelFrame(content_frame, text="📋 Stage 4 Overview")
        desc_frame.pack(fill=tk.X, pady=(0, 20))
        
        desc_text = """Stage 4: Document Generation
        
• Convert JSON content to professional Word documents
• Apply formatting, styles, and corporate branding
• Generate table of contents and page numbers
• Create final, publication-ready policy manuals
        
This final stage produces polished documents ready for distribution."""
        
        ttk.Label(desc_frame, text=desc_text, justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Generation options
        options_frame = ttk.LabelFrame(content_frame, text="⚙️ Document Options")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(padx=10, pady=10)
        
        # Output directory
        ttk.Label(options_grid, text="Output Directory:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(options_grid)
        output_frame.grid(row=0, column=1, sticky=tk.W + tk.E, padx=(10, 0), pady=5)
        
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "generated_documents"))
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_dir, width=40)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(
            output_frame,
            text="Browse...",
            command=self.browse_output_directory
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Document format options
        ttk.Label(options_grid, text="Document Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.doc_format = tk.StringVar(value="Word Document (.docx)")
        format_combo = ttk.Combobox(
            options_grid,
            textvariable=self.doc_format,
            values=["Word Document (.docx)"],
            state='readonly',
            width=30
        )
        format_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Generated documents list
        docs_frame = ttk.LabelFrame(content_frame, text="📄 Generated Documents")
        docs_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Document list with details
        self.docs_tree = ttk.Treeview(
            docs_frame,
            columns=('Status', 'Size', 'Modified'),
            show='tree headings',
            height=8
        )
        
        self.docs_tree.heading('#0', text='Document Name')
        self.docs_tree.heading('Status', text='Status')
        self.docs_tree.heading('Size', text='Size')
        self.docs_tree.heading('Modified', text='Last Modified')
        
        self.docs_tree.column('#0', width=250)
        self.docs_tree.column('Status', width=100)
        self.docs_tree.column('Size', width=80)
        self.docs_tree.column('Modified', width=120)
        
        self.docs_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="🔄 Refresh List",
            command=self.refresh_documents_list
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            button_frame,
            text="📂 Open Output Folder",
            command=self.open_output_folder
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="▶️ Generate Documents",
            command=self.run_stage4
        ).pack(side=tk.RIGHT)
        
    def create_config_widgets(self, parent):
        """Create Configuration interface."""
        # Main content frame with scrolling
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title and description
        title_label = ttk.Label(
            main_frame,
            text="Company Configuration",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        desc_label = ttk.Label(
            main_frame,
            text="Manage your company information used across all policy manuals.\nThis data is used for variable substitution in generated documents.",
            font=('Arial', 10),
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20))
        
        # Configuration editor frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration Editor")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Embed the configuration editor
        try:
            self.config_editor = ConfigEditorGUI(config_frame)
        except Exception as e:
            error_label = ttk.Label(
                config_frame,
                text=f"Error loading configuration editor: {e}",
                foreground='red'
            )
            error_label.pack(pady=20)
        
        # Quick actions frame
        actions_frame = ttk.LabelFrame(main_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        actions_grid = ttk.Frame(actions_frame)
        actions_grid.pack(padx=10, pady=10)
        
        # Buttons for common actions
        ttk.Button(
            actions_grid,
            text="🔧 Open Config Editor",
            command=self.open_config_editor_standalone,
            width=25
        ).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(
            actions_grid,
            text="✅ Validate Configuration",
            command=self.validate_configuration,
            width=25
        ).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(
            actions_grid,
            text="📄 Export Config",
            command=self.export_configuration,
            width=25
        ).grid(row=1, column=0, padx=5, pady=5)
        
        ttk.Button(
            actions_grid,
            text="📥 Import Config",
            command=self.import_configuration,
            width=25
        ).grid(row=1, column=1, padx=5, pady=5)
    
    def open_config_editor_standalone(self):
        """Open the configuration editor in a separate window."""
        try:
            import subprocess
            subprocess.Popen([sys.executable, 'config_editor_gui.py'])
            self.log_message("Opened standalone configuration editor")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open configuration editor: {e}")
    
    def validate_configuration(self):
        """Validate the current configuration."""
        try:
            from config_manager import get_config_manager
            config_manager = get_config_manager()
            validation = config_manager.validate()
            
            if validation.is_valid:
                if validation.warnings:
                    message = f"Configuration is valid!\n\nWarnings:\n" + "\n".join(validation.warnings)
                    messagebox.showwarning("Validation Result", message)
                else:
                    messagebox.showinfo("Validation Result", "✅ Configuration is valid!")
            else:
                message = f"Configuration has errors:\n\n" + "\n".join(validation.errors)
                messagebox.showerror("Validation Result", message)
                
            self.log_message("Configuration validation completed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to validate configuration: {e}")
    
    def export_configuration(self):
        """Export configuration to a file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Configuration",
                defaultextension=".yaml",
                filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
            )
            
            if file_path:
                import shutil
                shutil.copy("config/company.yaml", file_path)
                messagebox.showinfo("Export Complete", f"Configuration exported to:\n{file_path}")
                self.log_message(f"Configuration exported to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export configuration: {e}")
    
    def import_configuration(self):
        """Import configuration from a file."""
        try:
            file_path = filedialog.askopenfilename(
                title="Import Configuration",
                filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")]
            )
            
            if file_path:
                result = messagebox.askyesno(
                    "Import Configuration",
                    "This will replace your current configuration. Continue?"
                )
                
                if result:
                    import shutil
                    shutil.copy(file_path, "config/company.yaml")
                    messagebox.showinfo("Import Complete", "Configuration imported successfully!")
                    self.log_message(f"Configuration imported from {os.path.basename(file_path)}")
                    
                    # Reload the embedded editor if it exists
                    try:
                        if hasattr(self, 'config_editor'):
                            self.config_editor.load_configuration()
                    except:
                        pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import configuration: {e}")
        
    def create_status_bar(self, parent):
        """Create the status bar at the bottom."""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_text = ttk.Label(
            self.status_frame,
            text="Ready - Welcome to Policy Manual Generation System",
            relief=tk.SUNKEN
        )
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Current time
        self.time_label = ttk.Label(self.status_frame, text="")
        self.time_label.pack(side=tk.RIGHT)
        self.update_time()
        
    def update_time(self):
        """Update the time display."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def load_project_state(self):
        """Load the current project state from config.json."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.project_state.update(config)
                self.update_progress_display()
                self.log_message("Project state loaded successfully")
            else:
                self.log_message("No existing project found - starting fresh")
        except Exception as e:
            self.log_message(f"Error loading project state: {str(e)}")
            
    def update_progress_display(self):
        """Update the progress indicators based on current state."""
        stage = self.project_state.get('stage', 0)
        completed_stages = self.project_state.get('stages_completed', [])
        
        # Update stage status indicators
        for i in range(4):
            if i + 1 in completed_stages:
                self.stage_status[i].set("✅ Completed")
            elif i + 1 == stage:
                self.stage_status[i].set("🔄 In Progress")
            else:
                self.stage_status[i].set("⏳ Not Started")
        
        # Update overall progress
        progress = (len(completed_stages) / 4) * 100
        self.overall_progress['value'] = progress
        self.progress_text.config(text=f"{progress:.0f}% Complete")
        
    def log_message(self, message, widget=None):
        """Log a message to the specified widget or status bar."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        if widget:
            widget.config(state=tk.NORMAL)
            widget.insert(tk.END, formatted_message + "\n")
            widget.see(tk.END)
            widget.config(state=tk.DISABLED)
        
        self.status_text.config(text=message)
        print(formatted_message)  # Also log to console
        
    # Stage 1 Methods
    def browse_organogram_file(self):
        """Browse for organogram JSON file."""
        filename = filedialog.askopenfilename(
            title="Select Organogram File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.project_dir
        )
        
        if filename:
            self.organogram_file.set(filename)
            self.load_available_manuals()
            self.log_message(f"Organogram file selected: {os.path.basename(filename)}")
            
    def load_available_manuals(self):
        """Load available manuals from the organogram file."""
        organogram_path = self.organogram_file.get()
        if not organogram_path or not os.path.exists(organogram_path):
            messagebox.showerror("Error", "Please select a valid organogram file first.")
            return
            
        try:
            with open(organogram_path, 'r', encoding='utf-8') as f:
                organogram = json.load(f)
            
            # Clear existing checkboxes
            for widget in self.manual_checkbox_frame.winfo_children():
                widget.destroy()
                
            self.manual_vars.clear()
            
            # Create checkboxes for each manual type
            manuals = organogram.get('manuals', {})
            
            if not manuals:
                ttk.Label(
                    self.manual_checkbox_frame,
                    text="No manuals found in organogram file.",
                    foreground='red'
                ).pack()
                return
                
            row = 0
            col = 0
            for manual_key, manual_info in manuals.items():
                var = tk.BooleanVar()
                self.manual_vars[manual_key] = var
                
                checkbox = ttk.Checkbutton(
                    self.manual_checkbox_frame,
                    text=f"{manual_info.get('name', manual_key)} ({manual_key})",
                    variable=var
                )
                checkbox.grid(row=row, column=col, sticky=tk.W, padx=10, pady=2)
                
                col += 1
                if col > 1:  # Two columns
                    col = 0
                    row += 1
                    
            self.log_message(f"Loaded {len(manuals)} available manuals")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load organogram file: {str(e)}")
            self.log_message(f"Error loading organogram: {str(e)}")
            
    def run_stage1(self):
        """Execute Stage 1: Project Initiation."""
        # Validate inputs
        if not self.organogram_file.get():
            messagebox.showerror("Error", "Please select an organogram file.")
            return
            
        selected_manuals = [key for key, var in self.manual_vars.items() if var.get()]
        if not selected_manuals:
            messagebox.showerror("Error", "Please select at least one manual to generate.")
            return
            
        # Disable UI during processing
        self.notebook.tab(0, state='disabled')
        
        # Run Stage 1 in background thread
        def run_stage1_thread():
            try:
                self.log_message("Starting Stage 1: Project Initiation...", self.stage1_log)
                
                # Prepare command
                cmd = [
                    sys.executable, "init_project.py",
                    "--organogram", self.organogram_file.get(),
                    "--manuals"] + selected_manuals
                
                # Run the command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.project_dir
                )
                
                # Stream output
                if process.stdout:
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            self.root.after(0, lambda msg=output.strip(): 
                                          self.log_message(msg, self.stage1_log))
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.root.after(0, lambda: self.on_stage1_complete(selected_manuals))
                else:
                    self.root.after(0, lambda: self.on_stage1_error("Stage 1 failed with errors"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.on_stage1_error(str(e)))
                
        threading.Thread(target=run_stage1_thread, daemon=True).start()
        
    def on_stage1_complete(self, selected_manuals):
        """Handle Stage 1 completion."""
        self.project_state['stage'] = 1
        self.project_state['stages_completed'].append(1)
        self.project_state['selected_manuals'] = selected_manuals
        
        self.update_progress_display()
        self.populate_stage2_manuals()
        self.notebook.tab(0, state='normal')
        self.notebook.select(1)  # Switch to Stage 2 tab
        
        self.log_message("✅ Stage 1 completed successfully!", self.stage1_log)
        messagebox.showinfo("Success", "Stage 1: Project Initiation completed successfully!")
        
    def on_stage1_error(self, error_msg):
        """Handle Stage 1 error."""
        self.notebook.tab(0, state='normal')
        self.log_message(f"❌ Stage 1 failed: {error_msg}", self.stage1_log)
        messagebox.showerror("Error", f"Stage 1 failed: {error_msg}")
        
    # Stage 2 Methods
    def populate_stage2_manuals(self):
        """Populate Stage 2 manual selection combo."""
        try:
            # Look for generated sections files
            sections_files = []
            for file in os.listdir(self.project_dir):
                if file.startswith("sections_") and file.endswith(".json"):
                    manual_name = file.replace("sections_", "").replace(".json", "")
                    sections_files.append(manual_name)
            
            self.stage2_manual_combo['values'] = sections_files
            if sections_files:
                self.stage2_manual_combo.set(sections_files[0])
                self.load_manual_sections()
                
        except Exception as e:
            self.log_message(f"Error populating Stage 2 manuals: {str(e)}")
            
    def load_manual_sections(self, event=None):
        """Load sections for the selected manual."""
        manual_name = self.stage2_manual_combo.get()
        if not manual_name:
            return
            
        try:
            sections_file = f"sections_{manual_name}.json"
            if os.path.exists(sections_file):
                with open(sections_file, 'r', encoding='utf-8') as f:
                    self.current_sections = json.load(f)
                
                # Populate sections list
                self.sections_listbox.delete(0, tk.END)
                self.section_keys = []
                
                for section_key, section_data in self.current_sections.items():
                    if isinstance(section_data, dict) and 'title' in section_data:
                        display_name = f"{section_key}: {section_data['title']}"
                        self.sections_listbox.insert(tk.END, display_name)
                        self.section_keys.append(section_key)
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sections: {str(e)}")
            
    def on_section_select(self, event):
        """Handle section selection in listbox."""
        selection = self.sections_listbox.curselection()
        if not selection:
            return
            
        section_index = selection[0]
        section_key = self.section_keys[section_index]
        section_data = self.current_sections[section_key]
        
        # Display section details in editor
        self.section_editor.delete(1.0, tk.END)
        
        if isinstance(section_data, dict):
            formatted_content = json.dumps(section_data, indent=2, ensure_ascii=False)
            self.section_editor.insert(1.0, formatted_content)
        else:
            self.section_editor.insert(1.0, str(section_data))
            
        self.current_section_key = section_key
        
    def save_section_changes(self):
        """Save changes to the current section."""
        if not hasattr(self, 'current_section_key'):
            messagebox.showwarning("Warning", "Please select a section to save.")
            return
            
        try:
            # Get updated content from editor
            content = self.section_editor.get(1.0, tk.END).strip()
            updated_data = json.loads(content)
            
            # Update the sections data
            self.current_sections[self.current_section_key] = updated_data
            
            # Save back to file
            manual_name = self.stage2_manual_combo.get()
            sections_file = f"sections_{manual_name}.json"
            
            with open(sections_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_sections, f, indent=2, ensure_ascii=False)
                
            self.log_message(f"Saved changes to section: {self.current_section_key}")
            messagebox.showinfo("Success", "Section changes saved successfully!")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Invalid JSON format: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save section: {str(e)}")
            
    def run_stage2(self):
        """Execute Stage 2: Project Expansion."""
        try:
            self.log_message("Starting Stage 2: Project Expansion...")
            
            # Run project_expansion.py
            cmd = [sys.executable, "project_expansion.py"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                self.project_state['stage'] = 2
                if 2 not in self.project_state['stages_completed']:
                    self.project_state['stages_completed'].append(2)
                    
                self.update_progress_display()
                self.populate_stage3_manuals()
                self.notebook.select(2)  # Switch to Stage 3 tab
                
                messagebox.showinfo("Success", "Stage 2: Project Expansion completed successfully!")
                self.log_message("✅ Stage 2 completed successfully!")
            else:
                raise Exception(result.stderr or "Stage 2 failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Stage 2 failed: {str(e)}")
            self.log_message(f"❌ Stage 2 failed: {str(e)}")
            
    # Stage 3 Methods
    def populate_stage3_manuals(self):
        """Populate Stage 3 manual options."""
        # This will be populated with available manuals for content generation
        pass
        
    def run_stage3(self):
        """Execute Stage 3: Content Generation."""
        self.log_message("Starting Stage 3: Content Generation...")
        self.generation_status.config(text="Generating content...")
        
        def run_stage3_thread():
            try:
                cmd = [sys.executable, "generate_content.py"]
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=self.project_dir
                )
                
                # Update progress periodically
                progress = 0
                while process.poll() is None:
                    progress = min(progress + 10, 90)
                    self.root.after(0, lambda p=progress: self.generation_progress.config(value=p))
                    self.root.after(0, lambda: self.generation_status.config(text=f"Generating content... {progress}%"))
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        continue
                
                if process.returncode == 0:
                    self.root.after(0, self.on_stage3_complete)
                else:
                    self.root.after(0, lambda: self.on_stage3_error("Content generation failed"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.on_stage3_error(str(e)))
                
        threading.Thread(target=run_stage3_thread, daemon=True).start()
        
    def on_stage3_complete(self):
        """Handle Stage 3 completion."""
        self.generation_progress.config(value=100)
        self.generation_status.config(text="Content generation completed!")
        
        self.project_state['stage'] = 3
        if 3 not in self.project_state['stages_completed']:
            self.project_state['stages_completed'].append(3)
            
        self.update_progress_display()
        self.refresh_documents_list()
        self.notebook.select(3)  # Switch to Stage 4 tab
        
        messagebox.showinfo("Success", "Stage 3: Content Generation completed successfully!")
        self.log_message("✅ Stage 3 completed successfully!")
        
    def on_stage3_error(self, error_msg):
        """Handle Stage 3 error."""
        self.generation_progress.config(value=0)
        self.generation_status.config(text="Content generation failed!")
        messagebox.showerror("Error", f"Stage 3 failed: {error_msg}")
        self.log_message(f"❌ Stage 3 failed: {error_msg}")
        
    def pause_stage3(self):
        """Pause Stage 3 content generation."""
        # This would require more sophisticated process management
        self.log_message("Pause functionality not yet implemented")
        
    # Stage 4 Methods
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get()
        )
        
        if directory:
            self.output_dir.set(directory)
            self.log_message(f"Output directory set: {directory}")
            
    def refresh_documents_list(self):
        """Refresh the generated documents list."""
        # Clear existing items
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)
            
        output_path = self.output_dir.get()
        if not os.path.exists(output_path):
            return
            
        try:
            for filename in os.listdir(output_path):
                if filename.endswith('.docx'):
                    file_path = os.path.join(output_path, filename)
                    stat = os.stat(file_path)
                    
                    size = f"{stat.st_size / 1024:.1f} KB"
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                    
                    self.docs_tree.insert(
                        '',
                        'end',
                        text=filename,
                        values=('Generated', size, modified)
                    )
                    
        except Exception as e:
            self.log_message(f"Error refreshing documents list: {str(e)}")
            
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        output_path = self.output_dir.get()
        if os.path.exists(output_path):
            os.startfile(output_path)  # Windows
        else:
            messagebox.showwarning("Warning", "Output directory does not exist.")
            
    def run_stage4(self):
        """Execute Stage 4: Document Generation."""
        try:
            self.log_message("Starting Stage 4: Document Generation...")
            
            # Ensure output directory exists
            os.makedirs(self.output_dir.get(), exist_ok=True)
            
            # Run generate_documents.py
            cmd = [sys.executable, "generate_documents.py", "--output", self.output_dir.get()]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_dir)
            
            if result.returncode == 0:
                self.project_state['stage'] = 4
                if 4 not in self.project_state['stages_completed']:
                    self.project_state['stages_completed'].append(4)
                    
                self.update_progress_display()
                self.refresh_documents_list()
                
                messagebox.showinfo(
                    "Success", 
                    "Stage 4: Document Generation completed successfully!\n\n"
                    f"Documents saved to: {self.output_dir.get()}"
                )
                self.log_message("✅ Stage 4 completed successfully!")
                
                # Open output folder automatically
                self.open_output_folder()
                
            else:
                raise Exception(result.stderr or "Document generation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Stage 4 failed: {str(e)}")
            self.log_message(f"❌ Stage 4 failed: {str(e)}")


def main():
    """Main application entry point."""
    root = tk.Tk()
    
    # Set icon (if available)
    try:
        # You can add an icon file here if available
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = PolicyManualGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()