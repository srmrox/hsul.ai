# Policy Manual Generation System - 4-Stage Workflow

This system generates comprehensive policy manuals through a structured 4-stage process that allows for user input and customization at each stage.

## Installation

Before using the system, install the required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install python-docx requests
```

## Overview

The workflow has been redesigned into 4 distinct stages:

1. **Stage 1: Project Initiation** - Automated setup and structure creation
2. **Stage 2: Project Expansion** - User customization and input gathering
3. **Stage 3: Content Generation** - AI-powered content creation with user guidance
4. **Stage 4: Document Generation** - Professional document formatting and output

## Stage Details

### Stage 1: Project Initiation (`init_project.py`)

**Purpose:** Create the foundational structure for policy manuals

**What it does:**

- Generates comprehensive table of contents (sections.json)
- Creates variable placeholders for manual personalization
- Sets up project directories and configuration
- Establishes organizational responsibilities based on organogram.json

**Input files needed:**

- `input.txt` - List of policy manuals to create (one per line)
- `organogram.json` - Organizational structure (optional)
- `variables.json.example` - Template for variables (optional)

**Output:**

- `{project_name}_project/` directories for each manual
- `sections.json` - Table of contents with section descriptions
- `variables.json` - Common variables for all projects
- `status.json` - Project tracking information

**Usage:**

```bash
python init_project.py
```

### Stage 2: Project Expansion (`project_expansion.py`)

**Purpose:** Allow users to customize sections and provide input notes

**What it does:**

- Interactive section editor (add, modify, delete sections)
- Creates note files for user input:
  - `general_notes.txt` - Notes applicable to all manuals
  - `manual_specific_notes.txt` - Notes for this specific manual
- Allows editing of section descriptions to guide content generation

**Key features:**

- Edit section titles, descriptions, and numbering
- Add new sections or remove unwanted ones
- Template-guided note creation for user input
- Notes support meeting minutes, decisions, requirements, etc.

**Usage:**

```bash
python project_expansion.py
```

### Stage 3: Content Generation (`generate_content.py`)

**Purpose:** Generate AI-powered content using user guidance from Stage 2

**What it does:**

- Loads user notes from Stage 2 (general and manual-specific)
- Generates content for each section using AI
- Integrates organizational roles and responsibilities
- Applies variable placeholders throughout content
- Saves structured JSON content (no document generation)

**Key features:**

- Context-aware content generation based on section descriptions
- Integration of user notes into AI prompts
- Variable placeholder usage for personalization
- Iterative content generation with progress tracking

**Output:**

- `{project_name}_content.json` - Structured content ready for document generation

**Usage:**

```bash
python generate_content.py
```

### Stage 4: Document Generation (`generate_documents.py`)

**Purpose:** Create professionally formatted Word documents from JSON content

**What it does:**

- Loads structured content from Stage 3
- Applies proper Word document formatting
- Uses professional styles for headings, paragraphs, lists
- Substitutes all variables with final values
- Creates table of contents with proper indentation

**Key features:**

- Professional document styling (Arial headings, Times New Roman body)
- Proper heading hierarchy (H1, H2, H3) based on section numbering
- Bullet point formatting without markdown characters
- Variable substitution for personalization
- Automatic table of contents generation

**Output:**

- `{project_name}_manual.docx` - Publication-ready Word document

**Usage:**

```bash
python generate_documents.py
```

## Workflow Example

### Complete Workflow for Multiple Manuals

1. **Prepare input files:**

   ```text
   # input.txt
   HR Employee Handbook
   IT Security Policy Manual
   Financial Procedures Manual
   ```

2. **Run Stage 1:**

   ```bash
   python init_project.py
   ```

   Creates 3 project directories with sections and variables.

3. **Run Stage 2 for each project:**

   ```bash
   python project_expansion.py
   ```

   - Select each project
   - Edit sections as needed
   - Add notes from meetings, SME input, compliance requirements

4. **Run Stage 3 for each project:**

   ```bash
   python generate_content.py
   ```

   - Generates AI content incorporating your notes
   - Creates JSON content files

5. **Run Stage 4 for final documents:**

   ```bash
   python generate_documents.py
   ```

   - Creates professional Word documents
   - Ready for review and publication

## File Structure

```text
project_root/
├── init_project.py           # Stage 1
├── project_expansion.py      # Stage 2  
├── generate_content.py       # Stage 3
├── generate_documents.py     # Stage 4
├── input.txt                 # Manual list
├── config.json              # LM Studio settings
├── variables.json           # Common variables
├── organogram.json          # Org structure
└── {manual_name}_project/   # Project directories
    ├── sections.json        # TOC and descriptions
    ├── status.json         # Project status
    ├── notes/              # User input notes
    │   ├── general_notes.txt
    │   └── manual_specific_notes.txt
    ├── {project}_content.json  # Generated content
    └── {project}_manual.docx   # Final document
```

## Configuration Files

### input.txt

List of manuals to create, one per line:

```text
HR Employee Handbook
IT Security Policies
Quality Management System
Safety Procedures Manual
```

### organogram.json (optional)

Organizational structure for automatic role assignment:

```json
{
  "departments": {
    "hr": {
      "name": "Human Resources",
      "roles": {
        "hr_manager": {
          "title": "HR Manager",
          "name": "Jane Smith",
          "email": "jane.smith@company.com"
        }
      }
    }
  },
  "responsibility_matrix": {
    "policy_types": {
      "hr_policies": {
        "policy_owner": "hr_manager",
        "approver": "hr_director"
      }
    }
  }
}
```

### variables.json

Common variables across all manuals (auto-generated and editable):

```json
{
  "company_name": {
    "description": "Name of the organization",
    "default_value": "[COMPANY NAME]",
    "category": "organization"
  },
  "effective_date": {
    "description": "Policy effective date",
    "default_value": "[EFFECTIVE DATE]",
    "category": "policy"
  }
}
```

## Key Benefits of the 4-Stage System

1. **Separation of Concerns:** Each stage has a specific purpose and can be run independently
2. **User Control:** Stage 2 provides full control over structure and input
3. **Note Integration:** User notes and meeting minutes directly influence content generation
4. **Professional Output:** Stage 4 creates publication-ready documents with proper formatting
5. **Iterative Workflow:** Can re-run individual stages as needed
6. **Batch Processing:** Handle multiple manuals efficiently

## Requirements

- Python 3.7+
- python-docx library for Word document generation
- LM Studio or compatible OpenAI API endpoint for content generation
- requests library for API communication

Install dependencies:

```bash
pip install python-docx requests
```

## Tips for Best Results

1. **Stage 1:** Review generated sections carefully - they guide all subsequent content
2. **Stage 2:** Spend time on note files - detailed notes produce better content
3. **Stage 3:** Monitor content generation and restart if needed
4. **Stage 4:** Review final documents and adjust variables if needed

The system is designed to be flexible - you can re-run any stage to refine your output.
