Fake News Extension - Backend + Extension Integration

Overview
- Flask backend exposes endpoints for text/profile/url/image analysis at `http://localhost:5000`.
- Chrome extension (in `Chrome-ext/`) sends scraped tweet data to `/api/classify-all`.
- Groq LLM wrappers (in `ml-model/`) use the `GROQ_API_KEY` environment variable.

Setup
1. Create a Python virtual environment and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Set your `GROQ_API_KEY` securely. Do NOT commit your key to the repository.

Options:
- Create a local `.env` file (ignored by `.gitignore`) with the line:
  - `GROQ_API_KEY=your_key_here`
- Or export the environment variable in PowerShell before running the server:

```powershell
$env:GROQ_API_KEY = 'your_key_here'
```

Using an environment variable is recommended for security.

Run
- Start the Flask API:

```powershell
python "fake news extension\app.py"
```

- Load the Chrome extension:
  - Open `chrome://extensions` → toggle Developer mode → "Load unpacked" → select the `Chrome-ext` directory.
  - Click the extension icon → use the popup to fetch page text and call the backend.

Notes
- The Groq key is read from `GROQ_API_KEY` in environment or `.env`.
- The backend includes `/api/classify-all` which returns a structured JSON used by the extension.
- If you want me to remove the `.env` file and instead show how to set the key securely on your host, tell me and I'll update instructions.
