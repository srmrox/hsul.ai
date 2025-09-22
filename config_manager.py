#!/usr/bin/env python3
"""
Configuration Manager for Policy Manual Generation System
Handles YAML-based configuration with validation and variable substitution.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigManager:
    """Manages YAML-based configuration with validation and variable substitution."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "company.yaml"
        self.config_data = {}
        self.load_config()
    
    def load_config(self) -> bool:
        """Load configuration from YAML file."""
        try:
            if not self.config_file.exists():
                print(f"⚠️  Configuration file not found: {self.config_file}")
                return False
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config_data = yaml.safe_load(f) or {}
                
            print(f"Configuration loaded from {self.config_file}")
            return True
            
        except yaml.YAMLError as e:
            print(f"YAML parsing error: {e}")
            return False
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to YAML file."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Update metadata
            if 'metadata' not in self.config_data:
                self.config_data['metadata'] = {}
            self.config_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, indent=2, allow_unicode=True)
                
            print(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set configuration value using dot notation."""
        try:
            keys = key_path.split('.')
            data = self.config_data
            
            # Navigate to the parent dictionary
            for key in keys[:-1]:
                if key not in data:
                    data[key] = {}
                data = data[key]
            
            # Set the final value
            data[keys[-1]] = value
            return True
            
        except Exception as e:
            print(f"Error setting {key_path}: {e}")
            return False
    
    def validate(self) -> ValidationResult:
        """Validate configuration against defined rules."""
        errors = []
        warnings = []
        
        validation_rules = self.get('validation', {})
        required_fields = validation_rules.get('required_fields', [])
        field_patterns = validation_rules.get('field_patterns', {})
        field_types = validation_rules.get('field_types', {})
        
        # Check required fields
        for field_path in required_fields:
            value = self.get(field_path)
            if value is None or value == "":
                errors.append(f"Required field missing: {field_path}")
        
        # Check field patterns
        for field_path, pattern in field_patterns.items():
            value = self.get(field_path)
            if value and not re.match(pattern, str(value)):
                errors.append(f"Invalid format for {field_path}: {value}")
        
        # Check field types (enum validation)
        for field_path, allowed_values in field_types.items():
            value = self.get(field_path)
            if value and value not in allowed_values:
                errors.append(f"Invalid value for {field_path}: {value}. Must be one of: {allowed_values}")
        
        # Additional validation checks
        self._validate_contact_info(errors, warnings)
        self._validate_dates(errors, warnings)
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)
    
    def _validate_contact_info(self, errors: List[str], warnings: List[str]):
        """Validate contact information."""
        email = self.get('organization.contact.digital.email')
        if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            errors.append(f"Invalid email format: {email}")
            
        phone = self.get('organization.contact.phone.main')
        if phone and not re.match(r'^\+\d{10,15}$', phone):
            warnings.append(f"Phone number format should include country code: {phone}")
    
    def _validate_dates(self, errors: List[str], warnings: List[str]):
        """Validate date fields."""
        fiscal_start = self.get('organization.operations.fiscal_year.start')
        fiscal_end = self.get('organization.operations.fiscal_year.end')
        
        if fiscal_start and fiscal_end:
            # Basic date format validation
            try:
                datetime.strptime(fiscal_start, '%B %d')
                datetime.strptime(fiscal_end, '%B %d')
            except ValueError:
                errors.append("Invalid fiscal year date format. Use 'Month DD' format.")
    
    def get_variables_dict(self) -> Dict[str, str]:
        """Generate variables dictionary for backward compatibility."""
        variables = {}
        
        # Basic organization info
        variables['COMPANY_NAME'] = self.get('organization.profile.name', '')
        variables['COMPANY_LEGAL_NAME'] = self.get('organization.profile.legal_name', '')
        variables['COMPANY_SHORT_NAME'] = self.get('organization.profile.short_name', '')
        
        # Contact information
        variables['COMPANY_EMAIL'] = self.get('organization.contact.digital.email', '')
        variables['COMPANY_WEBSITE'] = self.get('organization.contact.digital.website', '')
        variables['COMPANY_PHONE'] = self.get('organization.contact.phone.main', '')
        variables['EMERGENCY_CONTACT'] = self.get('organization.contact.phone.emergency', variables['COMPANY_PHONE'])
        
        # Address (construct full address)
        address_parts = [
            self.get('organization.contact.address.street', ''),
            self.get('organization.contact.address.area', ''),
            self.get('organization.contact.address.city', ''),
            self.get('organization.contact.address.postal_code', ''),
            self.get('organization.contact.address.country', '')
        ]
        variables['COMPANY_ADDRESS'] = ', '.join(filter(None, address_parts))
        
        # Legal and operations
        variables['JURISDICTION'] = self.get('organization.legal.jurisdiction', '')
        variables['BUSINESS_HOURS'] = f"{self.get('organization.operations.business_hours.days', '')}, {self.get('organization.operations.business_hours.weekdays', '')}"
        variables['FISCAL_YEAR'] = f"{self.get('organization.operations.fiscal_year.start', '')} to {self.get('organization.operations.fiscal_year.end', '')}"
        
        # Policy settings
        variables['DOCUMENT_CLASSIFICATION'] = self.get('organization.policies.classification', 'Internal Use')
        variables['SCOPE_EMPLOYEES'] = "All employees, contractors, and temporary staff"  # Default value
        
        # Remove empty variables
        return {k: v for k, v in variables.items() if v}
    
    def apply_templates(self, text: str) -> str:
        """Apply variable substitution using templates."""
        if not text:
            return text
            
        # Get template definitions
        templates = self.get('templates', {})
        
        # Apply template substitutions
        for template_name, template_value in templates.items():
            placeholder = f"{{{template_name}}}"
            if placeholder in text:
                resolved_value = self.resolve_template(template_value)
                text = text.replace(placeholder, resolved_value)
        
        # Apply direct variable substitutions
        variables = self.get_variables_dict()
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(var_value))
        
        return text
    
    def resolve_template(self, template: str) -> str:
        """Resolve a template string with dot notation references."""
        if not template:
            return ""
            
        # Find all {organization.path.to.value} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        
        result = template
        for match in matches:
            value = self.get(match, "")
            result = result.replace(f"{{{match}}}", str(value))
        
        return result
    
    def get_categories(self) -> Dict[str, Dict]:
        """Get configuration organized by categories for GUI display."""
        return {
            "Company Profile": {
                "name": "organization.profile.name",
                "legal_name": "organization.profile.legal_name",
                "short_name": "organization.profile.short_name",
                "industry": "organization.profile.industry",
                "size": "organization.profile.size"
            },
            "Contact Information": {
                "email": "organization.contact.digital.email",
                "website": "organization.contact.digital.website",
                "main_phone": "organization.contact.phone.main",
                "emergency_phone": "organization.contact.phone.emergency",
                "street": "organization.contact.address.street",
                "area": "organization.contact.address.area",
                "city": "organization.contact.address.city",
                "postal_code": "organization.contact.address.postal_code",
                "country": "organization.contact.address.country"
            },
            "Legal & Compliance": {
                "jurisdiction": "organization.legal.jurisdiction",
                "governing_law": "organization.legal.governing_law",
                "regulatory_body": "organization.legal.regulatory_body",
                "registration_number": "organization.legal.registration_number",
                "tax_id": "organization.legal.tax_id"
            },
            "Operations": {
                "business_days": "organization.operations.business_hours.days",
                "business_hours": "organization.operations.business_hours.weekdays",
                "timezone": "organization.operations.business_hours.timezone",
                "fiscal_start": "organization.operations.fiscal_year.start",
                "fiscal_end": "organization.operations.fiscal_year.end",
                "current_fiscal": "organization.operations.fiscal_year.current_year"
            },
            "Policy Settings": {
                "classification": "organization.policies.classification",
                "version_control": "organization.policies.version_control",
                "review_cycle": "organization.policies.review_cycle",
                "approval_authority": "organization.policies.approval_authority"
            }
        }
    
    def get_field_info(self, field_path: str) -> Dict[str, Any]:
        """Get information about a specific field for GUI display."""
        validation_rules = self.get('validation', {})
        field_types = validation_rules.get('field_types', {})
        required_fields = validation_rules.get('required_fields', [])
        
        return {
            'value': self.get(field_path),
            'is_required': field_path in required_fields,
            'allowed_values': field_types.get(field_path),
            'field_type': self._infer_field_type(field_path),
            'description': self._get_field_description(field_path)
        }
    
    def _infer_field_type(self, field_path: str) -> str:
        """Infer the GUI field type based on field path and value."""
        if 'email' in field_path.lower():
            return 'email'
        elif 'phone' in field_path.lower():
            return 'phone'
        elif 'website' in field_path.lower():
            return 'url'
        elif field_path.endswith('version_control'):
            return 'boolean'
        elif 'date' in field_path.lower():
            return 'date'
        else:
            return 'text'
    
    def _get_field_description(self, field_path: str) -> str:
        """Get user-friendly description for field."""
        descriptions = {
            'organization.profile.name': 'Company display name',
            'organization.profile.legal_name': 'Full legal company name',
            'organization.contact.digital.email': 'Primary contact email',
            'organization.contact.phone.main': 'Main phone number with country code',
            'organization.legal.jurisdiction': 'Legal jurisdiction (country/state)',
            'organization.operations.business_hours.weekdays': 'Working hours (e.g., 9:00 AM - 5:00 PM)',
            'organization.operations.business_hours.days': 'Working days (e.g., Monday to Friday)',
        }
        return descriptions.get(field_path, field_path.split('.')[-1].replace('_', ' ').title())

# Singleton instance for global access
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def main():
    """Test the ConfigManager."""
    config = ConfigManager()
    
    print("Testing ConfigManager")
    print("=" * 40)
    
    # Test loading
    print(f"Company Name: {config.get('organization.profile.name')}")
    print(f"Email: {config.get('organization.contact.digital.email')}")
    
    # Test validation
    validation = config.validate()
    if validation.is_valid:
        print("Configuration is valid")
    else:
        print("Configuration errors:")
        for error in validation.errors:
            print(f"  - {error}")
    
    # Test variable generation
    variables = config.get_variables_dict()
    print(f"Generated {len(variables)} variables")
    for key, value in list(variables.items())[:5]:  # Show first 5
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()