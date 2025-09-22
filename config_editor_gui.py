#!/usr/bin/env python3
"""
GUI Configuration Editor for Policy Manual Generation System
Provides a user-friendly interface to edit YAML configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from pathlib import Path
from config_manager import ConfigManager, ValidationResult

class ConfigEditorGUI:
    """GUI Configuration Editor with tabbed interface."""
    
    def __init__(self, root=None, config_manager=None):
        if root is None:
            self.root = tk.Tk()
            self.is_standalone = True
        else:
            self.root = root
            self.is_standalone = False
            
        self.config = config_manager or ConfigManager()
        self.field_widgets = {}
        self.validation_labels = {}
        self.unsaved_changes = False
        
        self.setup_gui()
        self.load_configuration()
        
        if self.is_standalone:
            self.root.mainloop()
    
    def setup_gui(self):
        """Setup the main GUI window and components."""
        if self.is_standalone:
            self.root.title("Configuration Editor - Policy Manual Generator")
            self.root.geometry("800x700")
            self.root.minsize(700, 600)
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="Company Configuration", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_tabs()
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="Configuration loaded", 
                                     foreground='green')
        self.status_label.pack(side='left')
        
        # Buttons
        ttk.Button(button_frame, text="Validate", command=self.validate_config).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Reset", command=self.reset_config).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Load File", command=self.load_file).pack(side='right', padx=(5, 0))
        
        # Bind close event
        if self.is_standalone:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_tabs(self):
        """Create tabbed interface for different configuration categories."""
        categories = self.config.get_categories()
        
        for category_name, fields in categories.items():
            # Create tab frame
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=category_name)
            
            # Create scrollable frame
            canvas = tk.Canvas(tab_frame)
            scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add fields to tab
            self.create_fields(scrollable_frame, category_name, fields)
            
            # Bind mousewheel to canvas
            def _on_mousewheel(event, canvas=canvas):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_fields(self, parent, category_name, fields):
        """Create input fields for a category."""
        row = 0
        
        # Category header
        header_label = ttk.Label(parent, text=f"{category_name} Settings", 
                                font=('Arial', 12, 'bold'))
        header_label.grid(row=row, column=0, columnspan=2, pady=(10, 20), sticky='w')
        row += 1
        
        for field_name, field_path in fields.items():
            field_info = self.config.get_field_info(field_path)
            
            # Create label
            label_text = field_info['description']
            if field_info['is_required']:
                label_text += " *"
            
            label = ttk.Label(parent, text=label_text)
            label.grid(row=row, column=0, sticky='w', padx=(20, 10), pady=5)
            
            # Create input widget based on field type
            widget = self.create_input_widget(parent, field_path, field_info)
            widget.grid(row=row, column=1, sticky='ew', padx=(0, 20), pady=5)
            
            # Configure column weights
            parent.columnconfigure(1, weight=1)
            
            # Store widget reference
            self.field_widgets[field_path] = widget
            
            # Create validation label
            validation_label = ttk.Label(parent, text="", foreground='red', font=('Arial', 8))
            validation_label.grid(row=row+1, column=1, sticky='w', padx=(0, 20))
            self.validation_labels[field_path] = validation_label
            
            row += 2
        
        # Add some padding at the bottom
        ttk.Label(parent, text="").grid(row=row, column=0, pady=20)
    
    def create_input_widget(self, parent, field_path, field_info):
        """Create appropriate input widget based on field type."""
        field_type = field_info['field_type']
        value = field_info['value'] or ""
        allowed_values = field_info['allowed_values']
        
        if allowed_values:
            # Combobox for enum values
            widget = ttk.Combobox(parent, values=allowed_values, state='readonly')
            if value in allowed_values:
                widget.set(value)
            widget.bind('<<ComboboxSelected>>', lambda e: self.on_field_change())
            
        elif field_type == 'boolean':
            # Checkbutton for boolean values
            var = tk.BooleanVar()
            var.set(value in ['true', 'True', True, 1, '1'])
            widget = ttk.Checkbutton(parent, variable=var)
            # Store variable reference in a custom attribute
            setattr(widget, '_var', var)
            widget.bind('<Button-1>', lambda e: self.root.after(10, self.on_field_change))
            
        elif field_type in ['email', 'url', 'phone'] or 'text' in field_type:
            # Entry widget for text fields
            widget = ttk.Entry(parent, width=40)
            widget.insert(0, str(value))
            widget.bind('<KeyRelease>', lambda e: self.on_field_change())
            
        else:
            # Default to Entry
            widget = ttk.Entry(parent, width=40)
            widget.insert(0, str(value))
            widget.bind('<KeyRelease>', lambda e: self.on_field_change())
        
        return widget
    
    def load_configuration(self):
        """Load configuration into GUI fields."""
        try:
            self.config.load_config()
            
            for field_path, widget in self.field_widgets.items():
                value = self.config.get(field_path, "")
                
                if isinstance(widget, ttk.Combobox):
                    widget.set(str(value))
                elif isinstance(widget, ttk.Checkbutton):
                    getattr(widget, '_var').set(value in ['true', 'True', True, 1, '1'])
                elif isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(value))
            
            self.unsaved_changes = False
            self.update_status("Configuration loaded", 'green')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            self.update_status("Error loading configuration", 'red')
    
    def save_config(self):
        """Save configuration from GUI fields."""
        try:
            # Update configuration with field values
            for field_path, widget in self.field_widgets.items():
                if isinstance(widget, ttk.Combobox):
                    value = widget.get()
                elif isinstance(widget, ttk.Checkbutton):
                    value = getattr(widget, '_var').get()
                elif isinstance(widget, ttk.Entry):
                    value = widget.get().strip()
                else:
                    continue
                
                self.config.set(field_path, value)
            
            # Validate before saving
            validation = self.config.validate()
            if not validation.is_valid:
                error_msg = "Configuration validation failed:\n\n" + "\n".join(validation.errors)
                result = messagebox.askyesno("Validation Errors", 
                                           f"{error_msg}\n\nSave anyway?")
                if not result:
                    self.show_validation_errors(validation)
                    return
            
            # Save configuration
            if self.config.save_config():
                self.unsaved_changes = False
                self.update_status("Configuration saved successfully", 'green')
                if validation.warnings:
                    warning_msg = "Saved with warnings:\n\n" + "\n".join(validation.warnings)
                    messagebox.showwarning("Warnings", warning_msg)
            else:
                self.update_status("Failed to save configuration", 'red')
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            self.update_status("Error saving configuration", 'red')
    
    def validate_config(self):
        """Validate current configuration."""
        try:
            # Update config with current field values (without saving)
            for field_path, widget in self.field_widgets.items():
                if isinstance(widget, ttk.Combobox):
                    value = widget.get()
                elif isinstance(widget, ttk.Checkbutton):
                    value = getattr(widget, '_var').get()
                elif isinstance(widget, ttk.Entry):
                    value = widget.get().strip()
                else:
                    continue
                
                self.config.set(field_path, value)
            
            validation = self.config.validate()
            self.show_validation_errors(validation)
            
            if validation.is_valid:
                if validation.warnings:
                    self.update_status(f"Valid with {len(validation.warnings)} warnings", 'orange')
                else:
                    self.update_status("Configuration is valid", 'green')
            else:
                self.update_status(f"Validation failed: {len(validation.errors)} errors", 'red')
                
        except Exception as e:
            messagebox.showerror("Error", f"Validation failed: {e}")
    
    def show_validation_errors(self, validation: ValidationResult):
        """Show validation errors in the GUI."""
        # Clear previous validation messages
        for label in self.validation_labels.values():
            label.config(text="")
        
        # Show errors
        all_messages = validation.errors + validation.warnings
        if all_messages:
            message = "Validation Results:\n\n"
            if validation.errors:
                message += "Errors:\n" + "\n".join(f"• {err}" for err in validation.errors)
            if validation.warnings:
                if validation.errors:
                    message += "\n\n"
                message += "Warnings:\n" + "\n".join(f"• {warn}" for warn in validation.warnings)
            
            messagebox.showinfo("Validation Results", message)
        else:
            messagebox.showinfo("Validation", "✅ Configuration is valid!")
    
    def reset_config(self):
        """Reset configuration to original values."""
        if self.unsaved_changes:
            result = messagebox.askyesno("Unsaved Changes", 
                                       "You have unsaved changes. Reset anyway?")
            if not result:
                return
        
        self.load_configuration()
    
    def load_file(self):
        """Load configuration from a different file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration File",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.config.config_file = Path(filename)
                self.load_configuration()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
    
    def on_field_change(self):
        """Handle field value changes."""
        self.unsaved_changes = True
        self.update_status("Configuration modified (unsaved)", 'orange')
    
    def update_status(self, message, color='black'):
        """Update status label."""
        self.status_label.config(text=message, foreground=color)
    
    def on_closing(self):
        """Handle window close event."""
        if self.unsaved_changes:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?"
            )
            if result is True:  # Yes - save and close
                self.save_config()
                if not self.unsaved_changes:  # Only close if save succeeded
                    self.root.destroy()
            elif result is False:  # No - close without saving
                self.root.destroy()
            # Cancel - do nothing
        else:
            self.root.destroy()

class ConfigEditorDialog:
    """Modal dialog version of the configuration editor."""
    
    def __init__(self, parent, config_manager=None):
        self.result = None
        self.config = config_manager or ConfigManager()
        
        # Create modal dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration Editor")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, 
                                        parent.winfo_rooty() + 50))
        
        # Create editor inside dialog
        self.editor = ConfigEditorGUI(self.dialog, self.config)
        
        # Add OK/Cancel buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side='right')
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def ok_clicked(self):
        """Handle OK button click."""
        if self.editor.unsaved_changes:
            self.editor.save_config()
        self.result = 'ok'
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = 'cancel'
        self.dialog.destroy()

def main():
    """Run standalone configuration editor."""
    try:
        editor = ConfigEditorGUI()
    except Exception as e:
        print(f"Error running configuration editor: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()