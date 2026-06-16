/* ══════════════════════════════════════════
   app.js — NayePankh AI Hub Frontend Logic

   Blocks:
     1. Config
     2. Chat state
     3. Chat widget open/close
     4. Send message
     5. Register form
     6. Load stats + charts
     7. Count-up animation
══════════════════════════════════════════ */

// ─────────────────────────────────────────
// BLOCK 1 — CONFIG
// ─────────────────────────────────────────
// Change this to your Render URL after deployment, e.g.:
// const API_BASE = "https://nayepankh-ai-hub.onrender.com";
const API_BASE = "http://localhost:8000";

// ─────────────────────────────────────────
// BLOCK 2 — CHAT STATE
// ─────────────────────────────────────────
let messages = [];          // Full conversation history sent to /chat
let isChatOpen = false;
let deptChart = null;
let cityChart = null;

// ─────────────────────────────────────────
// BLOCK 3 — CHAT WIDGET OPEN / CLOSE
// ─────────────────────────────────────────
function openChat() {
  const panel = document.getElementById("chat-panel");
  panel.classList.remove("chat-closed");
  panel.classList.add("chat-open");
  isChatOpen = true;
  document.getElementById("chat-input").focus();
  scrollMessages();
}

function closeChat() {
  const panel = document.getElementById("chat-panel");
  panel.classList.remove("chat-open");
  panel.classList.add("chat-closed");
  isChatOpen = false;
}

function toggleChat() {
  if (isChatOpen) {
    closeChat();
  } else {
    openChat();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  // Bind chat buttons
  const navChatBtn = document.getElementById("nav-chat-btn");
  const heroChatBtn = document.getElementById("hero-chat-btn");
  const chatToggleBtn = document.getElementById("chat-toggle-btn");
  const chatCloseBtn = document.getElementById("chat-close-btn");
  const chatSendBtn = document.getElementById("chat-send-btn");
  const chatInput = document.getElementById("chat-input");

  if(navChatBtn) navChatBtn.addEventListener("click", openChat);
  if(heroChatBtn) heroChatBtn.addEventListener("click", openChat);
  if(chatToggleBtn) chatToggleBtn.addEventListener("click", toggleChat);
  if(chatCloseBtn) chatCloseBtn.addEventListener("click", closeChat);
  if(chatSendBtn) chatSendBtn.addEventListener("click", sendMessage);
  
  if(chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") sendMessage();
    });
  }
});

// ─────────────────────────────────────────
// BLOCK 4 — SEND MESSAGE
// ─────────────────────────────────────────
async function sendMessage() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text) return;

  // Clear input
  input.value = "";

  // Add user bubble to UI
  appendMessage("user", text);

  // Push to conversation history
  messages.push({ role: "user", content: text });

  // Show typing indicator
  showTyping();

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages })
    });

    const data = await res.json();
    const reply = data.reply || "Sorry, I couldn't get a response. Please try again.";

    // Remove typing indicator
    hideTyping();

    // Add Pakhi's response to UI
    appendMessage("pakhi", reply);

    // Push to conversation history
    messages.push({ role: "assistant", content: reply });

  } catch (err) {
    hideTyping();
    appendMessage("pakhi", "⚠️ I'm having trouble connecting to the server. Please make sure the backend is running at localhost:8000.");
  }
}

function appendMessage(sender, text) {
  const container = document.getElementById("chat-messages");

  const wrapper = document.createElement("div");
  wrapper.className = "message flex flex-col " + (sender === "user" ? "items-end" : "items-start");

  if (sender === "pakhi") {
    const label = document.createElement("span");
    label.className = "text-xs text-gray-400 mb-1 ml-1";
    label.textContent = "Pakhi";
    wrapper.appendChild(label);
  }

  const bubble = document.createElement("div");
  bubble.className = "max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed";

  if (sender === "user") {
    bubble.style.cssText = "background:#2E7D32; color:white; border-bottom-right-radius:4px;";
    bubble.textContent = text;
  } else {
    bubble.style.cssText = "background:#F0F0F0; color:#1A1A1A; border-top-left-radius:4px;";
    // Support basic markdown-style line breaks
    bubble.innerHTML = text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br/>");
  }

  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  scrollMessages();
}

function showTyping() {
  const container = document.getElementById("chat-messages");
  const wrapper = document.createElement("div");
  wrapper.className = "message flex flex-col items-start";

  const label = document.createElement("span");
  label.className = "text-xs text-gray-400 mb-1 ml-1";
  label.textContent = "Pakhi";
  wrapper.appendChild(label);

  const indicator = document.createElement("div");
  indicator.id = "typing-indicator";
  indicator.innerHTML = `
    <div class="dot"></div><div class="dot"></div><div class="dot"></div>
    <span style="font-size:10px;color:#888;margin-left:6px;">Pakhi is waking up… first response may take ~30s on free tier</span>
  `;
  wrapper.appendChild(indicator);
  container.appendChild(wrapper);
  scrollMessages();
}

function hideTyping() {
  // Remove the entire wrapper that contains the typing indicator
  const indicator = document.getElementById("typing-indicator");
  if (indicator) {
    const wrapper = indicator.closest(".message") || indicator.parentElement;
    if (wrapper && wrapper !== indicator) {
      wrapper.remove();
    } else {
      indicator.remove();
    }
  }
}

function scrollMessages() {
  const container = document.getElementById("chat-messages");
  container.scrollTop = container.scrollHeight;
}

// ─────────────────────────────────────────
// BLOCK 5 — REGISTER FORM
// ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("register-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name         = document.getElementById("reg-name").value.trim();
    const email        = document.getElementById("reg-email").value.trim();
    const skills       = document.getElementById("reg-skills").value.trim();
    const city         = document.getElementById("reg-city").value.trim();
    const hours        = parseInt(document.getElementById("reg-hours").value);
    const submitBtn    = document.getElementById("reg-submit");
    const errorDiv     = document.getElementById("reg-error");

    // Reset error
    errorDiv.classList.add("hidden");
    errorDiv.textContent = "";

    // Disable button
    submitBtn.disabled = true;
    submitBtn.textContent = "Matching you...";

    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name, email, skills, city, hours_per_week: hours
        })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        // Show success card
        document.getElementById("register-card").classList.add("hidden");
        document.getElementById("register-success").classList.remove("hidden");
        document.getElementById("success-name").textContent = `Welcome, ${data.name}! 🌱`;
        document.getElementById("success-dept").textContent = data.department;

        // Refresh stats
        loadStats();

        // Fire Confetti Animation
        if (typeof confetti !== "undefined") {
          confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#2E7D32', '#4CAF50', '#FF6F00', '#FFA000']
          });
        }
      } else {
        throw new Error(data.detail || "Registration failed. Please try again.");
      }

    } catch (err) {
      errorDiv.textContent = err.message;
      errorDiv.classList.remove("hidden");
      submitBtn.disabled = false;
      submitBtn.textContent = "🎯 Find My Department";
    }
  });
});

// ─────────────────────────────────────────
// BLOCK 6 — LOAD STATS + CHARTS
// ─────────────────────────────────────────
async function loadStats() {
  // Placeholder data for empty state
  const placeholder = {
    total: 0,
    by_department: {
      "Tech and Media": 2,
      "Education": 1,
      "Food Relief": 1,
      "Women Empowerment": 1,
      "Fundraising": 1
    },
    by_city: {
      "Kanpur": 3,
      "Ghaziabad": 2,
      "Delhi": 1
    }
  };

  let data = placeholder;

  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (res.ok) {
      const fetched = await res.json();
      // Use live data if volunteers exist, else keep placeholder for charts
      if (fetched.total > 0) {
        data = fetched;
      } else {
        data.total = 0; // show 0 for volunteer count
      }
    }
  } catch {
    // Backend not running — use placeholder silently
  }

  // Update live volunteer count in stats bar
  animateCount("stat-volunteers", data.total);

  // Render / update department doughnut chart
  const deptCtx = document.getElementById("dept-chart").getContext("2d");
  const deptLabels = Object.keys(data.by_department);
  const deptValues = Object.values(data.by_department);

  if (deptChart) deptChart.destroy();
  deptChart = new Chart(deptCtx, {
    type: "doughnut",
    data: {
      labels: deptLabels,
      datasets: [{
        data: deptValues,
        backgroundColor: [
          "#2E7D32", "#4CAF50", "#FF6F00", "#FFA000", "#81C784"
        ],
        borderWidth: 2,
        borderColor: "#fff"
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: "bottom", labels: { font: { size: 11 }, padding: 12 } }
      }
    }
  });

  // Render / update city bar chart
  const cityCtx = document.getElementById("city-chart").getContext("2d");
  const cityLabels = Object.keys(data.by_city);
  const cityValues = Object.values(data.by_city);

  if (cityChart) cityChart.destroy();
  cityChart = new Chart(cityCtx, {
    type: "bar",
    data: {
      labels: cityLabels,
      datasets: [{
        label: "Volunteers",
        data: cityValues,
        backgroundColor: "#4CAF50",
        borderRadius: 8,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1, font: { size: 11 } },
          grid: { color: "#f0f0f0" }
        },
        x: {
          ticks: { font: { size: 11 } },
          grid: { display: false }
        }
      }
    }
  });
}

// ─────────────────────────────────────────
// BLOCK 7 — COUNT-UP ANIMATION
// ─────────────────────────────────────────
function animateCount(elementId, targetValue, suffix = "") {
  const el = document.getElementById(elementId);
  if (!el) return;

  const duration = 2000;       // 2 seconds
  const steps    = 60;
  const stepTime = duration / steps;
  let current    = 0;
  const increment = targetValue / steps;

  const timer = setInterval(() => {
    current += increment;
    if (current >= targetValue) {
      current = targetValue;
      clearInterval(timer);
    }
    el.textContent = Math.floor(current).toLocaleString("en-IN") + suffix;
  }, stepTime);
}

// Run count-up for static stats on load
window.addEventListener("load", () => {
  animateCount("stat-helped",   200000, "+");
  animateCount("stat-missions", 5);
  animateCount("stat-cities",   3);
  loadStats(); // also animates stat-volunteers from live API
});
