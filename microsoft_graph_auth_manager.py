#!/usr/bin/env python3
"""
Microsoft Graph Authentication Manager
Intelligently chooses between Service Principal and Device Flow authentication.
Provides seamless experience for both enterprise and individual deployments.
"""

import os
from typing import Optional, Dict, Any, Literal
from microsoft_graph_auth import MicrosoftGraphAuth
from microsoft_graph_service_auth import MicrosoftGraphServiceAuth, initialize_service_auth, is_service_auth_available

AuthMode = Literal["auto", "service", "device"]

class MicrosoftGraphAuthManager:
    """
    Smart authentication manager that automatically chooses the best auth method.
    
    Priority:
    1. Service Principal (if client secret available) - Best for enterprise
    2. Device Flow (fallback) - Works for individual users
    """
    
    def __init__(self, auth_mode: AuthMode = "auto", client_secret: Optional[str] = None):
        """
        Initialize the authentication manager.
        
        Args:
            auth_mode: Authentication mode - "auto", "service", or "device"
            client_secret: Azure client secret for service principal auth
        """
        self.auth_mode = auth_mode
        self.client_secret = client_secret
        self._service_auth = None
        self._device_auth = None
        self._active_auth = None
        self._active_mode = None
        
        # Initialize based on mode
        self._initialize_auth()
    
    def _initialize_auth(self):
        """Initialize the appropriate authentication method."""
        if self.auth_mode == "service":
            # Force service principal only
            self._init_service_auth()
        elif self.auth_mode == "device":
            # Force device flow only
            self._init_device_auth()
        else:
            # Auto mode - try service first, fallback to device
            if not self._init_service_auth():
                self._init_device_auth()
    
    def _init_service_auth(self) -> bool:
        """Initialize service principal authentication."""
        try:
            self._service_auth = MicrosoftGraphServiceAuth(self.client_secret)
            if self._service_auth.test_connection():
                self._active_auth = self._service_auth
                self._active_mode = "service"
                print("🏢 Using Service Principal authentication (enterprise mode)")
                return True
        except Exception as e:
            print(f"⚠️  Service Principal auth not available: {e}")
        
        return False
    
    def _init_device_auth(self) -> bool:
        """Initialize device flow authentication."""
        try:
            self._device_auth = MicrosoftGraphAuth()
            self._active_auth = self._device_auth
            self._active_mode = "device"
            print("👤 Using Device Flow authentication (user mode)")
            return True
        except Exception as e:
            print(f"❌ Device Flow auth failed: {e}")
            return False
    
    def get_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """
        Get access token using the active authentication method.
        
        Args:
            force_refresh: Force a new token acquisition
            
        Returns:
            Access token string or None if authentication failed
        """
        if not self._active_auth:
            print("❌ No authentication method available")
            return None
        
        token = self._active_auth.get_access_token(force_refresh)
        
        # If service auth fails and we're in auto mode, try device auth
        if not token and self.auth_mode == "auto" and self._active_mode == "service":
            print("⚠️  Service Principal auth failed, falling back to Device Flow...")
            if self._init_device_auth():
                token = self._active_auth.get_access_token(force_refresh)
        
        return token
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get current user/service information."""
        if not self._active_auth:
            return None
        
        user_info = self._active_auth.get_user_info()
        
        # Add auth mode info
        if user_info:
            user_info["auth_mode"] = self._active_mode
            user_info["auth_type"] = "Service Principal" if self._active_mode == "service" else "User Account"
        
        return user_info
    
    def test_connection(self) -> bool:
        """Test the active authentication connection."""
        if not self._active_auth:
            return False
        
        return self._active_auth.test_connection()
    
    def clear_cache(self):
        """Clear authentication caches."""
        if self._service_auth:
            self._service_auth.clear_cache()
        if self._device_auth:
            self._device_auth.clear_cache()
    
    def get_auth_status(self) -> Dict[str, Any]:
        """Get detailed authentication status."""
        return {
            "active_mode": self._active_mode,
            "auth_mode_setting": self.auth_mode,
            "service_available": self._service_auth is not None,
            "device_available": self._device_auth is not None,
            "is_authenticated": self._active_auth is not None,
            "is_enterprise": self._active_mode == "service"
        }
    
    def switch_to_device_flow(self) -> bool:
        """Manually switch to device flow authentication."""
        print("🔄 Switching to Device Flow authentication...")
        return self._init_device_auth()
    
    def switch_to_service_principal(self, client_secret: Optional[str] = None) -> bool:
        """
        Manually switch to service principal authentication.
        
        Args:
            client_secret: Azure client secret (if different from initialization)
        """
        print("🔄 Switching to Service Principal authentication...")
        if client_secret:
            self.client_secret = client_secret
        return self._init_service_auth()


# Global authentication manager instance
auth_manager = None

def get_auth_manager(auth_mode: AuthMode = "auto", client_secret: Optional[str] = None) -> MicrosoftGraphAuthManager:
    """
    Get or create the global authentication manager.
    
    Args:
        auth_mode: Authentication mode preference
        client_secret: Azure client secret for service principal
    
    Returns:
        MicrosoftGraphAuthManager instance
    """
    global auth_manager
    
    if auth_manager is None:
        auth_manager = MicrosoftGraphAuthManager(auth_mode, client_secret)
    
    return auth_manager

def initialize_enterprise_auth(client_secret: str) -> bool:
    """
    Initialize enterprise authentication with service principal.
    
    Args:
        client_secret: Azure client secret
    
    Returns:
        True if successful, False otherwise
    """
    global auth_manager
    auth_manager = MicrosoftGraphAuthManager("service", client_secret)
    return auth_manager.test_connection()

def get_access_token(force_refresh: bool = False) -> Optional[str]:
    """Convenience function to get access token."""
    manager = get_auth_manager()
    return manager.get_access_token(force_refresh)

def get_user_info() -> Optional[Dict[str, Any]]:
    """Convenience function to get user info."""
    manager = get_auth_manager()
    return manager.get_user_info()
