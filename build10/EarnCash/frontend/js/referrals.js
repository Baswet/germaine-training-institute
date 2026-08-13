/* ==========================================================
   EARNCASH REFERRALS
========================================================== */

const referralsUser = checkLogin();

if (referralsUser) {
  loadReferralData(referralsUser.id);
}

async function loadReferralData(userId) {
  const [statsRes, referredRes, commissionsRes] = await Promise.all([
    apiRequest(`/users/stats/${userId}`),
    apiRequest(`/referrals/${userId}`),
    apiRequest(`/referrals/${userId}/commissions`),
  ]);

  if (statsRes.ok) {
    const s = statsRes.data;
    document.getElementById("memberCount").textContent = s.total_referrals ?? 0;
    document.getElementById("refCommission").textContent = formatKES(s.total_commission_earned);

    const linkInput = document.getElementById("affiliateLink");
    if (linkInput && s.referral_code) {
      linkInput.value = `${window.location.origin}${window.location.pathname.replace("referrals.html", "register.html")}?ref=${s.referral_code}`;
    }
  } else {
    // Don't let a failed request masquerade as "you have 0 referrals."
    document.getElementById("memberCount").textContent = "—";
    document.getElementById("refCommission").textContent = "Unable to load";
    const linkInput = document.getElementById("affiliateLink");
    if (linkInput) linkInput.value = "Unable to load your referral link.";
  }

  renderMembers(referredRes.ok ? referredRes.data : [], commissionsRes.ok ? commissionsRes.data : []);
}

function renderMembers(referred, commissions) {
  const container = document.getElementById("membersList");
  if (!container) return;

  if (!referred.length) {
    container.innerHTML = "<p>You haven't referred anyone yet. Share your link above to get started!</p>";
    return;
  }

  const commissionedUserIds = new Set(commissions.map((c) => c.referred_user_id));

  container.innerHTML = referred
    .map((member) => {
      const hasCommission = commissionedUserIds.has(member.id);
      return `
        <div class="transaction-row">
          <div>
            <strong>${escapeHtml(member.fullname)}</strong>
            <span class="tx-date">Joined ${formatDate(member.created_at)}</span>
          </div>
          <span class="${hasCommission ? "status-approved" : "status-pending"}">
            ${hasCommission ? "Commission earned" : "Awaiting enrollment"}
          </span>
        </div>`;
    })
    .join("");
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

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
