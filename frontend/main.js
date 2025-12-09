const state = {
  loggedIn: false,
  user: null,
  balance: null,
  streak: null,
  nextClaimIn: null,
};

const logBox = document.getElementById("log-box");
const statusText = document.getElementById("status-text");
const loginBtn = document.getElementById("login-btn");
const userPill = document.getElementById("user-pill");
const userName = document.getElementById("user-name");
const userId = document.getElementById("user-id");
const userAvatar = document.getElementById("user-avatar");
const balanceAmount = document.getElementById("balance-amount");
const streakText = document.getElementById("streak-text");
const cooldownText = document.getElementById("cooldown-text");
const dailyBtn = document.getElementById("daily-btn");
const refreshBtn = document.getElementById("refresh-btn");
const healthBtn = document.getElementById("health-btn");

const API_BASE = "https://frontend-endu.onrender.com"; // set to your API origin

function setStatus(message) {
  statusText.textContent = message;
}

function log(message) {
  const now = new Date().toLocaleTimeString();
  logBox.textContent = `[${now}] ${message}\n` + logBox.textContent;
}

function updateUI() {
  if (state.loggedIn && state.user) {
    userPill.classList.remove("hidden");
    userName.textContent = state.user.username || "User";
    userId.textContent = "#" + String(state.user.id).slice(-4);
    const initials = (state.user.username || "DB").slice(0, 2).toUpperCase();
    userAvatar.textContent = initials;
    loginBtn.classList.add("hidden");
  } else {
    userPill.classList.add("hidden");
    loginBtn.classList.remove("hidden");
  }

  balanceAmount.textContent = state.balance !== null ? `${state.balance} dbx` : "--";
  streakText.textContent = `Streak: ${state.streak ?? "--"}`;
  if (state.nextClaimIn) {
    const mins = Math.ceil(state.nextClaimIn / 60);
    cooldownText.textContent = `Next daily in ~${mins} min`;
    dailyBtn.disabled = true;
    dailyBtn.classList.add("disabled");
  } else {
    cooldownText.textContent = "";
    dailyBtn.disabled = false;
    dailyBtn.classList.remove("disabled");
  }
}

async function mockLogin() {
  // In production, redirect to the Discord OAuth URL returned by /auth/discord-url
  state.loggedIn = true;
  state.user = { id: 123456, username: "DemoUser" };
  log("Mock login complete. Replace this with Discord OAuth redirect/return handling.");
  await mockFetchBalance();
}

async function mockFetchBalance() {
  // Replace with GET /me once wired to the API
  state.balance = 750;
  state.streak = 3;
  state.nextClaimIn = null;
  updateUI();
}

async function mockClaimDaily() {
  // Replace with POST /economy/daily
  const now = Date.now();
  const lastClaim = localStorage.getItem("demo_last_claim");
  if (lastClaim && now - Number(lastClaim) < 24 * 60 * 60 * 1000) {
    const remaining = 24 * 60 * 60 * 1000 - (now - Number(lastClaim));
    state.nextClaimIn = Math.ceil(remaining / 1000);
    log("Daily already claimed. Cooldown active.");
    updateUI();
    return;
  }
  localStorage.setItem("demo_last_claim", String(now));
  state.balance = (state.balance || 0) + 100;
  state.streak = (state.streak || 0) + 1;
  state.nextClaimIn = 24 * 60 * 60;
  log("Daily claimed (demo).");
  updateUI();
}

async function pingHealth() {
  if (!API_BASE) {
    setStatus("Set API_BASE to test live health.");
    log("API_BASE not set. Using demo-only mode.");
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    setStatus(data.status === "ok" ? "API online" : "API issue");
    log(`Health: ${JSON.stringify(data)}`);
  } catch (err) {
    setStatus("API unreachable");
    log(`Health check failed: ${err}`);
  }
}

loginBtn.addEventListener("click", mockLogin);
refreshBtn.addEventListener("click", mockFetchBalance);
dailyBtn.addEventListener("click", mockClaimDaily);
healthBtn.addEventListener("click", pingHealth);

updateUI();
log("Demo mode active. Wire API_BASE and replace mock* calls to integrate.");
