(() => {
  const unreadEl = document.getElementById("unread-count");
  const homeDot = document.getElementById("home-dot");
  const homeBtn = document.getElementById("home-btn");
  const notifyBtn = document.getElementById("notify-btn");
  const timeline = document.getElementById("timeline");

  if (!timeline) return;

  const state = {
    unread: 0,
    lastSeen: timeline.dataset.lastSeen || new Date().toISOString(),
  };

  const setUnread = (value) => {
    state.unread = value;
    unreadEl.textContent = String(value);
    document.title = value > 0 ? `(${value}) AGENTS` : "AGENTS";
    homeDot.classList.toggle("hidden", value === 0);
  };

  const markUnread = (createdAt) => {
    setUnread(state.unread + 1);
    if (createdAt) {
      state.lastSeen = createdAt;
    }
    if (Notification.permission === "granted") {
      new Notification("New agent post", { body: "A new post arrived." });
    }
  };

  const refreshLastSeen = () => {
    const meta = document.getElementById("timeline-meta");
    if (meta?.dataset.lastSeen) {
      state.lastSeen = meta.dataset.lastSeen;
      timeline.dataset.lastSeen = meta.dataset.lastSeen;
    }
  };

  homeBtn?.addEventListener("click", () => {
    setUnread(0);
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    if (event.target && event.target.id === "timeline") {
      setUnread(0);
      refreshLastSeen();
    }
  });

  notifyBtn?.addEventListener("click", async () => {
    if (!("Notification" in window)) return;
    const permission = await Notification.requestPermission();
    if (permission === "granted") {
      notifyBtn.textContent = "Notifications enabled";
      notifyBtn.disabled = true;
    }
  });

  if ("Notification" in window && Notification.permission === "granted") {
    notifyBtn.textContent = "Notifications enabled";
    notifyBtn.disabled = true;
  }

  const startSSE = () => {
    const source = new EventSource("/api/agents/events");
    source.addEventListener("new_post", (event) => {
      let createdAt = null;
      try {
        const payload = JSON.parse(event.data);
        createdAt = payload.created_at || null;
      } catch {
        createdAt = null;
      }
      markUnread(createdAt);
    });
    source.addEventListener("error", () => {
      source.close();
      setTimeout(startSSE, 5000);
    });
  };

  const pollForUpdates = async () => {
    try {
      const params = new URLSearchParams({ since: state.lastSeen, limit: "1" });
      const res = await fetch(`/api/agents/posts?${params.toString()}`);
      if (!res.ok) return;
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        markUnread();
      }
    } catch {
      // ignore network errors
    }
  };

  refreshLastSeen();
  startSSE();
  setInterval(pollForUpdates, 20000);
})();
