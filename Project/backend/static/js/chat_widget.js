document.addEventListener("DOMContentLoaded", () => {
    const widgetHTML = `
      <div class="chatbot-widget" id="chatbotWidget">
        <div class="chatbot-panel" id="chatbotPanel" hidden>
          <div class="chatbot-header">
            <span class="chatbot-title">
              <span class="brand-icon">◈</span> Cyber AI
            </span>
            <button id="chatbotClose" class="chatbot-close" aria-label="Close Chat">×</button>
          </div>
          <div class="chatbot-messages" id="chatbotMessages">
            <div class="chat-bubble ai">Hello. Sentinel AI is online. How can I assist you with cybersecurity today?</div>
          </div>
          <div class="chatbot-input-area">
            <input type="text" id="chatbotInput" placeholder="Ask about threats, indicators..." autocomplete="off" />
            <button id="chatbotSend" aria-label="Send">
              <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
        </div>
        <button class="chatbot-toggle" id="chatbotToggle" aria-label="Open Chat">
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" class="toggle-icon"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </button>
      </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', widgetHTML);

    const chatToggle = document.getElementById("chatbotToggle");
    const chatPanel = document.getElementById("chatbotPanel");
    const chatClose = document.getElementById("chatbotClose");
    const chatInput = document.getElementById("chatbotInput");
    const chatSend = document.getElementById("chatbotSend");
    const chatMessages = document.getElementById("chatbotMessages");

    chatToggle.addEventListener("click", () => {
      chatPanel.hidden = !chatPanel.hidden;
      if (!chatPanel.hidden) {
        chatInput.focus();
      }
    });

    chatClose.addEventListener("click", () => {
      chatPanel.hidden = true;
    });

    function appendMessage(text, sender) {
      const bubble = document.createElement("div");
      bubble.className = `chat-bubble ${sender}`;
      bubble.textContent = text;
      chatMessages.appendChild(bubble);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return bubble;
    }

    async function sendChatMessage() {
      const text = chatInput.value.trim();
      if (!text) return;

      appendMessage(text, "user");
      chatInput.value = "";
      chatInput.disabled = true;
      chatSend.disabled = true;

      const loadingBubble = appendMessage("Typing...", "ai loading");

      try {
        // use authFetch to inherit our JWT authentication token automatically!
        const r = await authFetch(`/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
        });
        
        if (!r.ok) throw new Error("API error");
        const data = await r.json();
        loadingBubble.remove();
        
        if (data.success && data.response) {
          appendMessage(data.response, "ai");
        } else {
          throw new Error(data.error || "Invalid response");
        }
      } catch (e) {
        loadingBubble.remove();
        appendMessage("Error: Could not connect to AI. Please try again.", "ai");
      } finally {
        chatInput.disabled = false;
        chatSend.disabled = false;
        chatInput.focus();
      }
    }

    chatSend.addEventListener("click", sendChatMessage);
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendChatMessage();
      }
    });
});
