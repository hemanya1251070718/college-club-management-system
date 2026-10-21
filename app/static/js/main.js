// Delete confirmation handler
document.addEventListener("DOMContentLoaded", () => {
  const deleteForms = document.querySelectorAll("form.delete-form");
  deleteForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const entity = form.dataset.entity || "record";
      if (!confirm(`Are you sure you want to delete this ${entity}? This action is irreversible.`)) {
        e.preventDefault();
      }
    });
  });

  // Auto-dismiss alerts after 6 seconds
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 6000);
  });
});
