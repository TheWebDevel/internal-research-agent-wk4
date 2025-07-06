import webbrowser
import os

def open_google_console():
    print("🔗 Opening Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/")

def print_setup_steps():
    print("\n" + "="*60)
    print("🔧 SIMPLIFIED GOOGLE OAUTH SETUP")
    print("="*60)

    print("\n1. 📋 GOOGLE CLOUD CONSOLE:")
    print("   • Browser should open to console.cloud.google.com")
    print("   • Sign in with your Google account")

    print("\n2. 🏗️  CREATE/SELECT PROJECT:")
    print("   • Create new project or select existing")
    print("   • Note your Project ID")

    print("\n3. 🔌 ENABLE APIS:")
    print("   • Go to 'APIs & Services' > 'Library'")
    print("   • Search and enable:")
    print("     - Google Docs API")
    print("     - Google Drive API")

    print("\n4. ⚙️  CREDENTIALS:")
    print("   • Go to 'APIs & Services' > 'Credentials'")
    print("   • Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   • If prompted for consent screen:")
    print("     - Fill in App name: 'MCP Insurance Server'")
    print("     - Add your email as support contact")
    print("     - Add your email as test user")
    print("   • Choose 'Desktop application'")
    print("   • Name: 'MCP Insurance Server'")
    print("   • Leave JavaScript origins and redirect URIs empty")

    print("\n5. 📥 DOWNLOAD:")
    print("   • Download the JSON credentials file")
    print("   • Copy values to credentials.json (in root directory)")

    print("\n6. 🧪 TEST:")
    print("   • Run: python test_connection.py")

    print("\n" + "="*60)

def check_current_files():
    print("\n📁 CURRENT FILES:")

    files_to_check = [
        ("credentials.json", "Credentials file"),
        (".env", "Environment configuration"),
        ("test_connection.py", "Test script"),
        ("fastmcp_server.py", "MCP server")
    ]

    for filename, description in files_to_check:
        if os.path.exists(filename):
            print(f"   ✅ {filename} - {description}")
        else:
            print(f"   ❌ {filename} - {description} (missing)")

if __name__ == "__main__":
    print("🔍 Google OAuth Setup Checker")
    print("="*40)

    check_current_files()
    print_setup_steps()

    response = input("\n🤔 Open Google Cloud Console in browser? (y/n): ")
    if response.lower() in ['y', 'yes']:
        open_google_console()

    print("\n💡 TIP: If you get stuck, just focus on:")
    print("   1. Enable the APIs")
    print("   2. Create OAuth 2.0 Client ID (Desktop)")
    print("   3. Download the JSON file")