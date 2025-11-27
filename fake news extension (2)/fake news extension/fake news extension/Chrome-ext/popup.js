// Backend URL (Flask API)
const BACKEND_URL = "http://localhost:5000/api/classify-all";

const textInput = document.getElementById("textInput");
const getTextBtn = document.getElementById("getTextBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const resultDiv = document.getElementById("result");
const statusDiv = document.getElementById("status");

// 1) When user clicks "Get Page Text"
getTextBtn.addEventListener("click", async () => {
  statusDiv.textContent = "Getting page text...";
  resultDiv.textContent = "";

  try {
    // Get current active tab (the one you are looking at)
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    // Send message to contentScript.js in that tab
    chrome.tabs.sendMessage(
      tab.id,
      { type: "GET_PAGE_TEXT" },
      (response) => {
        if (chrome.runtime.lastError) {
          statusDiv.textContent = "Error: " + chrome.runtime.lastError.message;
          return;
        }
        if (response && response.text) {
          textInput.value = response.text;
          statusDiv.textContent = "Page text loaded. You can edit before analyzing.";
        } else {
          statusDiv.textContent = "No text found on this page.";
        }
      }
    );
  } catch (err) {
    statusDiv.textContent = "Failed to get tab info.";
    console.error(err);
  }
});

// 2) When user clicks "Analyze"
analyzeBtn.addEventListener("click", async () => {
  const text = textInput.value.trim();
  if (!text) {
    statusDiv.textContent = "Please enter or load some text first.";
    return;
  }

  statusDiv.textContent = "Analyzing...";
  resultDiv.textContent = "";

  // Payload expected by the Flask `/api/classify-all` endpoint
  const payload = {
    tweet_text: text,
    profile: null,
    urls: [],
    image_base64: null
  };

  try {
    const response = await fetch(BACKEND_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    renderResult(data);
    statusDiv.textContent = "Analysis complete.";
  } catch (err) {
    console.error(err);
    statusDiv.textContent = "Error contacting backend.";
    resultDiv.textContent = err.message;
  }
});

// 3) Show backend result nicely
function renderResult(data) {
  // Parse new response structure
  const overall = data.overall || {};
  const tweet = data.tweet || {};
  const profileRes = data.profile || {};
  const urls = data.urls || [];
  const image = data.image || null;

  let html = '';
  if (overall.classification) html += `<div><strong>Overall:</strong> ${overall.classification} (${overall.confidence}%)</div>`;
  if (tweet.classification) html += `<div>Tweet: ${tweet.classification} (${tweet.probability}%)</div>`;
  if (profileRes.classification) html += `<div>Profile: ${profileRes.classification} (${profileRes.probability}%)</div>`;
  if (urls.length > 0) {
    html += '<div><strong>URLs</strong><ul>';
    for (const u of urls) {
      html += `<li>${u.url} — ${u.classification} (${u.probability}%)</li>`;
    }
    html += '</ul></div>';
  }
  if (image) {
    html += `<div>Image: ${image.label || image.classification || 'UNKNOWN'} (${image.score || 'N/A'}%)</div>`;
  }

  if (!html) html = 'No detailed data received from backend.';
  resultDiv.innerHTML = html;
}
