#!/usr/bin/env python3
"""
Configuration Manager for Committed Capital Fee Automation System
Handles user settings, Excel file paths, and cross-platform config storage.
"""

import os
import json
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd


class ConfigManager:
    """Manages user configuration with cross-platform support."""
    
    def __init__(self):
        self.config_file = self._get_config_path()
        self.config_data = self._load_config()
    
    def _get_config_path(self) -> Path:
        """Get platform-specific config file path."""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            config_dir = Path.home() / "Library" / "Application Support" / "CommittedCapital"
        elif system == "Windows":
            config_dir = Path(os.environ.get("APPDATA", Path.home())) / "CommittedCapital"
        else:  # Linux and others
            config_dir = Path.home() / ".config" / "CommittedCapital"
        
        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        return config_dir / "fee_automation_config.json"
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file: {e}")
            return {}
    
    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error: Could not save config file: {e}")
            return False
    
    def get_excel_path(self) -> Optional[str]:
        """Get the configured Excel file path."""
        return self.config_data.get("excel_path")
    
    def set_excel_path(self, path: str) -> bool:
        """Set the Excel file path after validation."""
        validation_result = self.validate_excel_file(path)
        if validation_result[0]:  # Valid
            self.config_data["excel_path"] = path
            return self._save_config()
        return False
    
    def validate_excel_file(self, path: str) -> Tuple[bool, str]:
        """
        Validate Excel file and return (is_valid, error_message).
        
        Args:
            path: Path to Excel file
            
        Returns:
            Tuple of (is_valid: bool, error_message: str)
        """
        if not path:
            return False, "No file path provided"
        
        file_path = Path(path)
        
        # Check if file exists
        if not file_path.exists():
            return False, f"File does not exist: {path}"
        
        # Check if it's actually a file (not a directory)
        if not file_path.is_file():
            return False, f"Path is not a file: {path}"
        
        # Check file extension
        if file_path.suffix.lower() not in ['.xlsx', '.xls']:
            return False, f"File must be an Excel file (.xlsx or .xls): {file_path.suffix}"
        
        # Check if it's a cloud placeholder (common issue with OneDrive/SharePoint)
        if file_path.stat().st_size < 1024:  # Less than 1KB is suspicious
            return False, f"File appears to be a cloud placeholder or is too small. Ensure the file is fully synced from OneDrive/SharePoint."
        
        try:
            # Try to read Excel file and validate sheets
            excel_file = pd.ExcelFile(path)
            sheet_names = excel_file.sheet_names
            
            # Required sheets
            required_sheets = ['FeeSheet', 'InvestorSheet', 'CompanySheet']
            missing_sheets = [sheet for sheet in required_sheets if sheet not in sheet_names]
            
            if missing_sheets:
                return False, f"Missing required sheets: {', '.join(missing_sheets)}. Found sheets: {', '.join(sheet_names)}"
            
            # Validate required columns in each sheet
            validation_errors = []
            
            # FeeSheet validation
            try:
                fee_sheet = pd.read_excel(path, sheet_name='FeeSheet', nrows=1)
                required_fee_cols = ['Custodian Client Ref', 'Subscription code', 'Fund', 'Gross/Net', 
                                   'CC Set up fee %', 'CC AMC %', 'CC Carry %']
                missing_fee_cols = [col for col in required_fee_cols if col not in fee_sheet.columns]
                if missing_fee_cols:
                    validation_errors.append(f"FeeSheet missing columns: {', '.join(missing_fee_cols)}")
            except Exception as e:
                validation_errors.append(f"Could not read FeeSheet: {str(e)}")
            
            # InvestorSheet validation
            try:
                investor_sheet = pd.read_excel(path, sheet_name='InvestorSheet', nrows=1)
                required_investor_cols = ['Custodian Client Ref', 'Investor Name', 'Salutation', 
                                        'First Name', 'Last Name', 'Contact email']
                missing_investor_cols = [col for col in required_investor_cols if col not in investor_sheet.columns]
                if missing_investor_cols:
                    validation_errors.append(f"InvestorSheet missing columns: {', '.join(missing_investor_cols)}")
            except Exception as e:
                validation_errors.append(f"Could not read InvestorSheet: {str(e)}")
            
            # CompanySheet validation
            try:
                company_sheet = pd.read_excel(path, sheet_name='CompanySheet', nrows=1)
                required_company_cols = ['Company Name', 'Current Share Price', 'Share Class']
                missing_company_cols = [col for col in required_company_cols if col not in company_sheet.columns]
                if missing_company_cols:
                    validation_errors.append(f"CompanySheet missing columns: {', '.join(missing_company_cols)}")
            except Exception as e:
                validation_errors.append(f"Could not read CompanySheet: {str(e)}")
            
            if validation_errors:
                return False, "Excel file validation failed:\n• " + "\n• ".join(validation_errors)
            
            excel_file.close()
            return True, "Excel file is valid"
            
        except Exception as e:
            return False, f"Could not read Excel file: {str(e)}"
    
    def is_first_run(self) -> bool:
        """Check if this is the first run (no Excel path configured)."""
        return self.get_excel_path() is None
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings."""
        return self.config_data.copy()
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific setting."""
        self.config_data[key] = value
        return self._save_config()
    
    def reset_config(self) -> bool:
        """Reset configuration to defaults."""
        self.config_data = {}
        return self._save_config()


# Global config manager instance
config_manager = ConfigManager()
