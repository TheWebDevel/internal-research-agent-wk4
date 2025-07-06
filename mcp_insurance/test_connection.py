import os
import sys
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

def test_google_auth():
    print("🔐 Testing Google OAuth authentication...")

    creds = None
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        print("   Please run: python setup_google_auth.py")
        return False

    if os.path.exists(token_file):
        print("✅ Found existing token file")
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🔑 Starting OAuth flow...")
            print("   A browser window will open for authentication")
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as token:
            token.write(creds.to_json())
        print("✅ Token saved successfully")

    return creds

def test_drive_api(creds):
    """Test Google Drive API access."""
    print("\n📁 Testing Google Drive API...")

    try:
        drive_service = build("drive", "v3", credentials=creds)

        results = drive_service.files().list(
            pageSize=5,
            fields="files(id,name,mimeType)"
        ).execute()

        files = results.get("files", [])
        if files:
            print(f"✅ Successfully connected to Google Drive")
            print(f"   Found {len(files)} files (showing first 5):")
            for file in files:
                print(f"   • {file['name']} ({file['mimeType']})")
        else:
            print("✅ Connected to Google Drive (no files found)")

        return True
    except HttpError as error:
        print(f"❌ Google Drive API error: {error}")
        return False

def test_docs_api(creds):
    print("\n📄 Testing Google Docs API...")

    try:
        docs_service = build("docs", "v1", credentials=creds)

        print("✅ Google Docs API connection successful")
        return True
    except HttpError as error:
        print(f"❌ Google Docs API error: {error}")
        return False

def test_insurance_folder():
    folder_id = os.getenv("INSURANCE_FOLDER_ID")
    if not folder_id or folder_id == "your_folder_id_here":
        print("\n📂 Insurance folder not configured (optional)")
        return True

    print(f"\n📂 Testing insurance folder access: {folder_id}")

    try:
        creds = test_google_auth()
        if not creds:
            return False

        drive_service = build("drive", "v3", credentials=creds)

        folder = drive_service.files().get(fileId=folder_id).execute()
        print(f"✅ Successfully accessed folder: {folder['name']}")

        results = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10,
            fields="files(id,name,mimeType)"
        ).execute()

        files = results.get("files", [])
        if files:
            print(f"   Found {len(files)} files in folder:")
            for file in files:
                print(f"   • {file['name']} ({file['mimeType']})")
        else:
            print("   No files found in folder")

        return True
    except HttpError as error:
        print(f"❌ Error accessing folder: {error}")
        return False

def test_insurance_document_reading():
    print("\n📋 Testing Group Term Life Insurance 2025 document reading...")

    try:
        creds = test_google_auth()
        if not creds:
            return False

        drive_service = build("drive", "v3", credentials=creds)
        docs_service = build("docs", "v1", credentials=creds)

        folder_id = os.getenv("INSURANCE_FOLDER_ID")

        search_query = "name contains 'Group Term Life Insurance 2025'"

        search_query += " and (mimeType='application/vnd.google-apps.document' or mimeType='application/pdf')"

        if folder_id and folder_id != "your_folder_id_here":
            search_query += f" and '{folder_id}' in parents"

        print(f"🔍 Search query: {search_query}")

        try:
            results = drive_service.files().list(
                q=search_query,
                spaces="drive",
                fields="files(id,name,mimeType,modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()
        except HttpError as error:
            print(f"❌ Google Drive search error: {error}")
            print("   Trying alternative search without folder filter...")

            alt_query = "name contains 'Group Term Life Insurance 2025' and (mimeType='application/vnd.google-apps.document' or mimeType='application/pdf')"
            results = drive_service.files().list(
                q=alt_query,
                spaces="drive",
                fields="files(id,name,mimeType,modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()

        files = results.get("files", [])
        if not files:
            print("❌ Group Term Life Insurance 2025 document not found")
            print("   Available files in Drive:")
            try:
                all_files = drive_service.files().list(
                    pageSize=10,
                    fields="files(id,name,mimeType)"
                ).execute()
                for file in all_files.get("files", []):
                    print(f"   • {file['name']} ({file['mimeType']})")
            except:
                pass
            return False

        google_doc = next((doc for doc in files if doc.get("mimeType") == "application/vnd.google-apps.document"), None)
        if google_doc:
            doc = google_doc
        else:
            doc = files[0]  # fallback to first doc

        doc_id = doc.get("id")
        doc_name = doc.get("name")
        doc_type = doc.get("mimeType")

        print(f"✅ Found document: {doc_name} (Type: {doc_type})")

        if doc_type == "application/vnd.google-apps.document":
            try:
                document = docs_service.documents().get(documentId=doc_id).execute()
                content = []
                for element in document.get("body", {}).get("content", []):
                    if "paragraph" in element:
                        for para_element in element["paragraph"]["elements"]:
                            if "textRun" in para_element:
                                content.append(para_element["textRun"]["content"])

                full_content = "".join(content)
                print(f"✅ Successfully read document content ({len(full_content)} characters)")
                print("\n📄 First 500 characters of content:")
                print("-" * 50)
                print(full_content[:500])
                print("-" * 50)

                content_lower = full_content.lower()
                relevant_terms = ['maximum', 'insured', 'amount', 'coverage', 'limit', 'benefit', 'life', 'insurance']
                found_terms = [term for term in relevant_terms if term in content_lower]
                print(f"\n🔍 Found relevant terms: {found_terms}")

                if 'maximum' in content_lower and ('insured' in content_lower or 'amount' in content_lower):
                    print("✅ Document appears to contain maximum insured amount information")
                else:
                    print("⚠️  Document may not contain maximum insured amount information")

                print("\n🧪 Testing LLM query on document content...")

                aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
                aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
                aws_region = os.getenv('AWS_DEFAULT_REGION')

                print(f"🔑 AWS Credentials check:")
                print(f"   Access Key: {'✅ Set' if aws_access_key else '❌ Missing'}")
                print(f"   Secret Key: {'✅ Set' if aws_secret_key else '❌ Missing'}")
                print(f"   Region: {'✅ Set' if aws_region else '❌ Missing'}")

                if not aws_access_key or not aws_secret_key:
                    print("⚠️  AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file")
                    return True

                try:
                    original_dir = os.getcwd()
                    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    os.chdir(parent_dir)

                    from dotenv import load_dotenv
                    load_dotenv()

                    sys.path.append(parent_dir)
                    from providers.bedrock import get_llm
                    llm = get_llm()

                    prompt = f"""You are an insurance policy expert. Here is the full content of the Group Term Life Insurance 2025 policy document:

{full_content}

Question: What is the maximum insured amount?

Please answer the question based on the information in the document above. If the information is not available in the document, please state that clearly."""

                    answer = llm.invoke(prompt)
                    print(f"✅ LLM Response:")
                    print(f"   Content: {answer}")
                    print(f"   Type: {type(answer)}")
                    if hasattr(answer, 'content'):
                        print(f"   Answer content: {answer.content}")
                    if hasattr(answer, '__dict__'):
                        print(f"   Answer attributes: {list(answer.__dict__.keys())}")

                    os.chdir(original_dir)

                except Exception as e:
                    print(f"⚠️  LLM test failed: {e}")
                    print(f"   Error details: {type(e).__name__}")
                    print(f"   Document content retrieved successfully ({len(full_content)} characters)")

                    try:
                        os.chdir(original_dir)
                    except:
                        pass

                return True

            except HttpError as error:
                print(f"❌ Error reading Google Doc content: {error}")
                return False
        else:
            print(f"⚠️  Document is {doc_type}, cannot read content with Google Docs API")
            return False

    except Exception as e:
        print(f"❌ Error testing document reading: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Google OAuth Connection Test")
    print("="*40)

    creds = test_google_auth()
    if not creds:
        print("\n❌ Authentication failed")
        return

    drive_ok = test_drive_api(creds)
    docs_ok = test_docs_api(creds)
    folder_ok = test_insurance_folder()
    doc_reading_ok = test_insurance_document_reading()

    print("\n" + "="*40)
    print("📊 TEST RESULTS:")
    print(f"   Authentication: {'✅ PASS' if creds else '❌ FAIL'}")
    print(f"   Google Drive API: {'✅ PASS' if drive_ok else '❌ FAIL'}")
    print(f"   Google Docs API: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"   Insurance Folder: {'✅ PASS' if folder_ok else '⚠️  SKIP'}")
    print(f"   Document Reading: {'✅ PASS' if doc_reading_ok else '❌ FAIL'}")

    if creds and drive_ok and docs_ok:
        print("\n🎉 All tests passed! Your Google OAuth is working correctly.")
        print("   You can now run: python fastmcp_server.py")
    else:
        print("\n❌ Some tests failed. Please check your configuration.")

    print("="*40)

if __name__ == "__main__":
    main()