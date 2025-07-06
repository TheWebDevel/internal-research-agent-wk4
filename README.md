# 🤖 Annet: The Internal HR Policy & Insurance Research Agent

Welcome to **Annet**! Your AI-powered HR and insurance research assistant for Presidio. Annet answers all your HR policy questions, fetches insurance info from Google Docs, and even surfs the web for public info—all in a single, friendly chat interface! 🎉

## 🚀 What Can Annet Do?

- **HR Policy Q&A**: Instantly answers questions about your company's HR policies using smart RAG (vector search over internal PDFs).
- **Insurance Queries**: Connects to Google Drive to fetch and answer insurance-related questions for Presidio employees.
- **Web Search**: Uses SerpAPI (Google Search) to answer public/external questions (never mixes internal and external info!).
- **Smart Tool Selection**: Always uses the right tool for the job—no more mixing up sources!
- **Citations & References**: Every response includes proper citations and tool usage information.
- **Fun, Fast, and Secure**: All your data stays safe, and Annet is always ready to help with a smile. 😄

## 🎥 Demo Video
[Link to Demo in GDrive. The demo is too large to upload on GitHub 😅](https://drive.google.com/file/d/1IZGkkV53tqPtv4xfc4qZQhwAC1ZU_O63/view?usp=sharing)

## 🛠️ Tech Stack

### **Core Framework**
- **LangChain**: AI application framework for building LLM-powered applications
- **Streamlit**: Web app framework for creating beautiful, interactive UIs
- **AWS Bedrock**: Managed LLM service for Claude and other foundation models

### **AI & ML**
- **Claude 3 Sonnet**: Primary LLM for reasoning and text generation
- **Sentence Transformers**: Local embeddings for document similarity search
- **ChromaDB**: Vector database for storing and retrieving document embeddings

### **Data & Storage**
- **Google Drive API**: Access to insurance documents stored in Google Drive
- **Google Docs API**: Reading and parsing Google Doc content
- **PyPDF2**: PDF processing and text extraction from HR policy documents

### **Integration & Communication**
- **MCP (Model Context Protocol)**: Standardized protocol for tool integration
- **SerpAPI**: Google Search API for public/external information
- **Google OAuth 2.0**: Secure authentication for Google services

### **Development & Deployment**
- **Python 3.12**: Core programming language
- **FastMCP**: MCP server implementation for insurance tools
- **Environment Management**: Consolidated .env configuration

### **Security & Best Practices**
- **Environment Variables**: Secure credential management
- **Rate Limiting**: Web search protection and caching (1 second between searches)
- **Tool Isolation**: Strict separation between internal and external data sources
- **API Key Management**: Secure storage of SerpAPI, AWS, and Google credentials


## 🛠️ Installation & Setup

1. **Clone the Repo**

2. **Install Python Dependencies**

```bash
pip install -r requirements.txt
```

3. **Set Up Environment Variables**

- Copy the example env file and fill in your secrets:

```bash
cp env.example .env
# Edit .env with your AWS, Google, SerpAPI, and MCP config
```

**Required API Keys:**
- **AWS Bedrock**: For LLM access
- **SerpAPI**: For web search functionality (get free key from [serpapi.com](https://serpapi.com/))
- **Google OAuth**: For insurance document access

4. **Google Cloud Credentials**

- **Option A: Automatic Setup**
  ```bash
  cd mcp_insurance
  python setup_google_auth.py
  ```
  This will create template files and guide you through the setup process.

- **Option B: Manual Setup**
  - Place your Google OAuth credentials JSON (`credentials.json`) **and** the Google OAuth token file (`token.json`) in the root directory.
  - If you don't have `token.json`, it will be generated on first authentication.
  - See Google Cloud docs for setup and consent screen configuration.

- **Quick Setup Commands:**
  ```bash
  # Check current setup status
  python mcp_insurance/check_google_setup.py

  # Update credentials (if you have downloaded JSON)
  python mcp_insurance/update_credentials.py

  # Test the connection
  python mcp_insurance/test_connection.py
  ```

5. **Prepare HR Policy Documents**

- Put your HR policy PDFs in the `data/hr_policies/` folder (not just `hr_policies/`).
  - Example: `data/hr_policies/leave_policy.pdf`

6. **Configure SerpAPI for Web Search**

- **Get a Free API Key**: Sign up at [serpapi.com](https://serpapi.com/) (free tier includes 100 searches/month)
- **Add to Environment**: Add your SerpAPI key to the `.env` file:
  ```bash
  SERPAPI_KEY=your_serpapi_key_here
  ```
- **Test Web Search**: The web search tool will automatically use SerpAPI for external queries

7. **Run the MCP Insurance Server**

> **Note:** The MCP server is started automatically by the client. You do NOT need to run it manually!

---

## 💬 Usage

- **Start the Chat App:**

```bash
streamlit run main.py
```

- **Ask Anything!**
  - "What is the leave policy?"
  - "What is the maximum insured amount for health insurance?"
  - "What is the latest news about remote work in India?"

- **See the Magic:**
  - Annet will pick the right tool (RAG, MCP, or WebSearch) and answer you with a friendly, cited response.

---

## 🧪 Testing & Troubleshooting

### **Google OAuth Setup Testing**
```bash
# Test Google OAuth connection
python mcp_insurance/test_connection.py

# Check setup status
python mcp_insurance/check_google_setup.py

# Update credentials if needed
python mcp_insurance/update_credentials.py
```

### **MCP Server Testing**
```bash
# Test MCP server (from root directory)
python mcp_server.py

# Test insurance tools
python mcp_insurance/test_connection.py
```

### **Web Search Testing**
```bash
# Test SerpAPI web search
python -c "from dotenv import load_dotenv; load_dotenv(); from providers.websearch import web_search, get_search_status; print('Status:', get_search_status()); result = web_search('latest AI news'); print('Result:', result.get('answer', 'No result')[:100] + '...')"
```

### **Common Issues**
- **"Credentials not found"**: Run `python mcp_insurance/setup_google_auth.py`
- **"Token expired"**: Delete `token.json` and re-authenticate
- **"MCP connection failed"**: Ensure MCP server is running from root directory
- **"Rate limited"**: Use the "Clear Cache" button in the Streamlit sidebar
- **"SerpAPI not configured"**: Add your SerpAPI key to the `.env` file


## 🤩 Why You'll Love Annet

- **No more searching through endless PDFs!**
- **Instant, accurate answers—always from the right source.**
- **Easy to set up, fun to use, and secure by design.**

## 🧑‍💻 Contributing

PRs welcome! Please open an issue or discussion for big changes.


## 📄 License

MIT

*Made with ❤️ for Presidio Innovation Sprint Enablement*
