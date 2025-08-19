#!/usr/bin/env python3
"""
Microsoft Graph API Authentication Module
Handles device code flow authentication for accessing shared mailbox.
"""

import os
import json
import msal
from pathlib import Path
from typing import Optional, Dict, Any

class MicrosoftGraphAuth:
    """Microsoft Graph API authentication using device code flow."""
    
    # Azure App Registration details
    TENANT_ID = "5f429cd1-a68e-432d-ae9c-f8a933508f67"
    CLIENT_ID = "f59227de-b96d-409f-8beb-2a82d29c8908"
    
    # Required scopes for shared mailbox access
    SCOPES = [
        "User.Read",
        "Mail.ReadWrite.Shared",
        "Mail.Send.Shared"
    ]
    
    def __init__(self):
        """Initialize the authentication client."""
        # Use a persistent token cache location
        cache_location = Path.home() / ".msal_token_cache"
        cache_location.mkdir(exist_ok=True)
        cache_file = cache_location / "msal_cache.json"
        
        # Initialize token cache
        token_cache = msal.SerializableTokenCache()
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    token_cache.deserialize(f.read())
            except Exception as e:
                print(f"Warning: Could not load token cache: {e}")
        
        self.cache_file = cache_file
        self.app = msal.PublicClientApplication(
            client_id=self.CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{self.TENANT_ID}",
            token_cache=token_cache
        )
    

    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get access token, using device code flow if needed.
        
        Args:
            force_refresh: Force a new device code authentication
            
        Returns:
            Access token string or None if authentication failed
        """
        # First try to get token silently from cache
        if not force_refresh:
            accounts = self.app.get_accounts()
            if accounts:
                try:
                    result = self.app.acquire_token_silent(
                        scopes=self.SCOPES,
                        account=accounts[0]
                    )
                    if result and "access_token" in result:
                        self._save_cache()
                        return result["access_token"]
                except Exception as e:
                    print(f"Silent token acquisition failed: {e}")
        
        # If silent acquisition failed, use device code flow
        print("🔐 Microsoft Graph authentication required...")
        
        try:
            # Initiate device code flow
            flow = self.app.initiate_device_flow(scopes=self.SCOPES)
            
            if "user_code" not in flow:
                print("❌ Failed to create device code flow")
                return None
            
            # Display device code instructions
            print("\n" + "="*60)
            print("🔑 MICROSOFT GRAPH AUTHENTICATION REQUIRED")
            print("="*60)
            print(f"📱 Go to: {flow['verification_uri']}")
            print(f"🔢 Enter code: {flow['user_code']}")
            print("⏰ Waiting for authentication...")
            print("="*60)
            
            # Complete the flow
            result = self.app.acquire_token_by_device_flow(flow)
            
            if "access_token" in result:
                print("✅ Authentication successful!")
                self._save_cache()
                return result["access_token"]
            else:
                error = result.get("error", "Unknown error")
                error_desc = result.get("error_description", "")
                print(f"❌ Authentication failed: {error}")
                if error_desc:
                    print(f"   Details: {error_desc}")
                return None
                
        except Exception as e:
            print(f"❌ Device code authentication error: {e}")
            return None
    
    def _save_cache(self):
        """Save the token cache to disk."""
        try:
            if self.app.token_cache.has_state_changed:
                with open(self.cache_file, 'w') as f:
                    f.write(self.app.token_cache.serialize())
        except Exception as e:
            print(f"Warning: Could not save token cache: {e}")
    

    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user information."""
        token = self.get_access_token()
        if not token:
            return None
        
        try:
            import requests
            
            response = requests.get(
                "https://graph.microsoft.com/v1.0/me?$select=id,displayName,mail",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the Microsoft Graph connection."""
        print("🔍 Testing Microsoft Graph connection...")
        
        token = self.get_access_token()
        if not token:
            print("❌ Could not obtain access token")
            return False
        
        user_info = self.get_user_info()
        if user_info:
            print(f"✅ Connected as: {user_info.get('displayName', 'Unknown')} ({user_info.get('mail', 'No email')})")
            return True
        else:
            print("❌ Could not retrieve user information")
            return False
    
    def clear_cache(self):
        """Clear the token cache (force re-authentication)."""
        # MSAL handles token caching internally
        print("ℹ️ Token cache is handled internally by MSAL")


# Global instance
graph_auth = MicrosoftGraphAuth()


def get_access_token() -> Optional[str]:
    """Convenience function to get access token."""
    return graph_auth.get_access_token()


if __name__ == "__main__":
    # Test the authentication
    auth = MicrosoftGraphAuth()
    if auth.test_connection():
        print("🎉 Microsoft Graph authentication is working!")
    else:
        print("❌ Microsoft Graph authentication failed")
