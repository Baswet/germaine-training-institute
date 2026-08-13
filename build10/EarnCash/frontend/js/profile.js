/* ==========================================================
   EARNCASH PROFILE
========================================================== */

const profileUser = checkLogin();

if (profileUser) {
  document.getElementById("profileName").textContent = profileUser.name || "User";
  document.getElementById("profileEmail").textContent = profileUser.email || "";
  loadProfile(profileUser.id);
  applyDarkModePreference();
}

async function loadProfile(userId) {
  const { ok, data } = await apiRequest(`/users/profile/${userId}`);
  if (!ok) return;

  document.getElementById("editName").value = data.fullname || "";
  document.getElementById("editPhone").value = data.phone || "";
}

/* ==========================================================
   UPDATE PROFILE
========================================================== */
const profileForm = document.getElementById("profileForm");

if (profileForm) {
  profileForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const messageEl = document.getElementById("profileMessage");
    const submitBtn = profileForm.querySelector("button[type=submit]");

    const payload = {
      fullname: document.getElementById("editName").value.trim(),
      phone: document.getElementById("editPhone").value.trim(),
    };

    setButtonLoading(submitBtn, true, "Saving...", "Save Changes");

    const { ok, data } = await apiRequest(`/users/profile/${profileUser.id}`, {
      method: "PUT",
      body: payload,
    });

    setButtonLoading(submitBtn, false, "Saving...", "Save Changes");

    showProfileMessage(messageEl, ok, data);

    if (ok) {
      // Keep localStorage in sync so the name shown elsewhere stays accurate
      const updatedUser = { ...profileUser, name: payload.fullname };
      localStorage.setItem("currentUser", JSON.stringify(updatedUser));
      document.getElementById("profileName").textContent = payload.fullname;
    }
  });
}

/* ==========================================================
   CHANGE PASSWORD
========================================================== */
const passwordForm = document.getElementById("passwordForm");

if (passwordForm) {
  passwordForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const messageEl = document.getElementById("profileMessage");
    const submitBtn = passwordForm.querySelector("button[type=submit]");

    const payload = {
      current_password: document.getElementById("currentPassword").value,
      new_password: document.getElementById("newPassword").value,
    };

    setButtonLoading(submitBtn, true, "Updating...", "Change Password");

    const { ok, data } = await apiRequest(`/users/password/${profileUser.id}`, {
      method: "PUT",
      body: payload,
    });

    setButtonLoading(submitBtn, false, "Updating...", "Change Password");

    showProfileMessage(messageEl, ok, data);
    if (ok) passwordForm.reset();
  });
}

function showProfileMessage(el, ok, data) {
  if (!el) return;
  el.textContent = ok ? (data.message || "Saved successfully.") : (data.error || "Something went wrong.");
  el.style.display = "block";
  el.style.color = ok ? "green" : "#d93686";
  setTimeout(() => (el.style.display = "none"), 4000);
}

/* ==========================================================
   DARK MODE (client-side only, saved to localStorage)
========================================================== */
function applyDarkModePreference() {
  const toggle = document.getElementById("darkModeToggle");
  const enabled = localStorage.getItem("darkMode") === "true";

  if (enabled) document.body.classList.add("dark-mode");
  if (toggle) toggle.checked = enabled;

  if (toggle) {
    toggle.addEventListener("change", () => {
      document.body.classList.toggle("dark-mode", toggle.checked);
      localStorage.setItem("darkMode", toggle.checked);
    });
  }
}
