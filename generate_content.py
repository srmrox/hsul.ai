#!/usr/bin/env python3
"""
Policy Manual Content Generation - Stage 3
This script generates content for sections in policy manual projects.

STAGE 3: CONTENT GENERATION
- Generates content for policy manual sections using AI
- Integrates user notes from Stage 2 (general and manual-specific)
- Produces structured JSON content ready for document generation
- Stops at JSON content generation (no document creation)
- Prepares content for Stage 4 (Document Generation)

Part of the 4-stage policy manual generation workflow:
Stage 1: Project Initiation (init_project.py)
Stage 2: Project Expansion (project_expansion.py)
Stage 3: Content Generation (this script)
Stage 4: Document Generation (generate_documents.py)
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from config_manager import get_config_manager


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


class LMStudioClient:
    """Client for connecting to LM Studio API"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = "local-model"):
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.api_url = f"{self.base_url}/v1/chat/completions"
        
    def test_connection(self) -> bool:
        """Test if the connection to LM Studio is working"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Connection test failed: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """Generate a response from LM Studio"""
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except (KeyError, IndexError) as e:
            print(f"Error parsing response: {e}")
            return None


class ContentGenerator:
    """Main class for generating policy manual content"""
    
    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        
        # Initialize configuration manager
        self.config_manager = get_config_manager()
        
        # Use common config.json in main directory, project-specific files in project directory
        self.config_file = os.path.join(os.getcwd(), "config.json")
        # Use common organogram.json in main directory  
        self.organogram_file = os.path.join(os.getcwd(), "organogram.json")
        self.sections_file = os.path.join(project_dir, "sections.json")
        self.status_file = os.path.join(project_dir, "status.json")
        
        # Stage 2 note files
        self.notes_dir = os.path.join(project_dir, "notes")
        self.general_notes_file = os.path.join(self.notes_dir, "general_notes.txt")
        self.manual_notes_file = os.path.join(self.notes_dir, "manual_specific_notes.txt")
        
        self.sections: List[SectionInfo] = []
        self.config = {}
        self.variables = {}
        self.organogram = {}
        self.client: Optional[LMStudioClient] = None
        
        # User notes content
        self.general_notes = ""
        self.manual_notes = ""
    
    def load_project(self):
        """Load project configuration and data"""
        # Load common config (LM Studio settings)
        with open(self.config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # Load project-specific data from status.json and merge into config
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status_data = json.load(f)
                # Merge project-specific fields into config for backward compatibility
                self.config.update({
                    'manual_description': status_data.get('manual_description', ''),
                    'created_date': status_data.get('created_date', ''),
                    'project_name': status_data.get('project_name', ''),
                    'stage': status_data.get('stage', ''),
                    'policy_type': status_data.get('policy_type', ''),
                    'responsibilities': status_data.get('responsibilities', {})
                })
        
        # Load sections
        with open(self.sections_file, 'r', encoding='utf-8') as f:
            sections_data = json.load(f)
            self.sections = [SectionInfo.from_dict(data) for data in sections_data]
        
        # Load variables from ConfigManager
        self.variables = self.config_manager.get_variables_dict()
        
        # Load organogram
        if os.path.exists(self.organogram_file):
            with open(self.organogram_file, 'r', encoding='utf-8') as f:
                self.organogram = json.load(f)
        
        # Initialize LM Studio client
        self.client = LMStudioClient(
            self.config.get('lm_studio_url', 'http://localhost:1234'),
            self.config.get('model_name', 'local-model')
        )
        
        # Load user notes from Stage 2
        self.load_user_notes()
    
    def load_user_notes(self):
        """Load user notes from Stage 2 expansion"""
        # Load general notes
        if os.path.exists(self.general_notes_file):
            try:
                with open(self.general_notes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Filter out comments (lines starting with #)
                    lines = content.split('\n')
                    filtered_lines = [line for line in lines if not line.strip().startswith('#')]
                    self.general_notes = '\n'.join(filtered_lines).strip()
                    
                print(f"📝 Loaded general notes ({len(self.general_notes)} characters)")
            except Exception as e:
                print(f"⚠️ Could not load general notes: {e}")
                self.general_notes = ""
        else:
            print("📝 No general notes found")
            self.general_notes = ""
        
        # Load manual-specific notes
        if os.path.exists(self.manual_notes_file):
            try:
                with open(self.manual_notes_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Filter out comments (lines starting with #)
                    lines = content.split('\n')
                    filtered_lines = [line for line in lines if not line.strip().startswith('#')]
                    self.manual_notes = '\n'.join(filtered_lines).strip()
                    
                print(f"📝 Loaded manual-specific notes ({len(self.manual_notes)} characters)")
            except Exception as e:
                print(f"⚠️ Could not load manual-specific notes: {e}")
                self.manual_notes = ""
        else:
            print("📝 No manual-specific notes found")
            self.manual_notes = ""
    
    def save_sections(self):
        """Save sections to file"""
        sections_data = [section.to_dict() for section in self.sections]
        with open(self.sections_file, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    def save_status(self, status: Dict):
        """Save current project status"""
        status['last_updated'] = datetime.now().isoformat()
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
    
    def generate_section_content(self, section_index: int, existing_content: str = "") -> str:
        """Generate content for a specific section using description as guidance"""
        if section_index >= len(self.sections):
            return ""
            
        section = self.sections[section_index]
        manual_description = self.config.get('manual_description', '')
        
        context_prompt = ""
        if existing_content:
            # Limit context to avoid token limits
            context_words = existing_content.split()
            if len(context_words) > 500:
                context_prompt = f"\n\nPreviously written content (for context):\n{' '.join(context_words[-500:])}"
            else:
                context_prompt = f"\n\nPreviously written content (for context):\n{existing_content}"
        
        # Prepare variables context
        variables_context = ""
        if self.variables:
            variables_context = "\n\nAvailable variables (use these placeholders in your content):\n"
            for var_name, var_value in self.variables.items():
                placeholder = f"[{var_name}]"
                variables_context += f"- {placeholder}: {var_value}\n"
            variables_context += "\nUse these placeholders where appropriate in your content (e.g., [COMPANY_NAME], [COMPANY_EMAIL])."
        
        # Prepare organogram/responsibility context
        responsibility_context = ""
        responsibilities = self.config.get('responsibilities', {})
        if responsibilities:
            responsibility_context = "\n\nKey roles and responsibilities for this policy:\n"
            for role_type, role_info in responsibilities.items():
                responsibility_context += f"- {role_info.get('title', role_type)}: {role_info.get('name', '[NAME]')} ({role_info.get('email', '[EMAIL]')})\n"
            responsibility_context += "\nReference these roles when specifying responsibilities, approvals, or escalation procedures in your content."
        
        # Prepare user notes context
        notes_context = ""
        if self.general_notes or self.manual_notes:
            notes_context = "\n\nUser Notes and Guidelines:"
            
            if self.general_notes:
                notes_context += f"\n\nGeneral organizational notes (apply to all policies):\n{self.general_notes}"
            
            if self.manual_notes:
                notes_context += f"\n\nSpecific notes for this manual:\n{self.manual_notes}"
            
            notes_context += "\n\nIncorporate relevant information from these notes into your content where appropriate."
        
        prompt = f"""
        You are writing a comprehensive policy manual about: {manual_description}
        
        Please write detailed content for this section:
        Section {section.number}: {section.title}
        
        Section Description (your guide for what to cover):
        {section.description}
        {variables_context}
        {responsibility_context}
        {notes_context}
        
        Requirements:
        - Write 400-1000 words of detailed, professional content
        - Use clear, policy-appropriate language suitable for a professional environment
        - Include specific guidelines, procedures, or requirements as relevant
        - Structure with subheadings if appropriate based on the section description
        - Be comprehensive and address all aspects mentioned in the description
        - Do not repeat information from other sections
        - Use professional policy language with clear directives and actionable guidance
        - Include relevant examples or scenarios where appropriate
        - Use variable placeholders where appropriate (e.g., [COMPANY NAME], [EFFECTIVE DATE])
        - Reference appropriate roles for responsibilities and approvals when relevant
        {context_prompt}
        
        Write only the section content, do not include the section number or title in your response.
        Focus specifically on what is described in the section description above.
        """
        
        print(f"🔄 Generating content for Section {section.number}: {section.title}")
        print(f"   📝 Using description: {section.description[:100]}...")
        
        if not self.client:
            print("❌ Client not initialized!")
            return ""
        
        content = self.client.generate_response(prompt, max_tokens=1500, temperature=0.6)
        
        if content:
            # Update section
            self.sections[section_index].content = content
            self.sections[section_index].status = 'generated'
            self.sections[section_index].word_count = len(content.split())
            
            print(f"✅ Generated {len(content.split())} words for section {section.number}")
        else:
            print(f"❌ Failed to generate content for section {section.number}")
        
        return content or ""
    
    def generate_all_sections(self, resume_from: int = 0):
        """Generate content for all sections starting from a specific index"""
        print(f"\n🔄 Starting content generation from section {resume_from + 1} of {len(self.sections)}...")
        
        existing_content = ""
        
        # Build existing content from completed sections
        for i in range(resume_from):
            if i < len(self.sections) and self.sections[i].content:
                existing_content += f"\n\nSection {self.sections[i].number}: {self.sections[i].title}\n{self.sections[i].content}"
        
        for i in range(resume_from, len(self.sections)):
            section_content = self.generate_section_content(i, existing_content)
            
            if section_content:
                existing_content += f"\n\nSection {self.sections[i].number}: {self.sections[i].title}\n{section_content}"
            
            # Save progress after each section
            self.save_sections()
            
            completed_count = sum(1 for s in self.sections if s.status == 'generated')
            self.save_status({
                'phase': 'generating_content',
                'total_sections': len(self.sections),
                'completed_sections': completed_count,
                'current_section': i,
                'manual_description': self.config.get('manual_description', '')
            })
            
            # Small delay to avoid overwhelming the API
            time.sleep(1)
        
        print("✅ Completed content generation for all sections")
    
    def save_to_files(self, base_filename: str):
        """Save the manual content to JSON format for Stage 4 processing"""
        # Save sections data to JSON with enhanced structure for document generation
        json_filename = f"{base_filename}_content.json"
        sections_data = [section.to_dict() for section in self.sections]
        
        # Enhanced content data structure for Stage 4
        content_data = {
            'manual_description': self.config.get('manual_description', ''),
            'generated_date': datetime.now().isoformat(),
            'stage': 3,
            'stage_name': 'content_generation',
            'project_name': self.config.get('project_name', base_filename),
            'sections': sections_data,
            'variables': self.variables,
            'user_notes': {
                'general_notes': self.general_notes,
                'manual_specific_notes': self.manual_notes
            },
            'responsibilities': self.config.get('responsibilities', {}),
            'statistics': {
                'total_sections': len(self.sections),
                'total_words': sum(s.word_count for s in self.sections),
                'sections_needing_revision': sum(1 for s in self.sections if s.needs_revision),
                'sections_with_content': sum(1 for s in self.sections if s.content.strip()),
                'content_generation_completed': datetime.now().isoformat()
            },
            'ready_for_stage_4': True
        }
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(content_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Saved content to {json_filename}")
        print(f"✅ Stage 3 (Content Generation) output ready for Stage 4 (Document Generation)")
        
        return json_filename


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
                            # For Stage 3, accept Stage 2 completed projects
                            if stage_filter == 3 and project_stage not in [2, 3]:
                                continue
                            elif stage_filter != 3 and project_stage != stage_filter:
                                continue
                    except:
                        continue
                
                projects.append(project_name)
    
    return projects


def main():
    """Main function for Stage 3 - Content Generation"""
    print("🚀 Stage 3: Policy Manual Content Generation")
    print("=" * 60)
    
    # First check for projects ready for Stage 3 (completed Stage 2)
    stage_3_projects = list_available_projects(stage_filter=3)
    
    if stage_3_projects:
        print("📁 Projects ready for Stage 3 (Content Generation):")
        for i, project in enumerate(stage_3_projects, 1):
            project_dir = f"{project}_project"
            try:
                with open(os.path.join(project_dir, 'status.json'), 'r') as f:
                    status = json.load(f)
                    description = status.get('manual_description', 'No description')
                    stage = status.get('stage', 'Unknown')
                    stage_name = status.get('stage_name', 'unknown')
                    completed = status.get('completed_sections', 0)
                    total = status.get('total_sections', 0)
                
                print(f"   {i}. {project}")
                print(f"      Description: {description}")
                print(f"      Status: Stage {stage} ({stage_name}) ({completed}/{total} sections)")
                print()
                
            except Exception as e:
                print(f"   {i}. {project} (Error loading info: {e})")
    else:
        # If no Stage 3 ready projects, show all projects
        all_projects = list_available_projects()
        if not all_projects:
            print("❌ No projects found!")
            print("Run 'python init_project.py' first to create a project,")
            print("then 'python project_expansion.py' to prepare for content generation.")
            return
        
        print("📁 Available projects (may not be ready for Stage 3):")
        for i, project in enumerate(all_projects, 1):
            project_dir = f"{project}_project"
            try:
                with open(os.path.join(project_dir, 'status.json'), 'r') as f:
                    status = json.load(f)
                    description = status.get('manual_description', 'No description')
                    stage = status.get('stage', 'Unknown')
                    stage_name = status.get('stage_name', 'unknown')
                    completed = status.get('completed_sections', 0)
                    total = status.get('total_sections', 0)
                
                print(f"   {i}. {project}")
                print(f"      Description: {description}")
                print(f"      Current Stage: Stage {stage} ({stage_name})")
                if stage >= 2:
                    print(f"      Sections: ({completed}/{total})")
                print()
                
            except Exception as e:
                print(f"   {i}. {project} (Error loading info: {e})")
        
        stage_3_projects = all_projects
    
    # Get user selection
    while True:
        try:
            choice = input(f"Select project (1-{len(stage_3_projects)}): ").strip()
            project_index = int(choice) - 1
            
            if 0 <= project_index < len(stage_3_projects):
                selected_project = stage_3_projects[project_index]
                break
            else:
                print("Invalid selection!")
        except ValueError:
            print("Please enter a valid number!")
    
    project_dir = f"{selected_project}_project"
    print(f"\n📂 Selected project: {selected_project}")
    
    # Initialize content generator
    generator = ContentGenerator(project_dir)
    
    try:
        # Load project data
        print("📋 Loading project data...")
        generator.load_project()
        
        # Test LM Studio connection
        print("🔌 Testing LM Studio connection...")
        if not generator.client or not generator.client.test_connection():
            print("❌ Failed to connect to LM Studio. Please check the URL and ensure LM Studio is running.")
            return
        
        print("✅ Successfully connected to LM Studio!")
        
        # Determine where to start/resume
        completed_sections = sum(1 for s in generator.sections if s.status == 'generated')
        
        if completed_sections > 0:
            print(f"📊 Found {completed_sections}/{len(generator.sections)} completed sections")
            resume = input("Resume from where you left off? (y/n): ").strip().lower()
            
            if resume == 'y':
                start_from = completed_sections
                print(f"🔄 Resuming from section {start_from + 1}")
            else:
                start_from = 0
                print("🔄 Starting from the beginning")
        else:
            start_from = 0
            print("🔄 Starting content generation")
        
        # Generate content
        generator.generate_all_sections(start_from)
        
        # Save final results
        print("\n💾 Saving final results...")
        json_file = generator.save_to_files(selected_project)
        
        # Update final status
        generator.save_status({
            'stage': 3,
            'stage_name': 'content_generation',
            'phase': 'stage_3_completed',
            'total_sections': len(generator.sections),
            'completed_sections': len(generator.sections),
            'manual_description': generator.config.get('manual_description', ''),
            'generation_completed': datetime.now().isoformat(),
            'ready_for_stage_4': True
        })
        
        print(f"\n🎉 Stage 3 (Content Generation) completed!")
        print(f"📄 File created:")
        print(f"   - {json_file} (structured content for document generation)")
        
        # Show final statistics
        total_words = sum(s.word_count for s in generator.sections)
        print(f"\n📊 Final Statistics:")
        print(f"   Total sections: {len(generator.sections)}")
        print(f"   Total words: {total_words:,}")
        print(f"   Variables used: {len(generator.variables)}")
        if generator.general_notes:
            print(f"   General notes: {len(generator.general_notes)} characters")
        if generator.manual_notes:
            print(f"   Manual notes: {len(generator.manual_notes)} characters")
        
        print(f"\n🚀 Next step: Run 'python generate_documents.py' for Stage 4 (Document Generation)")
        print(f"   This will create properly formatted Word documents from the generated content.")
        
    except Exception as e:
        print(f"❌ Error during content generation: {e}")
        return


if __name__ == "__main__":
    main()