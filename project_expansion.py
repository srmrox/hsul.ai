#!/usr/bin/env python3
"""
Policy Manual Project Expansion - Stage 2
This script allows users to edit generated sections.json files and create note files.

STAGE 2: PROJECT EXPANSION
- Allows users to edit sections.json files for each manual
- Creates general and manual-specific note files for user input
- Collects user notes that will guide content generation in Stage 3
- Prepares projects for Stage 3 (Content Generation)

Part of the 4-stage policy manual generation workflow:
Stage 1: Project Initiation (init_project.py)
Stage 2: Project Expansion (this script)
Stage 3: Content Generation (generate_content.py)
Stage 4: Document Generation (generate_documents.py)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SectionInfo:
    """Data class to hold section information"""
    number: str
    title: str
    description: str = ""
    content: str = ""
    status: str = "pending"
    word_count: int = 0
    review_notes: str = ""
    needs_revision: bool = False

    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            number=data.get('number', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            content=data.get('content', ''),
            status=data.get('status', 'pending'),
            word_count=data.get('word_count', 0),
            review_notes=data.get('review_notes', ''),
            needs_revision=data.get('needs_revision', False)
        )


class ProjectExpander:
    """Handles Stage 2 - Project expansion with user input and editing"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self.sections_file = os.path.join(project_dir, "sections.json")
        self.status_file = os.path.join(project_dir, "status.json")
        self.notes_dir = os.path.join(project_dir, "notes")
        self.general_notes_file = os.path.join(self.notes_dir, "general_notes.txt")
        self.manual_notes_file = os.path.join(self.notes_dir, "manual_specific_notes.txt")
        
        self.sections: List[SectionInfo] = []
        self.status: Dict = {}
        
        # Ensure notes directory exists
        os.makedirs(self.notes_dir, exist_ok=True)
    
    def load_project_data(self):
        """Load project sections and status"""
        # Load sections
        if os.path.exists(self.sections_file):
            with open(self.sections_file, 'r', encoding='utf-8') as f:
                sections_data = json.load(f)
                self.sections = [SectionInfo.from_dict(data) for data in sections_data]
        else:
            raise FileNotFoundError(f"sections.json not found in {self.project_dir}")
        
        # Load status
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                self.status = json.load(f)
        else:
            raise FileNotFoundError(f"status.json not found in {self.project_dir}")
    
    def save_sections(self):
        """Save sections to file"""
        sections_data = [section.to_dict() for section in self.sections]
        with open(self.sections_file, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    def save_status(self, updates: Dict):
        """Update and save project status"""
        self.status.update(updates)
        self.status['last_updated'] = datetime.now().isoformat()
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.status, f, indent=2)
    
    def create_note_files(self):
        """Create note files if they don't exist"""
        manual_description = self.status.get('manual_description', 'Unknown Manual')
        
        # Create general notes file
        if not os.path.exists(self.general_notes_file):
            general_template = f"""# General Notes for All Manuals
# These notes will be used as context for ALL policy manuals during content generation.
# Include common organizational information, general policies, or universal guidelines.

# Examples of what to include:
# - Company values and mission
# - General organizational structure
# - Common compliance requirements
# - Standard procedures that apply across all departments
# - Meeting minutes that affect all policies
# - Executive decisions or directives

# Instructions:
# - Write your notes in plain text below this section
# - Each line starting with # is a comment and will be ignored
# - Be specific and detailed - these notes directly influence content generation
# - Update this file as you gather more information

# Your general notes start here:

"""
            with open(self.general_notes_file, 'w', encoding='utf-8') as f:
                f.write(general_template)
            print(f"📝 Created general notes file: {self.general_notes_file}")
        
        # Create manual-specific notes file  
        if not os.path.exists(self.manual_notes_file):
            manual_template = f"""# Manual-Specific Notes for: {manual_description}
# These notes will be used specifically for this manual during content generation.
# Include information relevant only to this particular policy area.

# Examples of what to include:
# - Subject matter expert input
# - Industry-specific requirements
# - Department-specific procedures
# - Regulatory compliance details for this area
# - Meeting minutes related to this policy area
# - Decisions or instructions specific to this manual

# Instructions:
# - Write your notes in plain text below this section
# - Each line starting with # is a comment and will be ignored
# - Be specific and detailed - these notes directly influence content generation
# - Focus on information relevant only to this manual type

# Your manual-specific notes for "{manual_description}" start here:

"""
            with open(self.manual_notes_file, 'w', encoding='utf-8') as f:
                f.write(manual_template)
            print(f"📝 Created manual-specific notes file: {self.manual_notes_file}")
    
    def show_project_summary(self):
        """Display project summary and current state"""
        manual_description = self.status.get('manual_description', 'Unknown')
        stage = self.status.get('stage', 'Unknown')
        stage_name = self.status.get('stage_name', 'Unknown')
        
        print(f"\n📋 PROJECT SUMMARY")
        print(f"=" * 60)
        print(f"Manual: {manual_description}")
        print(f"Current Stage: Stage {stage} ({stage_name})")
        print(f"Total Sections: {len(self.sections)}")
        print(f"Project Directory: {self.project_dir}")
        print(f"Notes Directory: {self.notes_dir}")
        print()
    
    def edit_sections_interactive(self):
        """Interactive section editor"""
        while True:
            print(f"\n📖 SECTION EDITOR")
            print(f"=" * 40)
            print(f"Current sections ({len(self.sections)} total):")
            
            for i, section in enumerate(self.sections, 1):
                print(f"{i:2d}. {section.number:6s} {section.title}")
                if len(section.description) > 80:
                    print(f"     Description: {section.description[:77]}...")
                else:
                    print(f"     Description: {section.description}")
            
            print(f"\nOptions:")
            print(f"1-{len(self.sections)}: Edit specific section")
            print(f"a: Add new section")
            print(f"d: Delete section")
            print(f"s: Save and continue")
            print(f"q: Quit without saving")
            
            choice = input(f"\nEnter your choice: ").strip().lower()
            
            if choice == 'q':
                return False  # Don't save changes
            elif choice == 's':
                self.save_sections()
                print("✅ Sections saved!")
                return True  # Save changes
            elif choice == 'a':
                self._add_new_section()
            elif choice == 'd':
                self._delete_section()
            else:
                try:
                    section_idx = int(choice) - 1
                    if 0 <= section_idx < len(self.sections):
                        self._edit_section(section_idx)
                    else:
                        print("❌ Invalid section number!")
                except ValueError:
                    print("❌ Please enter a valid option!")
    
    def _add_new_section(self):
        """Add a new section"""
        print(f"\n➕ ADD NEW SECTION")
        print(f"-" * 20)
        
        number = input("Section number (e.g., 5.2.1): ").strip()
        if not number:
            print("❌ Section number is required!")
            return
        
        title = input("Section title: ").strip()
        if not title:
            print("❌ Section title is required!")
            return
        
        description = input("Section description (what should be covered): ").strip()
        if not description:
            print("❌ Section description is required!")
            return
        
        new_section = SectionInfo(
            number=number,
            title=title,
            description=description
        )
        
        self.sections.append(new_section)
        print(f"✅ Added section {number}: {title}")
    
    def _delete_section(self):
        """Delete a section"""
        print(f"\n🗑️ DELETE SECTION")
        print(f"-" * 20)
        
        try:
            choice = input(f"Enter section number to delete (1-{len(self.sections)}): ").strip()
            section_idx = int(choice) - 1
            
            if 0 <= section_idx < len(self.sections):
                section = self.sections[section_idx]
                confirm = input(f"Delete section {section.number}: {section.title}? (y/N): ").strip().lower()
                
                if confirm == 'y':
                    deleted_section = self.sections.pop(section_idx)
                    print(f"✅ Deleted section {deleted_section.number}: {deleted_section.title}")
                else:
                    print("Deletion cancelled.")
            else:
                print("❌ Invalid section number!")
        except ValueError:
            print("❌ Please enter a valid number!")
    
    def _edit_section(self, section_idx: int):
        """Edit a specific section"""
        section = self.sections[section_idx]
        
        print(f"\n✏️ EDITING SECTION {section.number}")
        print(f"=" * 50)
        print(f"Current title: {section.title}")
        print(f"Current description: {section.description}")
        print()
        
        # Edit title
        new_title = input(f"New title (press Enter to keep current): ").strip()
        if new_title:
            section.title = new_title
            print("✅ Title updated")
        
        # Edit description
        print(f"\nCurrent description:")
        print(f"{section.description}")
        print()
        new_description = input(f"New description (press Enter to keep current): ").strip()
        if new_description:
            section.description = new_description
            print("✅ Description updated")
        
        # Edit section number
        new_number = input(f"New section number (current: {section.number}, press Enter to keep): ").strip()
        if new_number:
            section.number = new_number
            print("✅ Section number updated")
        
        print(f"✅ Section {section.number} updated successfully!")
    
    def open_note_files_for_editing(self):
        """Provide instructions for editing note files"""
        print(f"\n📝 NOTE FILES READY FOR EDITING")
        print(f"=" * 50)
        print(f"Two note files have been created in: {self.notes_dir}")
        print()
        print(f"1. General Notes (applies to all manuals):")
        print(f"   📄 {self.general_notes_file}")
        print(f"   Use for: Company policies, general procedures, universal guidelines")
        print()
        print(f"2. Manual-Specific Notes (applies only to this manual):")
        print(f"   📄 {self.manual_notes_file}")
        print(f"   Use for: Subject-matter expert input, specific requirements, meeting minutes")
        print()
        print(f"💡 Instructions:")
        print(f"   - Open these files in any text editor")
        print(f"   - Add your notes below the template sections")
        print(f"   - Include meeting minutes, decisions, requirements, etc.")
        print(f"   - These notes will guide content generation in Stage 3")
        print()
        
        input("Press Enter when you have finished editing the note files...")
    
    def finalize_stage_2(self):
        """Mark Stage 2 as complete and prepare for Stage 3"""
        # Update status to Stage 2 completed
        self.save_status({
            'stage': 2,
            'stage_name': 'project_expansion',
            'phase': 'stage_2_completed',
            'sections_edited': True,
            'notes_created': True,
            'ready_for_stage_3': True,
            'expansion_completed': datetime.now().isoformat()
        })
        
        print(f"\n🎉 Stage 2 (Project Expansion) completed!")
        print(f"✅ Sections edited and saved")
        print(f"✅ Note files created and ready")
        print(f"📁 Updated files:")
        print(f"   - {self.sections_file}")
        print(f"   - {self.general_notes_file}")
        print(f"   - {self.manual_notes_file}")
        print(f"   - {self.status_file}")
        print(f"\n🚀 Next step: Run 'python generate_content.py' for Stage 3 (Content Generation)")


def list_available_projects(stage_filter: Optional[int] = None) -> List[str]:
    """List available project directories, optionally filtered by stage"""
    projects = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.endswith('_project'):
            project_name = item.replace('_project', '')
            status_file = os.path.join(item, 'status.json')
            sections_file = os.path.join(item, 'sections.json')
            
            if os.path.exists(status_file) and os.path.exists(sections_file):
                # Check stage if filter is specified
                if stage_filter is not None:
                    try:
                        with open(status_file, 'r') as f:
                            status = json.load(f)
                            project_stage = status.get('stage', 0)
                            if project_stage != stage_filter:
                                continue
                    except:
                        continue
                
                projects.append(project_name)
    
    return projects


def select_project() -> Optional[str]:
    """Allow user to select a project for expansion"""
    # First check for projects ready for Stage 2 (completed Stage 1)
    stage_1_projects = list_available_projects(stage_filter=1)
    
    if stage_1_projects:
        print("📁 Projects ready for Stage 2 (Project Expansion):")
        for i, project in enumerate(stage_1_projects, 1):
            project_dir = f"{project}_project"
            try:
                with open(os.path.join(project_dir, 'status.json'), 'r') as f:
                    status = json.load(f)
                    description = status.get('manual_description', 'No description')
                    stage_name = status.get('stage_name', 'unknown')
                    
                print(f"   {i}. {project}")
                print(f"      Description: {description}")
                print(f"      Status: {stage_name}")
                print()
            except Exception as e:
                print(f"   {i}. {project} (Error loading info: {e})")
        
        # Get user selection
        while True:
            try:
                choice = input(f"Select project (1-{len(stage_1_projects)}): ").strip()
                project_index = int(choice) - 1
                
                if 0 <= project_index < len(stage_1_projects):
                    return stage_1_projects[project_index]
                else:
                    print("❌ Invalid selection!")
            except ValueError:
                print("❌ Please enter a valid number!")
    
    # If no Stage 1 projects, show all projects
    all_projects = list_available_projects()
    if not all_projects:
        print("❌ No projects found! Run 'python init_project.py' first.")
        return None
    
    print("📁 Available projects (all stages):")
    for i, project in enumerate(all_projects, 1):
        project_dir = f"{project}_project"
        try:
            with open(os.path.join(project_dir, 'status.json'), 'r') as f:
                status = json.load(f)
                description = status.get('manual_description', 'No description')
                stage = status.get('stage', 'Unknown')
                stage_name = status.get('stage_name', 'unknown')
                
            print(f"   {i}. {project}")
            print(f"      Description: {description}")
            print(f"      Current Stage: {stage} ({stage_name})")
            print()
        except Exception as e:
            print(f"   {i}. {project} (Error loading info: {e})")
    
    # Get user selection
    while True:
        try:
            choice = input(f"Select project (1-{len(all_projects)}): ").strip()
            project_index = int(choice) - 1
            
            if 0 <= project_index < len(all_projects):
                return all_projects[project_index]
            else:
                print("❌ Invalid selection!")
        except ValueError:
            print("❌ Please enter a valid number!")


def main():
    """Main function for Stage 2 - Project Expansion"""
    print("🚀 Stage 2: Policy Manual Project Expansion")
    print("=" * 60)
    
    # Select project
    selected_project = select_project()
    if not selected_project:
        return
    
    project_dir = f"{selected_project}_project"
    print(f"\n📂 Selected project: {selected_project}")
    
    # Initialize project expander
    try:
        expander = ProjectExpander(project_dir)
        expander.load_project_data()
        
        # Show project summary
        expander.show_project_summary()
        
        # Create note files
        print("📝 Setting up note files...")
        expander.create_note_files()
        
        # Main expansion workflow
        while True:
            print(f"\n🔧 STAGE 2 OPTIONS")
            print(f"=" * 30)
            print(f"1. Edit sections (add, modify, delete sections)")
            print(f"2. Open note files for editing") 
            print(f"3. Complete Stage 2 and proceed to Stage 3")
            print(f"4. Exit without completing Stage 2")
            
            choice = input(f"\nSelect option (1-4): ").strip()
            
            if choice == '1':
                print("\n🔧 Entering section editor...")
                sections_saved = expander.edit_sections_interactive()
                if sections_saved:
                    print("✅ Section changes saved!")
                else:
                    print("❌ Section changes discarded.")
                    
            elif choice == '2':
                expander.open_note_files_for_editing()
                
            elif choice == '3':
                # Finalize Stage 2
                expander.finalize_stage_2()
                break
                
            elif choice == '4':
                print("👋 Exiting without completing Stage 2.")
                break
                
            else:
                print("❌ Please select a valid option (1-4)!")
    
    except Exception as e:
        print(f"❌ Error during project expansion: {e}")
        return


if __name__ == "__main__":
    main()