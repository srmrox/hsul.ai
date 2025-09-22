#!/usr/bin/env python3
"""
Policy Manual Generator using LM Studio API
This script connects to LM Studio, generates a table of contents for a policy manual,
writes each section, and refines the final document.

Features:
- File-based progress tracking (no data loss on interruption)
- RTF output with proper formatting
- Resume functionality for interrupted sessions
- Status file management
"""

import requests
import json
import time
import re
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, from_dict
from rtf.Rtf import Rtf


@dataclass
class SectionInfo:
    """Data class to hold section information"""
    number: str
    title: str
    content: str = ""
    status: str = "pending"  # pending, generated, refined
    word_count: int = 0
    review_notes: str = ""
    needs_revision: bool = False

    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class LMStudioClient:
    """Client for connecting to LM Studio API"""
    
    def __init__(self, base_url: str = "http://localhost:1234", model_name: str = "local-model"):
        """
        Initialize the LM Studio client
        
        Args:
            base_url: The base URL for LM Studio API (default: http://localhost:1234)
            model_name: The model name to use (default: local-model)
        """
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
        """
        Generate a response from LM Studio
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for response generation
            
        Returns:
            Generated response or None if failed
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
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


class ProjectState:
    """Manages the project state and file-based progress tracking"""
    
    def __init__(self, project_name: str = "policy_manual"):
        self.project_name = project_name
        self.status_file = f"{project_name}_status.json"
        self.sections_file = f"{project_name}_sections.json"
        self.config_file = f"{project_name}_config.json"
        self.project_dir = f"{project_name}_project"
        
        # Ensure project directory exists
        os.makedirs(self.project_dir, exist_ok=True)
        
        self.status_file = os.path.join(self.project_dir, "status.json")
        self.sections_file = os.path.join(self.project_dir, "sections.json")
        self.config_file = os.path.join(self.project_dir, "config.json")
    
    def save_config(self, config: Dict):
        """Save project configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict:
        """Load project configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_status(self, status: Dict):
        """Save current project status"""
        status['last_updated'] = datetime.now().isoformat()
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
    
    def load_status(self) -> Dict:
        """Load current project status"""
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_sections(self, sections: List[SectionInfo]):
        """Save sections to file"""
        sections_data = [section.to_dict() for section in sections]
        with open(self.sections_file, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    def load_sections(self) -> List[SectionInfo]:
        """Load sections from file"""
        if os.path.exists(self.sections_file):
            with open(self.sections_file, 'r', encoding='utf-8') as f:
                sections_data = json.load(f)
                return [SectionInfo.from_dict(data) for data in sections_data]
        return []
    
    def project_exists(self) -> bool:
        """Check if a project already exists"""
        return os.path.exists(self.status_file)
    
    def cleanup(self):
        """Clean up project files when generation is complete"""
        if os.path.exists(self.project_dir):
            # Move completed files out of project directory
            completed_dir = f"{self.project_name}_completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(completed_dir):
                shutil.rmtree(completed_dir)
            shutil.move(self.project_dir, completed_dir)
            print(f"📁 Project files archived to {completed_dir}")


class RTFGenerator:
    """Generates RTF formatted documents"""
    
    def __init__(self):
        self.rtf = Rtf()
        
    def create_policy_manual_rtf(self, sections: List[SectionInfo], 
                                manual_description: str, 
                                filename: str = "policy_manual.rtf") -> str:
        """
        Create an RTF formatted policy manual
        
        Args:
            sections: List of section information
            manual_description: Description of the manual
            filename: Output filename
            
        Returns:
            Path to the created RTF file
        """
        # Create title
        self.rtf.addParagraph("POLICY MANUAL", 
                             font_size=28, 
                             bold=True, 
                             center=True)
        self.rtf.addParagraph("")  # Empty line
        
        # Add description
        self.rtf.addParagraph(f"Subject: {manual_description}", 
                             font_size=14, 
                             bold=True, 
                             center=True)
        self.rtf.addParagraph("")  # Empty line
        
        # Add generation date
        self.rtf.addParagraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", 
                             font_size=12, 
                             center=True)
        self.rtf.addParagraph("")  # Empty line
        self.rtf.addParagraph("")  # Empty line
        
        # Table of Contents
        self.rtf.addParagraph("TABLE OF CONTENTS", 
                             font_size=16, 
                             bold=True, 
                             underline=True)
        self.rtf.addParagraph("")  # Empty line
        
        for section in sections:
            toc_line = f"{section.number}. {section.title}"
            # Add indentation for subsections
            indent_level = section.number.count('.') - 1
            toc_line = "    " * indent_level + toc_line
            self.rtf.addParagraph(toc_line, font_size=11)
        
        self.rtf.addParagraph("")  # Empty line
        self.rtf.addParagraph("")  # Empty line
        
        # Add page break (simulated with multiple line breaks)
        for _ in range(5):
            self.rtf.addParagraph("")
        
        # Add sections
        for section in sections:
            if section.content.strip():
                # Section header
                self.rtf.addParagraph(f"Section {section.number}: {section.title}", 
                                     font_size=14, 
                                     bold=True, 
                                     underline=True)
                self.rtf.addParagraph("")  # Empty line
                
                # Section content
                # Split content into paragraphs
                paragraphs = section.content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # Check if it's a subheading (starts with capital letters and is short)
                        if (len(paragraph) < 100 and 
                            paragraph.strip().istitle() and 
                            not paragraph.endswith('.')):
                            self.rtf.addParagraph(paragraph.strip(), 
                                                 font_size=12, 
                                                 bold=True)
                        else:
                            self.rtf.addParagraph(paragraph.strip(), 
                                                 font_size=11)
                        self.rtf.addParagraph("")  # Empty line after each paragraph
                
                # Add extra space between sections
                self.rtf.addParagraph("")
                self.rtf.addParagraph("")
        
        # Save the RTF file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.rtf.dump())
        
        return filename
        
class PolicyManualGenerator:
    """Main class for generating policy manuals with file-based progress tracking"""
    
    def __init__(self, lm_client: LMStudioClient, project_state: ProjectState):
        self.client = lm_client
        self.state = project_state
        self.sections: List[SectionInfo] = []
        
    def generate_toc(self, manual_description: str) -> List[SectionInfo]:
        """
        Generate table of contents for the policy manual
        
        Args:
            manual_description: Description of the policy manual to create
            
        Returns:
            List of SectionInfo containing the table of contents
        """
        prompt = f"""
        Please create a comprehensive table of contents for a policy manual about: {manual_description}
        
        Format your response as a numbered list with clear section titles. Include main sections and subsections.
        Example format:
        1. Introduction
        1.1. Purpose and Scope
        1.2. Policy Overview
        2. Definitions and Terms
        2.1. Key Definitions
        2.2. Acronyms
        3. [Continue with relevant sections...]
        
        Make sure the table of contents is comprehensive and covers all important aspects of the topic.
        Provide exactly the numbered list format shown above, nothing else.
        """
        
        print("🔄 Generating table of contents...")
        toc_response = self.client.generate_response(prompt, max_tokens=1500, temperature=0.3)
        
        if not toc_response:
            raise Exception("Failed to generate table of contents")
        
        # Parse the TOC response
        sections = []
        lines = toc_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Match patterns like "1." or "1.1." followed by text
            match = re.match(r'^(\d+(?:\.\d+)*)\.\s*(.+)$', line)
            if match:
                section_number = match.group(1)
                section_title = match.group(2).strip()
                sections.append(SectionInfo(section_number, section_title))
        
        if not sections:
            raise Exception("No valid sections found in TOC response")
        
        self.sections = sections
        
        # Save sections to file
        self.state.save_sections(self.sections)
        
        # Update status
        self.state.save_status({
            'phase': 'toc_generated',
            'total_sections': len(self.sections),
            'completed_sections': 0,
            'manual_description': manual_description
        })
        
        print(f"✅ Generated {len(self.sections)} sections")
        return self.sections
    
    def load_existing_sections(self) -> List[SectionInfo]:
        """Load existing sections from file"""
        self.sections = self.state.load_sections()
        return self.sections
    
    def generate_section_content(self, section_index: int, manual_description: str, 
                               existing_content: str = "") -> str:
        """
        Generate content for a specific section
        
        Args:
            section_index: Index of the section in the sections list
            manual_description: Description of the overall manual
            existing_content: Previously generated content for context
            
        Returns:
            Generated content for the section
        """
        if section_index >= len(self.sections):
            return ""
            
        section = self.sections[section_index]
        
        context_prompt = ""
        if existing_content:
            # Limit context to avoid token limits
            context_words = existing_content.split()
            if len(context_words) > 500:
                context_prompt = f"\n\nPreviously written content (for context):\n{' '.join(context_words[-500:])}"
            else:
                context_prompt = f"\n\nPreviously written content (for context):\n{existing_content}"
        
        prompt = f"""
        You are writing a comprehensive policy manual about: {manual_description}
        
        Please write detailed content for this section:
        Section {section.number}: {section.title}
        
        Requirements:
        - Write 300-800 words of detailed, professional content
        - Use clear, policy-appropriate language
        - Include specific guidelines, procedures, or requirements as relevant
        - Structure with subheadings if appropriate
        - Be comprehensive but focused on this specific section
        - Do not repeat information from other sections
        {context_prompt}
        
        Write only the section content, do not include the section number or title in your response.
        """
        
        print(f"🔄 Generating content for Section {section.number}: {section.title}")
        content = self.client.generate_response(prompt, max_tokens=1200, temperature=0.6)
        
        if content:
            # Update section
            self.sections[section_index].content = content
            self.sections[section_index].status = 'generated'
            self.sections[section_index].word_count = len(content.split())
            
            # Save updated sections
            self.state.save_sections(self.sections)
            
            # Update status
            completed_count = sum(1 for s in self.sections if s.status == 'generated')
            self.state.save_status({
                'phase': 'generating_content',
                'total_sections': len(self.sections),
                'completed_sections': completed_count,
                'current_section': section_index,
                'manual_description': manual_description
            })
            
            print(f"✅ Generated {len(content.split())} words for section {section.number}")
        else:
            print(f"❌ Failed to generate content for section {section.number}")
        
        return content or ""
    
    def generate_all_sections(self, manual_description: str, resume_from: int = 0):
        """Generate content for all sections starting from a specific index"""
        print(f"\n🔄 Starting content generation from section {resume_from + 1} of {len(self.sections)}...")
        
        existing_content = ""
        
        # Build existing content from completed sections
        for i in range(resume_from):
            if i < len(self.sections) and self.sections[i].content:
                existing_content += f"\n\nSection {self.sections[i].number}: {self.sections[i].title}\n{self.sections[i].content}"
        
        for i in range(resume_from, len(self.sections)):
            section_content = self.generate_section_content(i, manual_description, existing_content)
            
            if section_content:
                existing_content += f"\n\nSection {self.sections[i].number}: {self.sections[i].title}\n{section_content}"
            
            # Small delay to avoid overwhelming the API
            time.sleep(1)
        
        print("✅ Completed content generation for all sections")
    
    def refine_manual(self, manual_description: str) -> List[SectionInfo]:
        """
        Review and refine the complete manual for duplicates and improvements
        
        Args:
            manual_description: Description of the manual
            
        Returns:
            Updated list of sections with refined content
        """
        print("\n🔄 Refining complete manual...")
        
        # Compile the full manual
        full_manual = []
        for section in self.sections:
            if section.content.strip():
                full_manual.append(f"Section {section.number}: {section.title}\n{section.content}")
        
        full_text = "\n\n".join(full_manual)
        
        prompt = f"""
        Please review this complete policy manual about: {manual_description}
        
        FULL MANUAL CONTENT:
        {full_text}
        
        Please analyze the manual and provide a JSON response with the following structure:
        {{
            "issues_found": [
                {{"type": "duplicate", "sections": ["1.1", "2.3"], "description": "Similar content about..."}},
                {{"type": "gap", "location": "after_section_3", "description": "Missing information about..."}}
            ],
            "improvements": [
                {{"section": "1.1", "suggestion": "Add more specific details about..."}},
                {{"section": "2.2", "suggestion": "Clarify the procedure for..."}}
            ],
            "overall_quality": "good/needs_work/excellent",
            "summary": "Overall assessment of the manual..."
        }}
        
        Focus on:
        1. Content duplication between sections
        2. Missing important information
        3. Clarity and consistency issues
        4. Policy completeness
        
        Respond only with the JSON, no additional text.
        """
        
        review_response = self.client.generate_response(prompt, max_tokens=1500, temperature=0.3)
        
        if review_response:
            try:
                # Try to parse JSON response
                review_data = json.loads(review_response)
                
                # Update sections with review information
                if 'improvements' in review_data:
                    for improvement in review_data['improvements']:
                        section_num = improvement.get('section', '')
                        suggestion = improvement.get('suggestion', '')
                        
                        for section in self.sections:
                            if section.number == section_num:
                                section.review_notes = suggestion
                                section.needs_revision = True
                                break
                
                # Save updated sections
                self.state.save_sections(self.sections)
                
                # Update status
                self.state.save_status({
                    'phase': 'review_completed',
                    'total_sections': len(self.sections),
                    'completed_sections': len(self.sections),
                    'manual_description': manual_description,
                    'review_data': review_data
                })
                
                # Add overall assessment
                overall_quality = review_data.get('overall_quality', 'unknown')
                summary = review_data.get('summary', 'No summary provided')
                
                print(f"✅ Manual review completed - Overall quality: {overall_quality}")
                print(f"📝 Summary: {summary}")
                
                if 'issues_found' in review_data and review_data['issues_found']:
                    print(f"⚠️  Found {len(review_data['issues_found'])} issues to address")
                    for issue in review_data['issues_found']:
                        print(f"   - {issue.get('type', 'Unknown')}: {issue.get('description', 'No description')}")
                
            except json.JSONDecodeError:
                print("⚠️  Could not parse review response as JSON, but manual generation completed")
        else:
            print("⚠️  Review step failed, but manual content has been generated")
        
        return self.sections
    
    def save_to_files(self, manual_description: str, base_filename: str = "policy_manual"):
        """Save the manual to RTF and JSON formats"""
        # Save sections data to JSON
        json_filename = f"{base_filename}_data.json"
        sections_data = [section.to_dict() for section in self.sections]
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'manual_description': manual_description,
                'generated_date': datetime.now().isoformat(),
                'sections': sections_data,
                'statistics': {
                    'total_sections': len(self.sections),
                    'total_words': sum(s.word_count for s in self.sections),
                    'sections_needing_revision': sum(1 for s in self.sections if s.needs_revision)
                }
            }, f, indent=2, ensure_ascii=False)
        print(f"📁 Saved data to {json_filename}")
        
        # Save complete manual to RTF file
        rtf_filename = f"{base_filename}.rtf"
        rtf_generator = RTFGenerator()
        rtf_generator.create_policy_manual_rtf(self.sections, manual_description, rtf_filename)
        print(f"📁 Saved formatted manual to {rtf_filename}")
        
        return json_filename, rtf_filename


def check_for_existing_project() -> Tuple[Optional[str], bool]:
    """
    Check for existing project directories and let user choose what to do
    
    Returns:
        Tuple of (project_name, resume_flag) or (None, False) if starting fresh
    """
    # Look for existing project directories
    existing_projects = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.endswith('_project'):
            project_name = item.replace('_project', '')
            status_file = os.path.join(item, 'status.json')
            if os.path.exists(status_file):
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        status = json.load(f)
                        existing_projects.append({
                            'name': project_name,
                            'dir': item,
                            'status': status,
                            'last_updated': status.get('last_updated', 'Unknown')
                        })
                except:
                    pass
    
    if not existing_projects:
        return None, False
    
    print("🔍 Found existing project(s):")
    for i, proj in enumerate(existing_projects, 1):
        phase = proj['status'].get('phase', 'unknown')
        completed = proj['status'].get('completed_sections', 0)
        total = proj['status'].get('total_sections', 0)
        description = proj['status'].get('manual_description', 'No description')
        
        print(f"  {i}. {proj['name']}")
        print(f"     Description: {description}")
        print(f"     Progress: {completed}/{total} sections ({phase})")
        print(f"     Last updated: {proj['last_updated']}")
        print()
    
    while True:
        choice = input("Choose an option:\n1. Resume existing project\n2. Start new project (will overwrite)\n3. Cancel\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            if len(existing_projects) == 1:
                return existing_projects[0]['name'], True
            else:
                try:
                    proj_num = int(input(f"Which project to resume? (1-{len(existing_projects)}): ")) - 1
                    if 0 <= proj_num < len(existing_projects):
                        return existing_projects[proj_num]['name'], True
                    else:
                        print("Invalid project number!")
                        continue
                except ValueError:
                    print("Please enter a valid number!")
                    continue
        elif choice == '2':
            if len(existing_projects) == 1:
                return existing_projects[0]['name'], False
            else:
                try:
                    proj_num = int(input(f"Which project to overwrite? (1-{len(existing_projects)}): ")) - 1
                    if 0 <= proj_num < len(existing_projects):
                        # Clean up existing project
                        if os.path.exists(existing_projects[proj_num]['dir']):
                            shutil.rmtree(existing_projects[proj_num]['dir'])
                        return existing_projects[proj_num]['name'], False
                    else:
                        print("Invalid project number!")
                        continue
                except ValueError:
                    print("Please enter a valid number!")
                    continue
        elif choice == '3':
            return None, False
        else:
            print("Please enter 1, 2, or 3!")


def main():
    """Main function to orchestrate the policy manual generation"""
    print("🚀 Policy Manual Generator")
    print("=" * 50)
    
    # Check for existing projects
    project_name, resume = check_for_existing_project()
    
    if project_name is None:
        print("Operation cancelled.")
        return
    
    if not resume:
        # Get user input for new project
        lm_studio_url = input("Enter LM Studio URL (default: http://localhost:1234): ").strip()
        if not lm_studio_url:
            lm_studio_url = "http://localhost:1234"
        
        model_name = input("Enter model name (default: local-model): ").strip()
        if not model_name:
            model_name = "local-model"
        
        if not project_name:
            project_name = input("Enter project name (default: policy_manual): ").strip()
            if not project_name:
                project_name = "policy_manual"
        
        manual_description = input("Describe the policy manual you want to create: ").strip()
        if not manual_description:
            print("❌ Manual description is required!")
            return
    
    # Initialize project state
    state = ProjectState(project_name)
    
    if resume:
        # Load existing configuration and status
        config = state.load_config()
        status = state.load_status()
        
        lm_studio_url = config.get('lm_studio_url', 'http://localhost:1234')
        model_name = config.get('model_name', 'local-model')
        manual_description = status.get('manual_description', 'Resumed project')
        
        print(f"\n📂 Resuming project: {project_name}")
        print(f"   Description: {manual_description}")
        print(f"   Phase: {status.get('phase', 'unknown')}")
        print(f"   Progress: {status.get('completed_sections', 0)}/{status.get('total_sections', 0)} sections")
    else:
        # Save configuration for new project
        config = {
            'lm_studio_url': lm_studio_url,
            'model_name': model_name,
            'created_date': datetime.now().isoformat()
        }
        state.save_config(config)
        print(f"\n📝 Starting new project: {project_name}")
    
    # Initialize client
    print(f"\n🔌 Connecting to LM Studio at {lm_studio_url}...")
    client = LMStudioClient(lm_studio_url, model_name)
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to LM Studio. Please check the URL and ensure LM Studio is running.")
        return
    
    print("✅ Successfully connected to LM Studio!")
    
    # Initialize generator
    generator = PolicyManualGenerator(client, state)
    
    try:
        if resume:
            # Load existing sections and determine where to resume
            sections = generator.load_existing_sections()
            status = state.load_status()
            
            if not sections:
                print("❌ No existing sections found. Cannot resume.")
                return
            
            phase = status.get('phase', 'unknown')
            current_section = status.get('current_section', 0)
            
            print(f"\n📋 Loaded {len(sections)} sections")
            completed_sections = sum(1 for s in sections if s.status == 'generated')
            print(f"📊 Progress: {completed_sections}/{len(sections)} sections completed")
            
            if phase == 'toc_generated' or phase == 'generating_content':
                if completed_sections < len(sections):
                    print(f"\n🔄 Resuming content generation from section {completed_sections + 1}")
                    generator.generate_all_sections(manual_description, completed_sections)
                else:
                    print("✅ All sections already completed")
            
            if phase != 'review_completed':
                # Perform review
                generator.refine_manual(manual_description)
        else:
            # Generate table of contents
            sections = generator.generate_toc(manual_description)
            print(f"\n📋 Table of Contents:")
            for section in sections:
                print(f"   {section.number}. {section.title}")
            
            # Confirm before proceeding
            proceed = input(f"\nProceed to generate content for {len(sections)} sections? (y/n): ").strip().lower()
            if proceed != 'y':
                print("Operation paused. You can resume later by running the script again.")
                return
            
            # Generate all section content
            generator.generate_all_sections(manual_description)
            
            # Refine the manual
            generator.refine_manual(manual_description)
        
        # Show progress summary
        completed_sections = sum(1 for s in generator.sections if s.status == 'generated')
        total_words = sum(s.word_count for s in generator.sections)
        print(f"\n📊 Final Summary:")
        print(f"   Completed sections: {completed_sections}/{len(generator.sections)}")
        print(f"   Total words generated: {total_words:,}")
        
        # Save results
        print(f"\n💾 Saving results...")
        json_file, rtf_file = generator.save_to_files(manual_description, project_name)
        
        print(f"\n🎉 Policy manual generation completed!")
        print(f"📄 Files created:")
        print(f"   - {json_file} (structured data)")
        print(f"   - {rtf_file} (formatted manual)")
        
        # Show final statistics
        needs_revision = sum(1 for s in generator.sections if s.needs_revision)
        if needs_revision > 0:
            print(f"\n⚠️  {needs_revision} sections may need revision based on review")
        
        # Clean up project files
        cleanup = input("\nClean up project files? (y/n): ").strip().lower()
        if cleanup == 'y':
            state.cleanup()
        else:
            print("📁 Project files retained for future reference")
        
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Generation interrupted. Progress has been saved.")
        print("Run the script again to resume from where you left off.")
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        print("Progress has been saved. You can try resuming later.")
        return


if __name__ == "__main__":
    main()
