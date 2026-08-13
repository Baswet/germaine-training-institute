/* ==========================================================
   EARNCASH ADMIN PANEL
========================================================== */

/* ==========================================================
   ADMIN LOGIN
========================================================== */
const adminLoginForm = document.getElementById("adminLoginForm");

if (adminLoginForm) {
  adminLoginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("adminError");
    errorEl.style.display = "none";

    const payload = {
      email: document.getElementById("adminUsername").value.trim(),
      password: document.getElementById("adminPassword").value,
    };

    const submitBtn = adminLoginForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in...";

    const { ok, data } = await apiRequest("/admin/login", { method: "POST", body: payload, auth: false });

    submitBtn.disabled = false;
    submitBtn.textContent = "Login To Admin Panel";

    if (ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("currentUser", JSON.stringify(data.admin));
      window.location.href = "admin.html";
    } else {
      errorEl.textContent = data.error || "Invalid admin credentials.";
      errorEl.style.display = "block";
    }
  });
}

/* ==========================================================
   ADMIN SESSION GUARD
========================================================== */
function checkAdminLogin() {
  const token = localStorage.getItem("token");
  let user = null;
  try {
    user = JSON.parse(localStorage.getItem("currentUser") || "null");
  } catch (_) {}

  if (!token || !user || user.role !== "admin") {
    window.location.href = "admin-login.html";
    return null;
  }
  return user;
}

function adminLogout() {
  localStorage.removeItem("token");
  localStorage.removeItem("currentUser");
  window.location.href = "admin-login.html";
}

/* ==========================================================
   ADMIN DASHBOARD
========================================================== */
const adminUser = document.getElementById("usersTable") ? checkAdminLogin() : null;

if (adminUser) {
  loadAdminStats();
  loadUsers();
  loadPendingEnrollments();
  loadPendingWithdrawals();
}

async function loadAdminStats() {
  const { ok, data } = await apiRequest("/admin/stats");

  const totalUsersEl = document.getElementById("totalUsers");
  const totalEarningsEl = document.getElementById("totalEarnings");
  const totalWithdrawalsEl = document.getElementById("totalWithdrawals");

  if (!ok) {
    // A failed request must never leave the "0" placeholder in place —
    // that would look like a real, confirmed zero instead of a load failure.
    if (totalUsersEl) totalUsersEl.textContent = "—";
    if (totalEarningsEl) totalEarningsEl.textContent = "Unable to load";
    if (totalWithdrawalsEl) totalWithdrawalsEl.textContent = "—";
    return;
  }

  if (totalUsersEl) totalUsersEl.textContent = data.total_users ?? 0;
  if (totalEarningsEl) totalEarningsEl.textContent = formatKES(data.total_tuition_collected);
  if (totalWithdrawalsEl) totalWithdrawalsEl.textContent = data.pending_withdrawals ?? 0;
}

async function loadUsers() {
  const container = document.getElementById("usersTable");
  const { ok, data } = await apiRequest("/admin/users");

  if (!ok) {
    container.innerHTML = "<p>Could not load users.</p>";
    return;
  }
  if (!data.length) {
    container.innerHTML = "<p>No registered users yet.</p>";
    return;
  }

  container.innerHTML = data
    .map((u) => `
      <div class="user-row">
        <div>
          <strong>${escapeHtml(u.fullname)}</strong>
          <div style="opacity:.7; font-size:.85rem;">${escapeHtml(u.email)} · code ${escapeHtml(u.referral_code)}</div>
        </div>
        <span>${formatKES(u.wallet)}</span>
      </div>`)
    .join("");
}

/* ==========================================================
   TUITION PAYMENT VERIFICATION
   This is the only screen in the whole app that can trigger a
   referral commission — and only after real money is confirmed.
========================================================== */
async function loadPendingEnrollments() {
  const container = document.getElementById("enrollmentsTable");
  if (!container) return;

  const [unpaidRes, partialRes] = await Promise.all([
    apiRequest("/admin/enrollments?status=unpaid"),
    apiRequest("/admin/enrollments?status=partial"),
  ]);

  const enrollments = [...(unpaidRes.ok ? unpaidRes.data : []), ...(partialRes.ok ? partialRes.data : [])];

  if (!enrollments.length) {
    container.innerHTML = "<p>No enrollments awaiting payment right now.</p>";
    return;
  }

  container.innerHTML = enrollments
    .map((en) => `
      <div class="user-row" data-enrollment-id="${en.id}">
        <div>
          <strong>${escapeHtml(en.student_name)}</strong> — ${escapeHtml(en.course_name)}
          <div style="opacity:.7; font-size:.85rem;">
            Due ${formatKES(en.amount_due)} · Paid so far ${formatKES(en.amount_paid)}
            ${en.referred_by_name ? ` · Referred by ${escapeHtml(en.referred_by_name)}` : ""}
          </div>
        </div>
        <button class="btn" data-action="verify-payment" data-id="${en.id}" data-remaining="${(en.amount_due - en.amount_paid).toFixed(2)}">
          Verify Payment
        </button>
      </div>`)
    .join("");

  container.querySelectorAll('button[data-action="verify-payment"]').forEach((btn) => {
    btn.addEventListener("click", () => verifyPayment(btn.dataset.id, btn.dataset.remaining));
  });
}

async function verifyPayment(enrollmentId, remaining) {
  const input = prompt(
    `Enter the amount actually received for this student (KES). Remaining balance: KES ${remaining}`,
    remaining
  );
  if (input === null) return;

  const amount_paid = Number(input);
  if (!amount_paid || amount_paid <= 0) {
    alert("Please enter a valid amount.");
    return;
  }

  const { ok, data } = await apiRequest(`/admin/enrollments/${enrollmentId}/verify-payment`, {
    method: "PUT",
    body: { amount_paid },
  });

  if (ok) {
    let msg = `Payment recorded. Status: ${data.payment_status}.`;
    if (data.commission_created) {
      msg += ` A commission of ${formatKES(data.commission_amount)} was credited to the referrer's wallet.`;
    }
    alert(msg);
    loadPendingEnrollments();
    loadAdminStats();
  } else {
    alert(data.error || "Could not verify payment.");
  }
}

/* ==========================================================
   WITHDRAWAL MANAGEMENT
========================================================== */
async function loadPendingWithdrawals() {
  const container = document.getElementById("withdrawalRequests");
  if (!container) return;

  const { ok, data } = await apiRequest("/admin/withdrawals?status=pending");

  if (!ok) {
    container.innerHTML = "<p>Could not load withdrawal requests.</p>";
    return;
  }
  if (!data.length) {
    container.innerHTML = "<p>No pending requests.</p>";
    return;
  }

  container.innerHTML = data
    .map((w) => `
      <div class="withdraw-row" data-withdrawal-id="${w.id}">
        <div>
          <strong>${escapeHtml(w.fullname)}</strong> — ${formatKES(w.amount)} via ${methodLabel(w.method)}
          <div style="opacity:.7; font-size:.85rem;">${escapeHtml(w.account_details)}</div>
        </div>
        <div style="display:flex; gap:8px;">
          <button class="btn" data-action="approve" data-id="${w.id}">Approve</button>
          <button class="btn btn-outline" data-action="reject" data-id="${w.id}">Reject</button>
        </div>
      </div>`)
    .join("");

  container.querySelectorAll("button[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => handleWithdrawalAction(btn.dataset.action, btn.dataset.id));
  });
}

async function handleWithdrawalAction(action, id) {
  if (action === "approve") {
    const { ok, data } = await apiRequest(`/admin/withdrawals/${id}/approve`, { method: "PUT" });
    if (!ok) return alert(data.error || "Could not approve withdrawal.");
  } else if (action === "reject") {
    const reason = prompt("Reason for rejection (optional):", "");
    const { ok, data } = await apiRequest(`/admin/withdrawals/${id}/reject`, {
      method: "PUT",
      body: { reason },
    });
    if (!ok) return alert(data.error || "Could not reject withdrawal.");
  }
  loadPendingWithdrawals();
  loadAdminStats();
}

function methodLabel(method) {
  return { mpesa: "M-Pesa", bank: "Bank Transfer", airtel_money: "Airtel Money" }[method] || method;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
