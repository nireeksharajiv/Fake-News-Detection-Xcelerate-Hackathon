// This listens for messages from the popup (popup.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "GET_PAGE_TEXT") {
    // Get all visible text from the page
    const bodyText = document.body.innerText || "";

    // Trim and limit so it's not too huge
    const trimmed = bodyText.trim().substring(0, 5000); // first 5000 characters

    // Send text back to the popup
    sendResponse({ text: trimmed });
  }

  // Return true to indicate we may send response asynchronously (good practice)
  return true;
});
