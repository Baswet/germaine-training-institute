/* ==========================================================
   EARNCASH FRONTEND AUTH
   Handles register/login forms, session storage, and the
   "require login" guard used by every protected page.
========================================================== */

function showMessage(el, text) {
  if (!el) return;
  el.textContent = text;
  el.style.display = "block";
}

function hideMessage(el) {
  if (!el) return;
  el.style.display = "none";
}

function setButtonLoading(button, isLoading, loadingText, defaultText) {
  if (!button) return;
  button.disabled = isLoading;
  button.textContent = isLoading ? loadingText : defaultText;
}

/* ==========================================================
   PASSWORD VISIBILITY TOGGLES
========================================================== */
function wirePasswordToggle(iconId, inputId) {
  const icon = document.getElementById(iconId);
  const input = document.getElementById(inputId);
  if (!icon || !input) return;

  icon.addEventListener("click", () => {
    const showing = input.type === "text";
    input.type = showing ? "password" : "text";

    // Lucide replaces <i data-lucide> with an <svg>, so toggling the icon
    // means swapping the element back to an <i> with the new icon name and
    // re-running createIcons() — then re-binding since outerHTML replaces
    // the DOM node entirely.
    const nextIcon = showing ? "eye" : "eye-off";
    icon.outerHTML = `<i id="${iconId}" data-lucide="${nextIcon}"></i>`;
    if (window.lucide) lucide.createIcons();
    wirePasswordToggle(iconId, inputId);
  });
}
wirePasswordToggle("toggleLoginPassword", "loginPassword");
wirePasswordToggle("toggleRegisterPassword", "registerPassword");
wirePasswordToggle("toggleConfirmPassword", "confirmPassword");

/* ==========================================================
   REGISTER
========================================================== */
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  // Auto-fill referral code from a shared link like register.html?ref=EC4F92A1B7
  const params = new URLSearchParams(window.location.search);
  const refFromLink = params.get("ref");
  const refInput = document.getElementById("registerReferralCode");
  if (refFromLink && refInput) refInput.value = refFromLink.toUpperCase();

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("registerError");
    const successEl = document.getElementById("registerSuccess");
    hideMessage(errorEl);
    hideMessage(successEl);

    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
      showMessage(errorEl, "Passwords do not match.");
      return;
    }
    if (password.length < 8) {
      showMessage(errorEl, "Password must be at least 8 characters.");
      return;
    }

    const termsBox = document.getElementById("terms");
    if (termsBox && !termsBox.checked) {
      showMessage(errorEl, "Please accept the terms and conditions.");
      return;
    }

    const payload = {
      fullname: document.getElementById("registerName").value.trim(),
      email: document.getElementById("registerEmail").value.trim(),
      phone: document.getElementById("registerPhone").value.trim(),
      password,
      referral_code: (document.getElementById("registerReferralCode")?.value || "").trim(),
    };

    const submitBtn = registerForm.querySelector("button[type=submit]");
    setButtonLoading(submitBtn, true, "Creating account...", "Create Account");

    const { ok, data } = await apiRequest("/auth/register", { method: "POST", body: payload, auth: false });

    setButtonLoading(submitBtn, false, "Creating account...", "Create Account");

    if (ok) {
      showMessage(successEl, "Account created successfully! Redirecting to login...");
      setTimeout(() => (window.location.href = "login.html"), 1500);
    } else {
      showMessage(errorEl, data.error || "Registration failed. Please try again.");
    }
  });
}

/* ==========================================================
   LOGIN
========================================================== */
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("loginError");
    hideMessage(errorEl);

    const payload = {
      email: document.getElementById("loginEmail").value.trim(),
      password: document.getElementById("loginPassword").value,
    };

    const submitBtn = loginForm.querySelector("button[type=submit]");
    setButtonLoading(submitBtn, true, "Logging in...", "Login");

    const { ok, data } = await apiRequest("/auth/login", { method: "POST", body: payload, auth: false });

    setButtonLoading(submitBtn, false, "Logging in...", "Login");

    if (ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("currentUser", JSON.stringify(data.user));
      window.location.href = "dashboard.html";
    } else {
      showMessage(errorEl, data.error || "Invalid email or password.");
    }
  });
}

/* ==========================================================
   SESSION GUARD — call at the top of any protected page
========================================================== */
function checkLogin() {
  const token = localStorage.getItem("token");
  if (!token) {
    window.location.href = "login.html";
    return null;
  }
  try {
    return JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (_) {
    return null;
  }
}

function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (_) {
    return null;
  }
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("currentUser");
  window.location.href = "login.html";
}

// Wire up any element with [data-logout] on the page (nav buttons, etc.)
document.querySelectorAll("[data-logout]").forEach((el) => {
  el.addEventListener("click", (e) => {
    e.preventDefault();
    logout();
  });
});
