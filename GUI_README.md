# Policy Manual Generation System - GUI Application

A comprehensive graphical user interface for the 4-stage policy manual generation system. This GUI provides an intuitive way to manage the entire workflow from project initiation to final document generation.

## ✨ Features

### 🏗️ Complete Workflow Management
- **Stage 1**: Project Initiation with organogram upload and manual selection
- **Stage 2**: Project Expansion with section editing and customization
- **Stage 3**: Content Generation with AI-powered content creation
- **Stage 4**: Document Generation with professional Word document output

### 📊 Progress Tracking
- Visual progress indicators for each stage
- Overall completion percentage
- Real-time status updates
- Stage validation and prerequisites

### 💻 User-Friendly Interface
- Tabbed interface for easy navigation
- File browser integration
- Real-time logging and feedback
- Error handling and validation

## 🚀 Getting Started

### Prerequisites
```bash
# Install required dependencies
pip install python-docx requests tkinter
```

### Launch the GUI
```bash
# Method 1: Direct launch
python gui_app.py

# Method 2: Using launcher
python launch_gui.py
```

## 📋 Stage-by-Stage Guide

### Stage 1: Project Initiation 🚀
1. **Upload Organogram**: Browse and select your organogram JSON file
2. **Select Manuals**: Choose which policy manuals to generate
3. **Initialize Project**: Click "Start Stage 1" to create project structure
4. **Review Output**: Check the generated table of contents and variables

**Inputs Required:**
- Organogram JSON file (defines company structure and roles)
- Manual selection (HR, IT, Finance, etc.)

**Outputs Generated:**
- `config.json` - Common project configuration
- `sections_[manual].json` - Table of contents for each manual
- `variables.json` - Variable placeholders for customization

### Stage 2: Project Expansion 📝
1. **Select Manual**: Choose a manual to customize from the dropdown
2. **Edit Sections**: Review and modify section structures
3. **Add Notes**: Customize content parameters and requirements
4. **Save Changes**: Update section configurations
5. **Complete Stage**: Finalize all customizations

**Features:**
- Interactive section editor with JSON formatting
- Real-time preview of section structure
- Note management for content generation guidelines
- Validation of section requirements

**Outputs Generated:**
- Updated `sections_[manual].json` files
- `general_notes.txt` - Overall project guidelines
- `[manual]_notes.txt` - Manual-specific customization notes

### Stage 3: Content Generation 🤖
1. **Select Generation Mode**: All manuals or specific manual
2. **Start Generation**: Begin AI-powered content creation
3. **Monitor Progress**: Track generation status and completion
4. **Preview Content**: Review generated content sections
5. **Validate Output**: Ensure content quality and completeness

**Features:**
- Progress tracking with percentage completion
- Real-time content preview
- Pause and resume functionality
- Error handling and retry mechanisms

**Requirements:**
- LM Studio running locally (http://localhost:1234)
- Configured AI model for content generation
- Completion of Stages 1 and 2

**Outputs Generated:**
- `content_[manual].json` - Complete content for each manual
- Structured JSON with sections, content, and metadata

### Stage 4: Document Generation 📄
1. **Set Output Directory**: Choose where to save generated documents
2. **Configure Format**: Select document format (Word .docx)
3. **Generate Documents**: Create professional policy manuals
4. **Review Output**: Check generated documents list
5. **Open Files**: Access completed documents directly

**Features:**
- Professional Word document formatting
- Automatic table of contents generation
- Variable substitution and personalization
- Corporate branding and styling
- Batch processing for multiple manuals

**Outputs Generated:**
- `[manual]_manual.docx` - Professional Word documents
- Properly formatted with headings, bullet points, and styles
- Ready for distribution and implementation

## 🎛️ GUI Components

### Main Window
- **Title Bar**: System name and branding
- **Progress Overview**: Visual indicators for all stages
- **Stage Tabs**: Dedicated interface for each stage
- **Status Bar**: Real-time status and timestamp

### Progress Overview Panel
- **Stage Indicators**: Visual status for each stage (⏳ 🔄 ✅)
- **Progress Bar**: Overall completion percentage
- **Stage Labels**: Clear identification of each workflow stage

### File Management
- **File Browser**: Integrated file selection dialogs
- **Path Display**: Clear indication of selected files
- **Output Management**: Organized document output and access

### Logging and Feedback
- **Real-time Logs**: Scrollable text areas for process output
- **Status Updates**: Immediate feedback on user actions
- **Error Handling**: Clear error messages and recovery guidance

## 🔧 Configuration

### LM Studio Setup
```json
{
  "lm_studio_url": "http://localhost:1234",
  "model_name": "local-model",
  "company_name": "Your Company",
  "organogram_path": "path/to/organogram.json"
}
```

### Organogram Structure
```json
{
  "company_name": "Your Company",
  "manuals": {
    "hr": {
      "name": "Human Resources Policy Manual",
      "description": "Comprehensive HR policies and procedures",
      "target_roles": ["hr_manager", "employees"]
    },
    "it": {
      "name": "IT Security Policy Manual",
      "description": "Information technology security policies",
      "target_roles": ["it_admin", "all_users"]
    }
  },
  "roles": {
    "hr_manager": "Human Resources Manager",
    "it_admin": "IT Administrator",
    "employees": "All Employees"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

**"python-docx library required"**
```bash
pip install python-docx
```

**"Failed to connect to LM Studio"**
- Ensure LM Studio is running on http://localhost:1234
- Check that a model is loaded and ready
- Verify network connectivity

**"No organogram file selected"**
- Use the Browse button to select a valid JSON organogram file
- Ensure the file follows the required structure
- Check file permissions and encoding

**"No content files found"**
- Complete Stage 3 (Content Generation) first
- Verify `content_*.json` files exist in the project directory
- Check file naming conventions

### GUI Not Responding
- Check console output for error messages
- Ensure all dependencies are installed correctly
- Restart the application and try again

## 📁 File Structure

```
project_root/
├── gui_app.py              # Main GUI application
├── launch_gui.py           # Simple launcher script
├── init_project.py         # Stage 1 backend
├── project_expansion.py    # Stage 2 backend
├── generate_content.py     # Stage 3 backend
├── generate_documents.py   # Stage 4 backend
├── config.json            # Common configuration
├── variables.json         # Variable definitions
├── organogram.json        # Company structure
├── sections_*.json        # Manual structures
├── content_*.json         # Generated content
├── *_notes.txt           # User customizations
└── generated_documents/   # Final output directory
    ├── hr_manual.docx
    ├── it_manual.docx
    └── ...
```

## 🔄 Workflow Integration

The GUI seamlessly integrates with all backend scripts:

1. **Stage 1**: Calls `init_project.py --organogram [file] --manuals [list]`
2. **Stage 2**: Uses `project_expansion.py` for section editing
3. **Stage 3**: Executes `generate_content.py` for AI content generation
4. **Stage 4**: Runs `generate_documents.py --output [dir]` for document creation

Each stage validates prerequisites and maintains state continuity throughout the workflow.

## 🎯 Best Practices

### Before Starting
- Prepare a comprehensive organogram file
- Ensure LM Studio is configured and running
- Have clear requirements for each manual type

### During Generation
- Review and customize sections in Stage 2
- Add specific notes and requirements
- Monitor content generation progress
- Validate outputs before proceeding

### After Completion
- Review generated documents for accuracy
- Customize formatting if needed
- Distribute to appropriate stakeholders
- Maintain version control for updates

## 🔮 Future Enhancements

- **Advanced Formatting**: More document styling options
- **Template System**: Reusable manual templates
- **Cloud Integration**: Remote LM Studio support
- **Collaboration Features**: Multi-user editing capabilities
- **Export Options**: PDF and other format support
- **Audit Trail**: Detailed change tracking and history

---

**Created**: September 2025  
**Version**: 1.0  
**System**: 4-Stage Policy Manual Generation with GUI