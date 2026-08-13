/* ==========================================================
   EARNCASH DASHBOARD
========================================================== */

const dashboardUser = checkLogin();

if (dashboardUser) {
  document.getElementById("userName").textContent = dashboardUser.name || "User";
  document.getElementById("userEmail").textContent = dashboardUser.email || "";
  loadDashboard(dashboardUser.id);
}

async function loadDashboard(userId) {
  const [statsRes, txRes] = await Promise.all([
    apiRequest(`/users/stats/${userId}`),
    apiRequest(`/users/transactions/${userId}`),
  ]);

  if (statsRes.ok) {
    const s = statsRes.data;
    document.getElementById("totalEarnings").textContent = formatKES(s.wallet_balance);
    document.getElementById("totalReferrals").textContent = s.total_referrals ?? 0;
    document.getElementById("totalCommission").textContent = formatKES(s.total_commission_earned);
    document.getElementById("walletBalance").textContent = Number(s.wallet_balance || 0).toLocaleString("en-KE", { minimumFractionDigits: 2 });

    const linkInput = document.getElementById("affiliateLink");
    if (linkInput && s.referral_code) {
      linkInput.value = `${window.location.origin}${window.location.pathname.replace("dashboard.html", "register.html")}?ref=${s.referral_code}`;
    }

    // Separate, additive link: refers a visitor straight to the real GTI
    // Explore Programmes hub with the same real referral code attached.
    // If that visitor later applies to and pays tuition for an AI
    // Bootcamp programme, the admin-confirmed commission flow (see
    // germaine-backend/app/services/admin_service.confirm_application_tuition)
    // credits this same wallet — never anything invented client-side.
    const gtiLinkInput = document.getElementById("gtiReferralLink");
    if (gtiLinkInput && s.referral_code) {
      gtiLinkInput.value = `${CONFIG.GTI_SITE_URL}ai-bootcamp-courses.html?ref=${s.referral_code}`;
    }
  } else {
    console.error("Failed to load stats:", statsRes.data.error);
    // A failed request must never be shown as if the real value were zero —
    // that would misrepresent an outage as "you have earned nothing."
    ["totalEarnings", "totalCommission"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = "Unable to load";
    });
    const referralsEl = document.getElementById("totalReferrals");
    if (referralsEl) referralsEl.textContent = "—";
    const walletEl = document.getElementById("walletBalance");
    if (walletEl) walletEl.textContent = "—";
    const linkInput = document.getElementById("affiliateLink");
    if (linkInput) linkInput.value = "Unable to load your referral link.";
  }

  if (txRes.ok) {
    renderTransactions(txRes.data);
    renderEarningsChart(txRes.data);
  }
}

function renderTransactions(transactions) {
  const container = document.getElementById("transactionList");
  if (!container) return;

  if (!transactions.length) {
    container.innerHTML = "<p>No transactions yet. Share your referral link to start earning!</p>";
    return;
  }

  container.innerHTML = transactions
    .slice(0, 10)
    .map((tx) => {
      const isPositive = Number(tx.amount) >= 0;
      return `
        <div class="transaction-row">
          <div>
            <strong>${escapeHtml(tx.description || tx.type)}</strong>
            <span class="tx-date">${formatDate(tx.created_at)}</span>
          </div>
          <span class="tx-amount ${isPositive ? "positive" : "negative"}">
            ${isPositive ? "+" : ""}${formatKES(tx.amount)}
          </span>
        </div>`;
    })
    .join("");
}

function renderEarningsChart(transactions) {
  const canvas = document.getElementById("earningsChart");
  if (!canvas || typeof Chart === "undefined") return;

  // Build a running wallet balance over time from the transaction ledger.
  const sorted = [...transactions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  let running = 0;
  const labels = [];
  const values = [];
  sorted.forEach((tx) => {
    running += Number(tx.amount);
    labels.push(formatDate(tx.created_at));
    values.push(running.toFixed(2));
  });

  new Chart(canvas, {
    type: "line",
    data: {
      labels: labels.length ? labels : ["Today"],
      datasets: [{
        label: "Wallet Balance (KES)",
        data: values.length ? values : [0],
        borderColor: "#ff4f9d",
        backgroundColor: "rgba(255,79,157,0.15)",
        tension: 0.35,
        fill: true,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true } },
    },
  });
}

function copyReferralLink() {
  const input = document.getElementById("affiliateLink");
  if (!input) return;
  input.select();
  navigator.clipboard.writeText(input.value).then(() => {
    const original = input.value;
    input.value = "Copied!";
    setTimeout(() => (input.value = original), 1200);
  });
}

function copyGtiReferralLink() {
  const input = document.getElementById("gtiReferralLink");
  if (!input) return;
  input.select();
  navigator.clipboard.writeText(input.value).then(() => {
    const original = input.value;
    input.value = "Copied!";
    setTimeout(() => (input.value = original), 1200);
  });
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
