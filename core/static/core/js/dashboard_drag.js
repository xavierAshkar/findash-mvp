function initSortable() {
  const widgetGrid = document.getElementById("widget-grid");
  if (!widgetGrid) return;

  // Prevent duplicate init (in case HTMX swaps again)
  if (widgetGrid.dataset.sortableInit === "true") return;

  Sortable.create(widgetGrid, {
    animation: 150,
    handle: ".dashboard-widget",
    ghostClass: "opacity-40",
    onEnd: function () {
      const newOrder = Array.from(widgetGrid.children).map((el, index) => ({
        widget_type: el.getAttribute("data-widget-id"),
        position: index,
      }));

      console.log("Saving new order:", newOrder);

      fetch("/dashboard/save-widget-order/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({ order: newOrder }),
      });
    },
  });

  widgetGrid.dataset.sortableInit = "true";
}

// CSRF helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Call on first load
initSortable();

// Re-init on HTMX widget grid replacement
document.body.addEventListener("htmx:afterSwap", (e) => {
  if (e.detail.target.id === "widget-grid") {
    initSortable();
  }
});
