#!/usr/bin/env python3
"""
Policy Manual Project Initialization - Stage 1
This script creates a new policy manual project with TOC and variables setup.

STAGE 1: PROJECT INITIATION
- Generates comprehensive table of contents (sections.json) 
- Creates variable placeholders for manual personalization
- Sets up project structure and basic configuration
- Prepares foundation for Stage 2 (Project Expansion)

Part of the 4-stage policy manual generation workflow:
Stage 1: Project Initiation (this script)
Stage 2: Project Expansion (project_expansion.py) 
Stage 3: Content Generation (generate_content.py)
Stage 4: Document Generation (generate_documents.py)
"""

import requests
import json
import time
import re
import os
import sys
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from config_manager import get_config_manager


@dataclass
class SectionInfo:
    """Data class to hold section information"""
    number: str
    title: str
    description: str = ""  # Section description to guide content generation
    content: str = ""
    status: str = "pending"  # pending, generated, refined
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


class ProjectInitializer:
    """Handles project initialization and TOC generation"""
    
    def __init__(self, lm_client: LMStudioClient, project_name: str):
        self.client = lm_client
        self.project_name = project_name
        self.project_dir = f"{project_name}_project"
        self.sections: List[SectionInfo] = []
        
        # Ensure project directory exists
        os.makedirs(self.project_dir, exist_ok=True)
        
        # Initialize configuration manager
        self.config_manager = get_config_manager()
        
        # Use common config.json in main directory, project-specific files in project directory
        self.config_file = os.path.join(os.getcwd(), "config.json")
        # Use common organogram.json in main directory
        self.organogram_file = os.path.join(os.getcwd(), "organogram.json")
        self.sections_file = os.path.join(self.project_dir, "sections.json")
        self.status_file = os.path.join(self.project_dir, "status.json")
    
    def save_config(self, config: Dict):
        """Save common configuration (LM Studio settings only)"""
        # Load existing common config or create new one
        common_config = self.load_config()
        
        # Update only the LM Studio settings in common config
        common_config['lm_studio_url'] = config.get('lm_studio_url')
        common_config['model_name'] = config.get('model_name')
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(common_config, f, indent=2)
    
    def load_config(self) -> Dict:
        """Load common configuration"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Return default config
            return {
                'lm_studio_url': 'http://localhost:1234',
                'model_name': 'local-model'
            }
    
    def save_status(self, status: Dict):
        """Save current project status"""
        status['last_updated'] = datetime.now().isoformat()
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
    
    def save_sections(self, sections: List[SectionInfo]):
        """Save sections to file"""
        sections_data = [section.to_dict() for section in sections]
        with open(self.sections_file, 'w', encoding='utf-8') as f:
            json.dump(sections_data, f, indent=2, ensure_ascii=False)
    
    def save_variables(self, variables: Dict, manual_description: str):
        """Save variables to YAML configuration (now deprecated - ConfigManager handles this)"""
        print(f"⚠️  Variable saving is now handled by ConfigManager. Generated variables:")
        for var_name, var_info in variables.items():
            print(f"  {var_name}: {var_info}")
        print("  Please use the Configuration Editor to update company information.")

    def load_organogram(self) -> Dict:
        """Load organizational structure from organogram.json"""
        if os.path.exists(self.organogram_file):
            try:
                with open(self.organogram_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load organogram: {e}")
                return {}
        else:
            print("⚠️  organogram.json not found")
            return {}

    def determine_policy_responsibilities(self, manual_description: str) -> Dict:
        """Determine responsibilities based on manual type and organogram"""
        organogram = self.load_organogram()
        if not organogram:
            return {}

        # Map common manual types to policy types
        manual_type_mapping = {
            'hr': 'hr_policies',
            'human resources': 'hr_policies', 
            'employee': 'hr_policies',
            'personnel': 'hr_policies',
            'it': 'it_security_policies',
            'information technology': 'it_security_policies',
            'cyber': 'it_security_policies',
            'security': 'it_security_policies',
            'data protection': 'it_security_policies',
            'financial': 'financial_policies',
            'finance': 'financial_policies',
            'accounting': 'financial_policies',
            'budget': 'financial_policies',
            'expense': 'financial_policies',
            'operational': 'operational_policies',
            'operations': 'operational_policies',
            'process': 'operational_policies',
            'procedure': 'operational_policies',
            'safety': 'safety_policies',
            'health': 'safety_policies',
            'workplace safety': 'safety_policies',
            'legal': 'legal_compliance_policies',
            'compliance': 'legal_compliance_policies',
            'regulatory': 'legal_compliance_policies',
            'quality': 'quality_policies',
            'qms': 'quality_policies',
            'iso': 'quality_policies'
        }

        # Determine policy type based on manual description
        manual_desc_lower = manual_description.lower()
        policy_type = None
        
        for keyword, p_type in manual_type_mapping.items():
            if keyword in manual_desc_lower:
                policy_type = p_type
                break
        
        # Default to operational_policies if no match
        if not policy_type:
            policy_type = 'operational_policies'

        # Get responsibility matrix
        responsibility_matrix = organogram.get('responsibility_matrix', {}).get('policy_types', {})
        responsibilities = responsibility_matrix.get(policy_type, {})

        # Resolve role names to actual people/details
        resolved_responsibilities = {}
        departments = organogram.get('departments', {})
        
        for role_type, role_key in responsibilities.items():
            # Find the role in departments
            role_info = self._find_role_in_organogram(role_key, departments)
            if role_info:
                resolved_responsibilities[role_type] = {
                    'role_key': role_key,
                    'title': role_info.get('title', role_key),
                    'name': role_info.get('name', f'[{role_key}]'),
                    'email': role_info.get('email', f'[{role_key}_EMAIL]'),
                    'phone': role_info.get('phone', f'[{role_key}_PHONE]')
                }

        return {
            'policy_type': policy_type,
            'responsibilities': resolved_responsibilities
        }

    def _find_role_in_organogram(self, role_key: str, departments: Dict) -> Optional[Dict]:
        """Find a role in the organizational structure"""
        for dept_key, dept_info in departments.items():
            roles = dept_info.get('roles', {})
            if role_key in roles:
                return roles[role_key]
        return None
    
    def generate_toc(self, manual_description: str) -> List[SectionInfo]:
        """
        Generate table of contents as JSON with hierarchical structure
        
        Args:
            manual_description: Description of the policy manual to create
            
        Returns:
            List of SectionInfo containing the table of contents with descriptions
        """
        prompt = f"""
        Create a comprehensive table of contents for a policy manual about: {manual_description}
        
        Return your response as a JSON object with the following structure:
        {{
          "sections": [
            {{
              "number": "1",
              "title": "Introduction",
              "description": "Overview of the policy manual, its purpose, scope, and how to use it effectively"
            }},
            {{
              "number": "1.1",
              "title": "Purpose and Scope",
              "description": "Define the specific purpose of this manual and outline its scope and boundaries"
            }},
            {{
              "number": "1.1.1",
              "title": "Applicability",
              "description": "Detail who this manual applies to and under what circumstances"
            }},
            {{
              "number": "2",
              "title": "Definitions and Terms",
              "description": "Key terminology, industry-specific definitions, and acronyms used throughout the manual"
            }}
          ]
        }}
        
        Requirements:
        - Use maximum 3 levels of numbering: 1, 1.1, 1.1.1
        - Create comprehensive coverage for: {manual_description}
        - Each section should have a clear, descriptive title
        - Each section must have a detailed description (2-3 sentences) explaining what will be covered
        - Descriptions should be specific and guide content creation
        - Ensure no overlap between section descriptions
        - Include all essential topics for a comprehensive policy manual
        
        Return ONLY the JSON object, no additional text.
        """
        
        print("🔄 Generating table of contents as JSON...")
        toc_response = self.client.generate_response(prompt, max_tokens=2500, temperature=0.3)
        
        if not toc_response:
            raise Exception("Failed to generate table of contents")
        
        try:
            # Parse JSON response
            toc_data = json.loads(toc_response.strip())
            
            if 'sections' not in toc_data:
                raise ValueError("JSON response missing 'sections' key")
            
            sections = []
            for section_data in toc_data['sections']:
                if all(key in section_data for key in ['number', 'title', 'description']):
                    section = SectionInfo(
                        number=section_data['number'],
                        title=section_data['title'],
                        description=section_data['description']
                    )
                    sections.append(section)
                else:
                    print(f"⚠️ Skipping incomplete section: {section_data}")
            
            if not sections:
                raise Exception("No valid sections found in JSON response")
            
            self.sections = sections
            print(f"✅ Generated {len(self.sections)} sections with descriptions")
            
            # Display the generated TOC for review
            print(f"\n📋 Generated Table of Contents:")
            for section in sections:
                indent = "  " * (section.number.count('.'))
                print(f"{indent}{section.number}. {section.title}")
                print(f"{indent}   📝 {section.description}")
                print()
            
            return self.sections
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Response was: {toc_response}")
            raise Exception("Invalid JSON format in TOC response")
        except Exception as e:
            print(f"❌ Error processing TOC: {e}")
            print(f"Response was: {toc_response}")
            raise
    
    def generate_variables(self, manual_description: str) -> Dict:
        """
        Generate variables that will be used throughout the policy manual
        
        Args:
            manual_description: Description of the policy manual to create
            
        Returns:
            Dictionary of variables with their descriptions and default values
        """
        
        # Get policy responsibilities from organogram
        policy_info = self.determine_policy_responsibilities(manual_description)
        responsibilities = policy_info.get('responsibilities', {})
        
        # Create context for the LLM including organizational roles
        org_context = ""
        if responsibilities:
            org_context = "\n\nBased on organizational structure, the following roles are relevant:\n"
            for role_type, role_info in responsibilities.items():
                org_context += f"- {role_type}: {role_info['title']} ({role_info['name']})\n"
        
        prompt = f"""
        Create a comprehensive list of variables that would be needed for a policy manual about: {manual_description}
        
        These variables will be used to personalize the policy manual with specific organization details.
        {org_context}
        
        Return your response as a JSON object with the following structure:
        {{
          "variables": {{
            "policy_owner": {{
              "description": "Person responsible for maintaining this policy",
              "default_value": "[POLICY OWNER]",
              "category": "responsibility"
            }},
            "effective_date": {{
              "description": "Date when this policy becomes effective",
              "default_value": "[EFFECTIVE DATE]",
              "category": "policy"
            }},
            "version": {{
              "description": "Version number of this policy document",
              "default_value": "1.0",
              "category": "document"
            }},
            "department": {{
              "description": "Department responsible for this policy",
              "default_value": "[DEPARTMENT]",
              "category": "organization"
            }}
          }}
        }}
        
        Requirements:
        - Include all essential variables for: {manual_description}
        - Each variable should have: description, default_value, category
        - Categories: organization, contact, policy, legal, operational
        - Default values should be placeholder text in [BRACKETS]
        - Include variables for company details, contact information, dates, legal requirements
        - Consider industry-specific variables that might be needed
        
        Return ONLY the JSON object, no additional text.
        """
        
        print("🔄 Generating variables for policy manual...")
        variables_response = self.client.generate_response(prompt, max_tokens=2000, temperature=0.3)
        
        if not variables_response:
            raise Exception("Failed to generate variables")
        
        try:
            # Parse JSON response
            variables_data = json.loads(variables_response.strip())
            
            if 'variables' not in variables_data:
                raise ValueError("JSON response missing 'variables' key")
            
            variables = variables_data['variables']
            
            # Add organogram-based responsibility variables
            policy_info = self.determine_policy_responsibilities(manual_description)
            responsibilities = policy_info.get('responsibilities', {})
            
            for role_type, role_info in responsibilities.items():
                var_name = f"{role_type.upper()}_NAME"
                variables[var_name] = {
                    'description': f"Name of the {role_info['title']}",
                    'default_value': role_info['name'],
                    'category': 'responsibility',
                    'from_organogram': True
                }
                
                var_name = f"{role_type.upper()}_EMAIL"
                variables[var_name] = {
                    'description': f"Email of the {role_info['title']}",
                    'default_value': role_info['email'],
                    'category': 'responsibility',
                    'from_organogram': True
                }
            
            print(f"✅ Generated {len(variables)} variables (including {len(responsibilities)} from organogram)")
            
            # Display the generated variables for review
            print(f"\n📋 Generated Variables:")
            for var_name, var_info in variables.items():
                category = var_info.get('category', 'general')
                description = var_info.get('description', 'No description')
                default = var_info.get('default_value', '[NOT SET]')
                source = " (from organogram)" if var_info.get('from_organogram') else ""
                print(f"   {var_name} ({category}): {description}{source}")
                print(f"      Default: {default}")
                print()
            
            return variables
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response: {e}")
            print(f"Response was: {variables_response}")
            raise Exception("Invalid JSON format in variables response")
        except Exception as e:
            print(f"❌ Error processing variables: {e}")
            print(f"Response was: {variables_response}")
            raise
    
    def allow_user_modifications(self) -> bool:
        """
        Allow user to review and modify section descriptions
        
        Returns:
            True if modifications were made, False otherwise
        """
        print("\n" + "="*60)
        print("📝 SECTION DESCRIPTIONS REVIEW")
        print("="*60)
        print("You can now review and modify the section descriptions before content generation.")
        print("These descriptions guide the LLM on what to write in each section.\n")
        
        while True:
            choice = input("Choose an option:\n1. Review/Edit sections\n2. Proceed with current descriptions\n3. Regenerate TOC\nEnter choice (1-3): ").strip()
            
            if choice == '1':
                return self._edit_sections()
            elif choice == '2':
                print("✅ Proceeding with current descriptions...")
                return False
            elif choice == '3':
                print("🔄 Will regenerate table of contents...")
                return True  # Signal to regenerate
            else:
                print("Please enter 1, 2, or 3!")
    
    def _edit_sections(self) -> bool:
        """
        Interactive editor for section descriptions
        
        Returns:
            True if any modifications were made
        """
        modifications_made = False
        
        print(f"\n📋 Current sections ({len(self.sections)} total):")
        for i, section in enumerate(self.sections, 1):
            print(f"\n{i}. Section {section.number}: {section.title}")
            print(f"   Description: {section.description}")
        
        while True:
            try:
                choice = input(f"\nEnter section number to edit (1-{len(self.sections)}), or 0 to finish: ").strip()
                
                if choice == '0':
                    break
                
                section_idx = int(choice) - 1
                if 0 <= section_idx < len(self.sections):
                    section = self.sections[section_idx]
                    print(f"\nEditing Section {section.number}: {section.title}")
                    print(f"Current description: {section.description}")
                    
                    new_description = input("Enter new description (or press Enter to keep current): ").strip()
                    if new_description:
                        section.description = new_description
                        modifications_made = True
                        print("✅ Description updated!")
                        
                        # Save changes immediately
                        self.save_sections(self.sections)
                    else:
                        print("Description unchanged.")
                else:
                    print("Invalid section number!")
                    
            except ValueError:
                print("Please enter a valid number!")
        
        if modifications_made:
            print("✅ All changes have been saved to sections.json")
        
        return modifications_made


def read_input_file() -> List[str]:
    """Read manuals list from input.txt file"""
    input_file = "input.txt"
    if not os.path.exists(input_file):
        print(f"❌ {input_file} not found. Please create it with one manual description per line.")
        return []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    return lines

def update_input_file(remaining_manuals: List[str]):
    """Update input.txt with remaining manuals"""
    input_file = "input.txt"
    with open(input_file, 'w', encoding='utf-8') as f:
        for manual in remaining_manuals:
            f.write(f"{manual}\n")

def review_common_variables():
    """Allow user to review and update the common configuration"""
    config_manager = get_config_manager()
    
    print("\n" + "="*60)
    print("CONFIGURATION REVIEW")
    print("="*60)
    
    # Show current configuration
    variables = config_manager.get_variables_dict()
    
    if not variables:
        print("No configuration found. Please set up your company information.")
        return False
    
    print(f"Current configuration:")
    print(f"  Company Name: {config_manager.get('organization.profile.name')}")
    print(f"  Email: {config_manager.get('organization.contact.digital.email')}")
    print(f"  Jurisdiction: {config_manager.get('organization.legal.jurisdiction')}")
    print()
    
    # Validate configuration
    validation = config_manager.validate()
    if validation.is_valid:
        print("Configuration is valid")
    else:
        print("Configuration has issues:")
        for error in validation.errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
    
    print()
    print("To modify configuration, run: python config_editor_gui.py")
    
    return validation.is_valid


def batch_initialize_projects():
    """Initialize all projects from input.txt and collect variables"""
    print("🚀 Batch Policy Manual Project Initialization")
    print("=" * 60)
    
    # Read manuals from input file
    manuals = read_input_file()
    if not manuals:
        return
    
    print(f"📋 Found {len(manuals)} manuals to process:")
    for i, manual in enumerate(manuals, 1):
        print(f"   {i}. {manual}")
    print()
    
    # Load existing common config
    config_file = os.path.join(os.getcwd(), "config.json")
    existing_config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print("📋 Found existing configuration - using saved settings")
            lm_studio_url = existing_config.get('lm_studio_url', 'http://localhost:1234')
            model_name = existing_config.get('model_name', 'local-model')
            print(f"   LM Studio URL: {lm_studio_url}")
            print(f"   Model Name: {model_name}")
        except Exception as e:
            print(f"⚠️  Could not load existing config: {e}")
            existing_config = {}
    
    # Only ask for configuration if not found in existing config
    if not existing_config:
        print("\n⚙️  LM Studio Configuration Required")
        # Get LM Studio configuration
        default_url = 'http://localhost:1234'
        lm_studio_url = input(f"Enter LM Studio URL (default: {default_url}): ").strip()
        if not lm_studio_url:
            lm_studio_url = default_url
        
        default_model = 'local-model'
        model_name = input(f"Enter model name (default: {default_model}): ").strip()
        if not model_name:
            model_name = default_model
    
    # Initialize client
    print(f"\n🔌 Connecting to LM Studio at {lm_studio_url}...")
    client = LMStudioClient(lm_studio_url, model_name)
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to LM Studio. Please check the URL and ensure LM Studio is running.")
        return
    
    print("✅ Successfully connected to LM Studio!")
    
    # Save common configuration
    config = {
        'lm_studio_url': lm_studio_url,
        'model_name': model_name,
    }
    config_file = os.path.join(os.getcwd(), "config.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    print("✅ Updated common configuration")
    
    # Process each manual
    processed_manuals = []
    failed_manuals = []
    
    for i, manual_description in enumerate(manuals, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(manuals)}: {manual_description}")
        print(f"{'='*60}")
        
        # Generate project name from manual description
        project_name = re.sub(r'[^a-zA-Z0-9\s]', '', manual_description)
        project_name = re.sub(r'\s+', '_', project_name).lower()[:30]
        
        try:
            # Check if project already exists
            project_dir = f"{project_name}_project"
            if os.path.exists(project_dir):
                print(f"⚠️  Project '{project_name}' already exists. Skipping...")
                processed_manuals.append(manual_description)
                continue
            
            # Initialize project
            initializer = ProjectInitializer(client, project_name)
            
            # Get organogram-based policy responsibilities
            policy_info = initializer.determine_policy_responsibilities(manual_description)
            
            # Save project-specific information
            project_status = {
                'manual_description': manual_description,
                'created_date': datetime.now().isoformat(),
                'stage': 1,
                'stage_name': 'project_initiation',
                'project_name': project_name,
                'policy_type': policy_info['policy_type'],
                'responsibilities': policy_info['responsibilities']
            }
            initializer.save_status(project_status)
            
            # Generate table of contents with user review
            sections = []
            max_attempts = 3
            for attempt in range(max_attempts):
                sections = initializer.generate_toc(manual_description)
                if sections:
                    break
                print(f"Attempt {attempt + 1} failed, retrying...")
            
            if not sections:
                print(f"❌ Failed to generate TOC for: {manual_description}")
                failed_manuals.append(manual_description)
                continue
            
            # Save sections
            initializer.save_sections(sections)
            
            # Generate and save variables (accumulated in common file)
            variables = initializer.generate_variables(manual_description)
            initializer.save_variables(variables, manual_description)
            
            # Update status
            initializer.save_status({
                'stage': 1,
                'stage_name': 'project_initiation',
                'phase': 'stage_1_completed',
                'total_sections': len(sections),
                'completed_sections': 0,
                'manual_description': manual_description,
                'variables_count': len(variables),
                'project_name': project_name,
                'ready_for_stage_2': True
            })
            
            print(f"✅ Successfully initialized: {manual_description}")
            processed_manuals.append(manual_description)
            
        except Exception as e:
            print(f"❌ Failed to initialize '{manual_description}': {str(e)}")
            failed_manuals.append(manual_description)
    
    # Update input.txt by removing processed manuals
    remaining_manuals = [m for m in manuals if m not in processed_manuals]
    update_input_file(remaining_manuals)
    
    # Show summary
    print(f"\n🎉 Batch Processing Complete!")
    print(f"✅ Successfully processed: {len(processed_manuals)} manuals")
    if failed_manuals:
        print(f"❌ Failed: {len(failed_manuals)} manuals")
        for manual in failed_manuals:
            print(f"   - {manual}")
    
    if remaining_manuals:
        print(f"📝 Remaining in input.txt: {len(remaining_manuals)} manuals")
    else:
        print("📝 All manuals from input.txt have been processed!")
    
    # Prompt user to review configuration
    config_manager = get_config_manager()
    print(f"\n📝 Configuration has been updated with variables from all manuals.")
    print(f"📁 Please review: config/company.yaml or run 'python config_editor_gui.py'")
    print(f"🚀 Next step: Run 'python project_expansion.py' for Stage 2 (Project Expansion)")
    print(f"   This will allow you to edit sections and add notes for all projects.")


def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Policy Manual Project Initialization - Stage 1')
    parser.add_argument('--organogram', type=str, help='Path to organogram JSON file')
    parser.add_argument('--manuals', nargs='+', help='List of manual types to generate')
    parser.add_argument('--single', action='store_true', help='Run single manual mode (legacy)')
    
    args = parser.parse_args()
    
    if args.organogram and args.manuals:
        # GUI mode with specific organogram and manuals
        gui_batch_mode(args.organogram, args.manuals)
    elif args.single:
        # Legacy single manual mode
        single_manual_mode()
    else:
        # Default batch mode from input.txt
        batch_initialize_projects()


def gui_batch_mode(organogram_path: str, manual_types: List[str]):
    """Process specific manuals with given organogram (called from GUI)"""
    print("🚀 Policy Manual Project Initialization (GUI Mode)")
    print("=" * 60)
    
    try:
        # Load organogram
        with open(organogram_path, 'r', encoding='utf-8') as f:
            organogram = json.load(f)
        
        print(f"📋 Loaded organogram: {organogram_path}")
        print(f"📚 Selected manuals: {', '.join(manual_types)}")
        
        # Get company info from organogram
        company_name = organogram.get('company_name', 'Your Company')
        
        # Load or create common configuration
        config_file = os.path.join(os.getcwd(), "config.json")
        existing_config = {}
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                print("📋 Found existing configuration")
            except Exception as e:
                print(f"⚠️  Could not load existing config: {e}")
                
        # Use existing config or defaults
        lm_studio_url = existing_config.get('lm_studio_url', 'http://localhost:1234')
        model_name = existing_config.get('model_name', 'local-model')
        
        print(f"🔌 Using LM Studio at {lm_studio_url} with model {model_name}")
        
        # Initialize client
        client = LMStudioClient(lm_studio_url, model_name)
        
        # Test connection
        if not client.test_connection():
            print("❌ Failed to connect to LM Studio. Please check the URL and ensure LM Studio is running.")
            sys.exit(1)
        
        print("✅ Successfully connected to LM Studio!")
        
        # Common configuration
        config = {
            'lm_studio_url': lm_studio_url,
            'model_name': model_name,
            'company_name': company_name,
            'organogram_path': organogram_path,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process each selected manual
        processed_manuals = []
        failed_manuals = []
        
        for manual_type in manual_types:
            if manual_type not in organogram.get('manuals', {}):
                print(f"⚠️  Manual type '{manual_type}' not found in organogram - skipping")
                failed_manuals.append(manual_type)
                continue
                
            print(f"\n🔄 Processing {manual_type}...")
            
            manual_info = organogram['manuals'][manual_type]
            manual_description = manual_info.get('description', f'{manual_type} Policy Manual')
            
            # Generate project name
            project_name = re.sub(r'[^a-zA-Z0-9\s]', '', manual_type)
            project_name = re.sub(r'\s+', '_', project_name).lower()[:30]
            
            try:
                # Check if project already exists
                project_dir = f"{project_name}_project"
                if os.path.exists(project_dir):
                    print(f"⚠️  Project '{project_name}' already exists. Skipping...")
                    processed_manuals.append(manual_type)
                    continue
                
                # Initialize project
                initializer = ProjectInitializer(client, project_name)
                
                # Get organogram-based policy responsibilities
                policy_info = initializer.determine_policy_responsibilities(manual_description)
                
                # Save project-specific information
                project_status = {
                    'manual_description': manual_description,
                    'created_date': datetime.now().isoformat(),
                    'stage': 1,
                    'stage_name': 'project_initiation',
                    'project_name': project_name,
                    'policy_type': policy_info['policy_type'],
                    'responsibilities': policy_info['responsibilities']
                }
                initializer.save_status(project_status)
                
                # Generate table of contents
                sections = []
                max_attempts = 3
                for attempt in range(max_attempts):
                    sections = initializer.generate_toc(manual_description)
                    if sections:
                        break
                    print(f"Attempt {attempt + 1} failed, retrying...")
                
                if not sections:
                    print(f"❌ Failed to generate TOC for: {manual_type}")
                    failed_manuals.append(manual_type)
                    continue
                
                # Save sections
                initializer.save_sections(sections)
                
                # Generate and save variables
                variables = initializer.generate_variables(manual_description)
                initializer.save_variables(variables, manual_description)
                
                # Update status
                initializer.save_status({
                    'stage': 1,
                    'stage_name': 'project_initiation',
                    'phase': 'stage_1_completed',
                    'total_sections': len(sections),
                    'completed_sections': 0,
                    'manual_description': manual_description,
                    'variables_count': len(variables),
                    'ready_for_stage_2': True
                })
                
                processed_manuals.append(manual_type)
                print(f"✅ {manual_type}: {len(sections)} sections, {len(variables)} variables")
                
            except Exception as e:
                print(f"❌ Failed to process {manual_type}: {str(e)}")
                failed_manuals.append(manual_type)
                continue
        
        # Save common configuration
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 GUI batch processing completed!")
        print(f"✅ Processed: {len(processed_manuals)} manuals")
        if failed_manuals:
            print(f"❌ Failed: {len(failed_manuals)} manuals")
        print(f"📄 Common config saved to: config.json")
        print(f"\n🚀 Next step: Use GUI or run 'python project_expansion.py' for Stage 2")
        
    except Exception as e:
        print(f"❌ Error during GUI batch processing: {e}")
        sys.exit(1)


def single_manual_mode():
    """Legacy single manual processing mode"""
    print("🚀 Single Policy Manual Project Initialization")
    print("=" * 50)
    
    # Load existing common config if available
    config_file = os.path.join(os.getcwd(), "config.json")
    existing_config = {}
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            print("📋 Found existing configuration - using saved settings")
            lm_studio_url = existing_config.get('lm_studio_url', 'http://localhost:1234')
            model_name = existing_config.get('model_name', 'local-model')
            print(f"   LM Studio URL: {lm_studio_url}")
            print(f"   Model Name: {model_name}")
        except Exception as e:
            print(f"⚠️  Could not load existing config: {e}")
            existing_config = {}
    
    # Get user input
    project_name = input("Enter project folder name: ").strip()
    if not project_name:
        print("❌ Project name is required!")
        return
    
    # Only ask for configuration if not found in existing config
    if not existing_config:
        print("\n⚙️  LM Studio Configuration Required")
        default_url = 'http://localhost:1234'
        lm_studio_url = input(f"Enter LM Studio URL (default: {default_url}): ").strip()
        if not lm_studio_url:
            lm_studio_url = default_url
        
        default_model = 'local-model'
        model_name = input(f"Enter model name (default: {default_model}): ").strip()
        if not model_name:
            model_name = default_model
    
    manual_description = input("Describe the policy manual you want to create: ").strip()
    if not manual_description:
        print("❌ Manual description is required!")
        return
    
    # Check if project already exists
    project_dir = f"{project_name}_project"
    if os.path.exists(project_dir):
        overwrite = input(f"Project '{project_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
        shutil.rmtree(project_dir)
    
    # Initialize client
    print(f"\n🔌 Connecting to LM Studio at {lm_studio_url}...")
    client = LMStudioClient(lm_studio_url, model_name)
    
    # Test connection
    if not client.test_connection():
        print("❌ Failed to connect to LM Studio. Please check the URL and ensure LM Studio is running.")
        return
    
    print("✅ Successfully connected to LM Studio!")
    
    # Initialize project
    initializer = ProjectInitializer(client, project_name)
    
    try:
        # Save common configuration (LM Studio settings)
        config = {
            'lm_studio_url': lm_studio_url,
            'model_name': model_name,
        }
        initializer.save_config(config)
        print(f"✅ Updated common configuration")
        
        # Get organogram-based policy responsibilities
        policy_info = initializer.determine_policy_responsibilities(manual_description)
        
        # Save project-specific information in status
        project_status = {
            'manual_description': manual_description,
            'created_date': datetime.now().isoformat(),
            'stage': 1,
            'stage_name': 'project_initiation',
            'project_name': project_name,
            'policy_type': policy_info['policy_type'],
            'responsibilities': policy_info['responsibilities']
        }
        initializer.save_status(project_status)
        
        # Generate table of contents with user review
        while True:
            sections = initializer.generate_toc(manual_description)
            
            # Allow user to review and modify descriptions
            should_regenerate = initializer.allow_user_modifications()
            
            if not should_regenerate:
                break  # User is satisfied with descriptions
        
        # Save sections
        initializer.save_sections(sections)
        
        # Generate variables
        variables = initializer.generate_variables(manual_description)
        initializer.save_variables(variables, manual_description)
        
        # Update status
        initializer.save_status({
            'stage': 1,
            'stage_name': 'project_initiation',
            'phase': 'stage_1_completed',
            'total_sections': len(sections),
            'completed_sections': 0,
            'manual_description': manual_description,
            'variables_count': len(variables),
            'ready_for_stage_2': True
        })
        
        print(f"\n🎉 Stage 1 (Project Initiation) completed!")
        print(f"📁 Project folder: {project_dir}")
        print(f"📄 Files created:")
        print(f"   - ../config.json (common configuration)")
        print(f"   - sections.json ({len(sections)} sections)")
        print(f"   - ../config/company.yaml (YAML configuration)")
        print(f"   - status.json (project status)")
        print(f"\n🚀 Next step: Run 'python project_expansion.py' for Stage 2 (Project Expansion)")
        print(f"   This will allow you to edit sections and add user notes.")
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return


if __name__ == "__main__":
    main()