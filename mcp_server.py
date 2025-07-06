import os
import json
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

print("[MCP SERVER] Starting simplified MCP Insurance Server...", flush=True)

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

class GoogleDocsService:
    def __init__(self):
        self.creds = None
        self.docs_service = None
        self.drive_service = None
        self.insurance_folder_id = os.getenv("INSURANCE_FOLDER_ID")
        self._authenticated = False

    def authenticate(self):
        if self._authenticated:
            return
        creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open(token_file, "w") as token:
                token.write(self.creds.to_json())
        self.docs_service = build("docs", "v1", credentials=self.creds)
        self.drive_service = build("drive", "v3", credentials=self.creds)
        self._authenticated = True

    def get_document_content(self, document_id: str) -> str:
        """Get content from a specific Google Doc."""
        print(f"[MCP SERVER] get_document_content called with ID: {document_id}", flush=True)

        try:
            self.authenticate()

            if not self.docs_service:
                print("[MCP SERVER] Docs service not available", flush=True)
                return "Error: Google Docs service not available"

            if not document_id:
                print("[MCP SERVER] No document ID provided", flush=True)
                return "Error: No document ID provided"

            print(f"[MCP SERVER] Fetching document {document_id}...", flush=True)
            document = self.docs_service.documents().get(documentId=document_id).execute()

            content = []
            for element in document.get("body", {}).get("content", []):
                if "paragraph" in element:
                    for para_element in element["paragraph"]["elements"]:
                        if "textRun" in para_element:
                            content.append(para_element["textRun"]["content"])

            result = "".join(content)
            print(f"[MCP SERVER] Retrieved document content ({len(result)} chars)", flush=True)
            return result

        except Exception as e:
            print(f"[MCP SERVER] Exception in get_document_content: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc()
            return f"Error retrieving document: {str(e)}"

gdocs = GoogleDocsService()

mcp = FastMCP("insurance-server")

print("[MCP SERVER] Registering single tool...", flush=True)

@mcp.tool()
def get_document_content(document_id: str) -> str:
    """Get content from a specific insurance document by ID."""
    return gdocs.get_document_content(document_id)

print("[MCP SERVER] get_document_content tool registered", flush=True)

if __name__ == "__main__":
    print("[MCP SERVER] Starting simplified server...", flush=True)
    print("📋 Available tool:")
    print("   - get_document_content: Get document content by ID")
    print("🔗 Server ready to accept connections...")
    print("💡 Note: Google OAuth credentials required for full functionality")
    print("-" * 50)

    try:
        mcp.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)