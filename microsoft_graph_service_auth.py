#!/usr/bin/env python3
"""
Microsoft Graph Service Principal Authentication
Enterprise-grade authentication using client credentials flow.
No user interaction required - perfect for multi-user deployments.
"""

import os
import json
import msal
import requests
from pathlib import Path
from typing import Optional, Dict, Any

class MicrosoftGraphServiceAuth:
    """Microsoft Graph API authentication using service principal (client credentials flow)."""
    
    # Azure App Registration details
    TENANT_ID = "5f429cd1-a68e-432d-ae9c-f8a933508f67"
    CLIENT_ID = "f59227de-b96d-409f-8beb-2a82d29c8908"
    
    # Required scopes for service principal (different from user scopes)
    SCOPES = ["https://graph.microsoft.com/.default"]
    
    def __init__(self, client_secret: Optional[str] = None):
        """
        Initialize the service principal authentication.
        
        Args:
            client_secret: Azure app client secret. If None, will try to get from environment.
        """
        # Get client secret from parameter or environment
        self.client_secret = client_secret or os.getenv('AZURE_CLIENT_SECRET')
        
        if not self.client_secret:
            raise ValueError(
                "Client secret is required for service principal authentication. "
                "Provide it as parameter or set AZURE_CLIENT_SECRET environment variable."
            )
        
        # Initialize MSAL confidential client
        self.app = msal.ConfidentialClientApplication(
            client_id=self.CLIENT_ID,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.TENANT_ID}"
        )
        
        # Cache for access token
        self._cached_token = None
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get access token using client credentials flow.
        
        Args:
            force_refresh: Force a new token acquisition
            
        Returns:
            Access token string or None if authentication failed
        """
        # Return cached token if valid and not forcing refresh
        if not force_refresh and self._cached_token:
            # Check if token is still valid (simple check - tokens usually last 1 hour)
            # In production, you'd want more sophisticated token validation
            return self._cached_token.get("access_token")
        
        try:
            # Acquire token using client credentials
            result = self.app.acquire_token_for_client(scopes=self.SCOPES)
            
            if "access_token" in result:
                self._cached_token = result
                print("✅ Service principal authentication successful!")
                return result["access_token"]
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                print(f"❌ Service principal authentication failed: {error_msg}")
                return None
                
        except Exception as e:
            print(f"❌ Service principal authentication error: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get service principal information (different from user info).
        
        Returns:
            Service principal info or None if failed
        """
        token = self.get_access_token()
        if not token:
            return None
        
        try:
            # For service principals, we can get app info instead of user info
            response = requests.get(
                f"https://graph.microsoft.com/v1.0/applications?$filter=appId eq '{self.CLIENT_ID}'&$select=id,displayName,appId",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("value"):
                    app_info = data["value"][0]
                    return {
                        "id": app_info.get("id"),
                        "displayName": f"Service: {app_info.get('displayName', 'Unknown App')}",
                        "mail": "service@committedcapital.co.uk",  # Service account indicator
                        "userPrincipalName": "service-principal"
                    }
            
            # Fallback info
            return {
                "displayName": "Service Principal",
                "mail": "service@committedcapital.co.uk",
                "userPrincipalName": "service-principal"
            }
                
        except Exception as e:
            print(f"Error getting service principal info: {e}")
            return {
                "displayName": "Service Principal",
                "mail": "service@committedcapital.co.uk",
                "userPrincipalName": "service-principal"
            }
    
    def test_connection(self) -> bool:
        """Test the Microsoft Graph connection."""
        print("🔍 Testing Microsoft Graph service principal connection...")
        
        token = self.get_access_token()
        if not token:
            print("❌ Could not obtain access token")
            return False
        
        # Test by trying to access Graph API
        try:
            response = requests.get(
                "https://graph.microsoft.com/v1.0/organization",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                print("✅ Service principal connection successful!")
                return True
            else:
                print(f"❌ Service principal connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Service principal connection error: {e}")
            return False
    
    def clear_cache(self):
        """Clear the token cache."""
        self._cached_token = None
        print("ℹ️ Service principal token cache cleared")


# Global service auth instance (will be initialized when client secret is available)
service_auth = None

def initialize_service_auth(client_secret: Optional[str] = None) -> bool:
    """
    Initialize the global service auth instance.
    
    Args:
        client_secret: Azure app client secret
        
    Returns:
        True if initialization successful, False otherwise
    """
    global service_auth
    
    try:
        service_auth = MicrosoftGraphServiceAuth(client_secret)
        return service_auth.test_connection()
    except Exception as e:
        print(f"❌ Failed to initialize service authentication: {e}")
        return False

def is_service_auth_available() -> bool:
    """Check if service authentication is available and working."""
    global service_auth
    
    if not service_auth:
        # Try to initialize with environment variable
        return initialize_service_auth()
    
    return service_auth.test_connection()
