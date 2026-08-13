/* ==========================================================
   EARNCASH WITHDRAWALS
========================================================== */

const withdrawUser = checkLogin();

if (withdrawUser) {
  loadWalletBalance(withdrawUser.id);
  loadWithdrawHistory(withdrawUser.id);
}

async function loadWalletBalance(userId) {
  const { ok, data } = await apiRequest(`/users/stats/${userId}`);
  if (ok) {
    document.getElementById("withdrawBalance").textContent =
      Number(data.wallet_balance || 0).toLocaleString("en-KE", { minimumFractionDigits: 2 });
  } else {
    // A failed balance request must never render as "0.00" — that would
    // look like a real, confirmed zero balance instead of a technical error.
    document.getElementById("withdrawBalance").textContent = "—";
  }
}

async function loadWithdrawHistory(userId) {
  const container = document.getElementById("withdrawHistory");
  const { ok, data } = await apiRequest(`/withdrawals/history/${userId}`);

  if (!ok) {
    container.innerHTML = "<p>Could not load withdrawal history.</p>";
    return;
  }
  if (!data.length) {
    container.innerHTML = "<p>You haven't requested any withdrawals yet.</p>";
    return;
  }

  const statusClass = { pending: "status-pending", approved: "status-approved", rejected: "status-rejected" };

  container.innerHTML = data
    .map((w) => `
      <div class="transaction-row">
        <div>
          <strong>${formatKES(w.amount)} via ${methodLabel(w.method)}</strong>
          <span class="tx-date">${formatDate(w.created_at)}</span>
        </div>
        <span class="${statusClass[w.status] || ""}">${capitalize(w.status)}</span>
      </div>`)
    .join("");
}

function methodLabel(method) {
  return { mpesa: "M-Pesa", bank: "Bank Transfer", airtel_money: "Airtel Money" }[method] || method;
}

function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

const withdrawForm = document.getElementById("withdrawForm");

if (withdrawForm) {
  withdrawForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      amount: Number(document.getElementById("withdrawAmount").value),
      method: document.getElementById("withdrawMethod").value,
      details: document.getElementById("withdrawDetails").value.trim(),
    };

    if (!payload.amount || payload.amount <= 0) {
      alert("Please enter a valid amount.");
      return;
    }
    if (!payload.method) {
      alert("Please select a payment method.");
      return;
    }

    const submitBtn = withdrawForm.querySelector("button[type=submit]");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    const { ok, data } = await apiRequest("/withdrawals/request", { method: "POST", body: payload });

    submitBtn.disabled = false;
    submitBtn.textContent = "Submit Withdrawal";

    if (ok) {
      alert("Withdrawal request submitted! It's now pending admin approval.");
      withdrawForm.reset();
      loadWalletBalance(withdrawUser.id);
      loadWithdrawHistory(withdrawUser.id);
    } else {
      alert(data.error || "Could not submit withdrawal request.");
    }
  });
}
