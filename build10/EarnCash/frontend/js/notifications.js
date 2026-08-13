/* ==========================================================
   EARNCASH NOTIFICATIONS
========================================================== */

const notificationsUser = checkLogin();

if (notificationsUser) {
  loadNotifications(notificationsUser.id);
}

async function loadNotifications(userId) {
  const container = document.getElementById("notificationList");
  const { ok, data } = await apiRequest(`/notifications/${userId}`);

  if (!ok) {
    container.innerHTML = "<p>Could not load notifications.</p>";
    return;
  }
  if (!data.length) {
    container.innerHTML = "<p>You're all caught up — no notifications yet.</p>";
    return;
  }

  container.innerHTML = data
    .map((n) => `
      <div class="transaction-row notification-row ${n.status === "unread" ? "unread" : ""}" data-id="${n.id}">
        <div>
          <strong>${escapeHtml(n.title)}</strong>
          <p class="tx-date">${escapeHtml(n.message)}</p>
          <span class="tx-date">${formatDate(n.created_at)}</span>
        </div>
        <div class="notification-actions">
          ${n.status === "unread" ? `<button data-action="read" data-id="${n.id}">Mark read</button>` : ""}
          <button data-action="delete" data-id="${n.id}">Delete</button>
        </div>
      </div>`)
    .join("");

  container.querySelectorAll("button[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => handleNotificationAction(btn.dataset.action, btn.dataset.id, userId));
  });
}

async function handleNotificationAction(action, id, userId) {
  if (action === "read") {
    await apiRequest(`/notifications/read/${id}`, { method: "PUT" });
  } else if (action === "delete") {
    await apiRequest(`/notifications/delete/${id}`, { method: "DELETE" });
  }
  loadNotifications(userId);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
