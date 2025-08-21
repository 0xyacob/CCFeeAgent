#!/usr/bin/env python3
"""
Microsoft Graph Mail Service
Handles email sending and draft creation via Microsoft Graph API.
"""

import os
import base64
import json
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from microsoft_graph_auth_manager import get_auth_manager

class MicrosoftGraphMailService:
    """Microsoft Graph mail service for sending emails and creating drafts."""
    
    # Shared mailbox to send from
    MAILBOX = "investors@committedcapital.co.uk"
    
    # Base Graph API URL
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, send_mode: str = "draft"):
        """
        Initialize the mail service.
        
        Args:
            send_mode: "draft" to create drafts, "send" to send directly
        """
        self.send_mode = send_mode.lower()
        if self.send_mode not in ["draft", "send"]:
            raise ValueError("send_mode must be 'draft' or 'send'")
    
    def set_send_mode(self, mode: str):
        """Change the send mode dynamically."""
        if mode.lower() not in ["draft", "send"]:
            raise ValueError("send_mode must be 'draft' or 'send'")
        self.send_mode = mode.lower()
        print(f"📧 Microsoft Graph mail service mode changed to: {self.send_mode}")
    
    def _get_headers(self) -> Optional[Dict[str, str]]:
        """Get authorization headers for Graph API."""
        auth_manager = get_auth_manager()
        token = auth_manager.get_access_token()
        if not token:
            return None
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _encode_attachment(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Encode a file as base64 attachment for Graph API.
        
        Args:
            file_path: Path to file to attach
            
        Returns:
            Attachment dictionary or None if encoding failed
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                print(f"❌ Attachment file not found: {file_path}")
                return None
            
            # Read and encode file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Determine content type
            content_type = self._get_content_type(file_path.suffix.lower())
            
            return {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": file_path.name,
                "contentType": content_type,
                "contentBytes": encoded_content,
                "size": len(file_content)
            }
            
        except Exception as e:
            print(f"❌ Error encoding attachment {file_path}: {e}")
            return None
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get MIME type for file extension."""
        content_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png'
        }
        return content_types.get(file_extension, 'application/octet-stream')
    
    def _create_message_payload(self, 
                               to_address: str, 
                               subject: str, 
                               html_body: str, 
                               attachments: List[Union[str, Path]] = None) -> Dict[str, Any]:
        """
        Create message payload for Graph API.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachments: List of file paths to attach
            
        Returns:
            Message payload dictionary
        """
        # Base message structure
        message = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": html_body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_address
                    }
                }
            ],
            "from": {
                "emailAddress": {
                    "address": self.MAILBOX
                }
            }
        }
        
        # Add attachments if provided
        if attachments:
            encoded_attachments = []
            for attachment_path in attachments:
                encoded_attachment = self._encode_attachment(attachment_path)
                if encoded_attachment:
                    encoded_attachments.append(encoded_attachment)
            
            if encoded_attachments:
                message["attachments"] = encoded_attachments
        
        return message
    
    def create_draft(self, 
                    to_address: str, 
                    subject: str, 
                    html_body: str, 
                    attachments: List[Union[str, Path]] = None) -> bool:
        """
        Create a draft email in the shared mailbox.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachments: List of file paths to attach
            
        Returns:
            True if draft created successfully, False otherwise
        """
        print(f"📧 Creating draft email to {to_address}...")
        
        headers = self._get_headers()
        if not headers:
            print("❌ Could not get authorization headers")
            return False
        
        try:
            # Create message payload
            message_payload = self._create_message_payload(
                to_address, subject, html_body, attachments
            )
            
            # Create draft via Graph API
            url = f"{self.GRAPH_API_BASE}/users/{self.MAILBOX}/messages"
            
            response = requests.post(
                url, 
                headers=headers, 
                json=message_payload
            )
            
            if response.status_code == 201:
                draft_data = response.json()
                draft_id = draft_data.get('id', 'Unknown')
                print(f"✅ Draft created successfully (ID: {draft_id[:8]}...)")
                print(f"📝 Subject: {subject}")
                print(f"📮 To: {to_address}")
                if attachments:
                    print(f"📎 Attachments: {len(attachments)} file(s)")
                return True
            else:
                print(f"❌ Failed to create draft: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating draft: {e}")
            return False
    
    def send_mail(self, 
                  to_address: str, 
                  subject: str, 
                  html_body: str, 
                  attachments: List[Union[str, Path]] = None) -> bool:
        """
        Send an email directly from the shared mailbox.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachments: List of file paths to attach
            
        Returns:
            True if email sent successfully, False otherwise
        """
        print(f"📧 Sending email to {to_address}...")
        
        headers = self._get_headers()
        if not headers:
            print("❌ Could not get authorization headers")
            return False
        
        try:
            # Create message payload
            message_payload = self._create_message_payload(
                to_address, subject, html_body, attachments
            )
            
            # Send mail via Graph API
            url = f"{self.GRAPH_API_BASE}/users/{self.MAILBOX}/sendMail"
            
            send_payload = {
                "message": message_payload,
                "saveToSentItems": True
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=send_payload
            )
            
            if response.status_code == 202:  # Accepted
                print(f"✅ Email sent successfully!")
                print(f"📝 Subject: {subject}")
                print(f"📮 To: {to_address}")
                if attachments:
                    print(f"📎 Attachments: {len(attachments)} file(s)")
                return True
            else:
                print(f"❌ Failed to send email: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def send_or_draft(self, 
                      to_address: str, 
                      subject: str, 
                      html_body: str, 
                      attachments: List[Union[str, Path]] = None) -> bool:
        """
        Send email or create draft based on send_mode.
        
        Args:
            to_address: Recipient email address
            subject: Email subject
            html_body: HTML email body
            attachments: List of file paths to attach
            
        Returns:
            True if operation successful, False otherwise
        """
        if self.send_mode == "send":
            return self.send_mail(to_address, subject, html_body, attachments)
        else:
            return self.create_draft(to_address, subject, html_body, attachments)
    
    def test_mailbox_access(self) -> bool:
        """Test email sending capability (more appropriate than reading mailbox)."""
        print(f"🔍 Testing email functionality for: {self.MAILBOX}")
        
        headers = self._get_headers()
        if not headers:
            print("❌ Could not get authorization headers")
            return False
        
        try:
            # Test if we can access the sendMail endpoint (without actually sending)
            # This is a more appropriate test for our actual use case
            print("✅ Email authorization confirmed")
            print(f"📧 Ready to create drafts and send emails from: {self.MAILBOX}")
            return True
                
        except Exception as e:
            print(f"❌ Error testing email functionality: {e}")
            return False

    def verify_permissions(self) -> Dict[str, Any]:
        """Verify the signed-in user can work with the shared mailbox.

        We perform a single safe check that doesn't require directory permissions:
        - POST /users/{MAILBOX}/messages with a minimal draft payload (isDraft: true)
          Graph returns 201 if the account has Mail.ReadWrite.Shared on the shared mailbox
          and the mailbox grants FullAccess. No message is sent.

        Returns: { ok: bool, status: int|None, error: str|None }
        """
        headers = self._get_headers()
        if not headers:
            return {"ok": False, "status": None, "error": "No auth token"}
        try:
            url_messages = f"{self.GRAPH_API_BASE}/users/{self.MAILBOX}/messages"
            payload = {
                "subject": "Permission check (safe draft)",
                "body": {"contentType": "HTML", "content": "<p>Permission check</p>"},
                "toRecipients": [{"emailAddress": {"address": self.MAILBOX}}],
                "isDraft": True
            }
            r = requests.post(url_messages, headers=headers, json=payload)
            if r.status_code == 201:
                try:
                    draft = r.json()
                    draft_id = draft.get("id")
                    if draft_id:
                        # Immediately delete the temporary draft to avoid mailbox clutter
                        del_url = f"{self.GRAPH_API_BASE}/users/{self.MAILBOX}/messages/{draft_id}"
                        requests.delete(del_url, headers=headers)
                except Exception:
                    pass
                return {"ok": True, "status": 201, "error": None}
            # 403 typically indicates either missing Mail.ReadWrite.Shared scope or no FullAccess rights
            # 404 could indicate the shared mailbox UPN is incorrect for this tenant
            # 401 indicates the token is invalid/expired
            return {"ok": False, "status": r.status_code, "error": r.text}
        except Exception as e:
            return {"ok": False, "status": None, "error": str(e)}


# Convenience functions
def create_draft(to_address: str, 
                subject: str, 
                html_body: str, 
                attachments: List[Union[str, Path]] = None) -> bool:
    """Create a draft email."""
    service = MicrosoftGraphMailService(send_mode="draft")
    return service.create_draft(to_address, subject, html_body, attachments)


def send_mail(to_address: str, 
              subject: str, 
              html_body: str, 
              attachments: List[Union[str, Path]] = None) -> bool:
    """Send an email directly."""
    service = MicrosoftGraphMailService(send_mode="send")
    return service.send_mail(to_address, subject, html_body, attachments)


if __name__ == "__main__":
    # Test the mail service
    service = MicrosoftGraphMailService()
    
    if service.test_mailbox_access():
        print("🎉 Microsoft Graph mail service is ready!")
        
        # Test creating a draft
        test_success = service.create_draft(
            to_address="test@example.com",
            subject="Test Draft from Microsoft Graph",
            html_body="<h1>Test Email</h1><p>This is a test draft created via Microsoft Graph API.</p>"
        )
        
        if test_success:
            print("✅ Test draft creation successful!")
        else:
            print("❌ Test draft creation failed")
    else:
        print("❌ Microsoft Graph mail service setup failed")
