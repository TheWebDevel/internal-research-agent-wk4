import json
from pathlib import Path

def create_credentials_template():
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID_HERE.apps.googleusercontent.com",
            "project_id": "YOUR_PROJECT_ID",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET_HERE",
            "redirect_uris": ["http://localhost"]
        }
    }

    credentials_file = Path("../credentials.json")
    if not credentials_file.exists():
        with open(credentials_file, "w") as f:
            json.dump(template, f, indent=2)
        print("✅ Created credentials.json template in root directory")
        print("📝 Please replace the placeholder values with your actual Google OAuth credentials")
    else:
        print("ℹ️  credentials.json already exists in root directory")

def create_env_template():
    """Create a .env template file."""
    env_template = """# Google OAuth Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json

# Google Drive Folder ID (optional)
# Set this to a specific folder ID to limit searches to that folder
INSURANCE_FOLDER_ID=your_folder_id_here

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
"""

    env_file = Path("../.env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_template)
        print("✅ Created .env template in root directory")
        print("📝 Please update the .env file with your configuration")
    else:
        print("ℹ️  .env file already exists in root directory")

def print_setup_instructions():
    print("\n" + "="*60)
    print("🔧 GOOGLE OAUTH SETUP INSTRUCTIONS")
    print("="*60)
    print("\n1. GOOGLE CLOUD CONSOLE SETUP:")
    print("   • Go to https://console.cloud.google.com/")
    print("   • Create a new project or select existing one")
    print("   • Enable APIs: Google Docs API, Google Drive API")
    print("   • Go to 'APIs & Services' > 'Credentials'")
    print("   • Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   • Choose 'Desktop application'")
    print("   • Download the credentials file")
    print("\n2. UPDATE CREDENTIALS:")
    print("   • Replace the placeholder values in credentials.json (in root directory)")
    print("   • Update .env file with your folder ID (optional)")
    print("\n3. UPLOAD YOUR SAMPLE PDF:")
    print("   • Upload your sample PDF to Google Drive")
    print("   • Note the folder ID if you want to limit searches")
    print("\n4. TEST THE CONNECTION:")
    print("   • Run: python test_connection.py (from root directory)")
    print("\n5. START THE SERVER:")
    print("   • Run: python mcp_server.py (from root directory)")
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🚀 Setting up Google OAuth configuration...")
    create_credentials_template()
    create_env_template()
    print_setup_instructions()