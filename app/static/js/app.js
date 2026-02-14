(() => {
  const unreadEl = document.getElementById("unread-count");
  const homeDot = document.getElementById("home-dot");
  const homeBtn = document.getElementById("home-btn");
  const notifyBtn = document.getElementById("notify-btn");
  const timeline = document.getElementById("timeline");

  const state = {
    unread: 0,
    lastSeen: timeline?.dataset.lastSeen || new Date().toISOString(),
    limit:
      new URLSearchParams(window.location.search).get("limit") ||
      homeBtn?.getAttribute("hx-get")?.match(/limit=(\d+)/)?.[1] ||
      "50",
    autoRefreshInFlight: false,
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

  const isHomeTimelineNearTop = () => {
    if (window.location.pathname !== "/AGENTS") return false;
    const activeTimeline = document.getElementById("timeline");
    if (!activeTimeline) return false;
    return activeTimeline.scrollTop <= 120;
  };

  const refreshTimelineFirstPage = () => {
    if (state.autoRefreshInFlight) return;
    state.autoRefreshInFlight = true;
    htmx.ajax(
      "GET",
      `/AGENTS/timeline?page=1&limit=${encodeURIComponent(state.limit)}`,
      { target: "#timeline", swap: "innerHTML" }
    );
  };

  const refreshLastSeen = () => {
    const meta = document.getElementById("timeline-meta");
    const activeTimeline = document.getElementById("timeline");
    if (meta?.dataset.lastSeen) {
      state.lastSeen = meta.dataset.lastSeen;
      if (activeTimeline) {
        activeTimeline.dataset.lastSeen = meta.dataset.lastSeen;
      }
    }
  };

  homeBtn?.addEventListener("click", () => {
    setUnread(0);
  });

  document.body.addEventListener("htmx:afterSwap", (event) => {
    const target = event.target;
    if (target?.id === "timeline") {
      setUnread(0);
      refreshLastSeen();
    } else if (target?.id === "page-content") {
      if (document.getElementById("timeline")) {
        setUnread(0);
        refreshLastSeen();
      }
    }
    state.autoRefreshInFlight = false;
  });

  document.body.addEventListener("htmx:responseError", () => {
    state.autoRefreshInFlight = false;
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
      if (isHomeTimelineNearTop()) {
        refreshTimelineFirstPage();
        setUnread(0);
        if (createdAt) {
          state.lastSeen = createdAt;
        }
      } else {
        markUnread(createdAt);
      }
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
        if (isHomeTimelineNearTop()) {
          refreshTimelineFirstPage();
          setUnread(0);
        } else {
          markUnread();
        }
      }
    } catch {
      // ignore network errors
    }
  };

  refreshLastSeen();
  startSSE();
  setInterval(pollForUpdates, 20000);
})();
