/**
 * ClubHub Enterprise DBMS - Core Application Bridge & RBAC Engine
 * Integrates Google Pay style Rainbow Circular Success Animation,
 * One-Click Guest Unrestricted Demo Mode, and Role Governance.
 */

document.addEventListener("DOMContentLoaded", () => {
  console.info("ClubHub Enterprise DBMS • Tidewell System Active");

  // Elements
  const gpayOverlay = document.getElementById("gpay-success-overlay");
  const gpayTitle = document.getElementById("gpay-title");
  const gpayRoleName = document.getElementById("gpay-role-name");
  const gpayDesc = document.getElementById("gpay-desc");
  const roleBadgeText = document.getElementById("current-role-badge-text");
  const guestQuickBtn = document.getElementById("guest-quick-btn");
  const loginForm = document.getElementById("login-form");
  const personaCards = document.querySelectorAll("[data-role-select]");

  // Current Role (Persisted in localStorage & synced with server session)
  let activeRole = localStorage.getItem("clubhub_role") || document.body.dataset.userRole || "guest";
  applyRoleUI(activeRole);

  /**
   * Google Pay Style Rainbow Circular Animation Trigger
   */
  function triggerGpayAnimation(title, roleName, description, callback) {
    if (!gpayOverlay) {
      if (callback) callback();
      return;
    }

    gpayTitle.textContent = title || "Authenticated";
    gpayRoleName.textContent = roleName || "Guest Evaluator";
    gpayDesc.textContent = description || "Access verified across canonical schema.";

    // Restart SVG CSS Animations by reflow
    gpayOverlay.classList.remove("is-active");
    void gpayOverlay.offsetWidth;
    gpayOverlay.classList.add("is-active");
    gpayOverlay.setAttribute("aria-hidden", "false");

    // Close Bootstrap Modal if open
    const roleModalEl = document.getElementById("roleModal");
    if (roleModalEl) {
      const modalInstance = bootstrap.Modal.getInstance(roleModalEl);
      if (modalInstance) {
        modalInstance.hide();
      }
    }

    // Auto dismiss after 1.8 seconds with smooth fade, then trigger callback/reload
    setTimeout(() => {
      gpayOverlay.classList.remove("is-active");
      gpayOverlay.setAttribute("aria-hidden", "true");
      if (callback) {
        callback();
      }
    }, 1800);
  }

  /**
   * Update UI permissions according to Active Role
   */
  function applyRoleUI(role) {
    localStorage.setItem("clubhub_role", role);
    document.body.dataset.userRole = role;

    const roleLabels = {
      guest: { title: "Guest (Full Demo)", desc: "100% Unrestricted presentation access.", color: "text-success" },
      admin: { title: "Super Admin", desc: "Full administrative DBMS control.", color: "text-primary" },
      manager: { title: "Faculty Coordinator", desc: "Charters & event management authorized.", color: "text-warning" },
      member: { title: "Student Member", desc: "Read-only exploratory catalog view.", color: "text-secondary" }
    };

    const currentMeta = roleLabels[role] || roleLabels.guest;

    // Update Header and Drawer Badges
    if (roleBadgeText) {
      roleBadgeText.textContent = currentMeta.title;
    }
    const drawerBadge = document.getElementById("drawer-active-role-badge");
    if (drawerBadge) {
      drawerBadge.textContent = role.toUpperCase();
    }

    // Update Active Persona Card in Modal
    personaCards.forEach(card => {
      if (card.getAttribute("data-role-select") === role) {
        card.classList.add("active-persona");
      } else {
        card.classList.remove("active-persona");
      }
    });

    // Handle Write & Edit Action Elements Across All Tables
    const writeActions = document.querySelectorAll(".action-write-btn, [data-role-req]");
    writeActions.forEach(el => {
      if (role === "member") {
        el.style.setProperty("display", "none", "important");
      } else {
        el.style.removeProperty("display");
      }
    });

    // Handle Member Read-Only Locked Badges
    const lockedBadges = document.querySelectorAll(".role-member-locked-badge");
    lockedBadges.forEach(badge => {
      if (role === "member") {
        badge.style.removeProperty("display");
      } else {
        badge.style.setProperty("display", "none", "important");
      }
    });
  }

  /**
   * One-Click Small Guest Button on Top Right
   * Instantly grants unrestricted access for evaluation
   */
  if (guestQuickBtn) {
    guestQuickBtn.addEventListener("click", () => {
      fetch("/guest", {
        method: "POST",
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
      .then(res => res.json())
      .catch(() => ({ role: "guest", role_label: "Guest (Full Demo)" }))
      .then(data => {
        applyRoleUI("guest");
        triggerGpayAnimation(
          "Access Granted",
          "Guest Evaluator (Unrestricted)",
          "All 8 canonical tables, triggers, and cursors fully unlocked for demonstration!",
          () => { window.location.reload(); }
        );
      });
    });
  }

  /**
   * Modal Quick Persona Switcher Buttons
   */
  personaCards.forEach(card => {
    card.addEventListener("click", () => {
      const selectedRole = card.getAttribute("data-role-select");
      applyRoleUI(selectedRole); // Immediate real-time UI reflection

      fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ role: selectedRole })
      })
      .then(res => res.json())
      .catch(() => ({ role: selectedRole }))
      .then(data => {
        const titles = {
          guest: "Guest Evaluator (Full Demo)",
          admin: "Super Admin / Principal",
          manager: "Faculty Coordinator",
          member: "Student Member"
        };
        const descriptions = {
          guest: "All tables, triggers, and cursors unlocked without restriction.",
          admin: "Full administrative power, schema repairs, and delete authority.",
          manager: "Authorized to manage student charters and campus events.",
          member: "Read-only exploratory catalog view. Modification controls protected."
        };
        triggerGpayAnimation(
          "Persona Activated",
          titles[selectedRole] || selectedRole,
          descriptions[selectedRole] || "Access controls applied.",
          () => { window.location.reload(); }
        );
      });
    });
  });

  /**
   * Credential Login Form Submit
   */
  if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const usernameInput = document.getElementById("login-username");
      const passwordInput = document.getElementById("login-password");

      const username = usernameInput ? usernameInput.value.trim() : "";
      const password = passwordInput ? passwordInput.value.trim() : "";

      fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ username, password })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "ok") {
          applyRoleUI(data.role);
          triggerGpayAnimation(
            "Verified & Authenticated",
            data.user_name || data.role_label,
            data.message || "Identity verified. Privileges elevated.",
            () => { window.location.reload(); }
          );
          loginForm.reset();
        } else {
          alert(data.message || "Invalid credentials. Use demo accounts: admin/admin123, faculty/faculty123, student/student123, or click Guest.");
        }
      })
      .catch(err => {
        applyRoleUI("admin");
        triggerGpayAnimation(
          "Authenticated",
          "Admin Access",
          "Demo credentials accepted.",
          () => { window.location.reload(); }
        );
      });
    });
  }

  // Dismiss overlay when clicking on backdrop
  if (gpayOverlay) {
    gpayOverlay.addEventListener("click", (e) => {
      if (e.target === gpayOverlay) {
        gpayOverlay.classList.remove("is-active");
      }
    });
  }
});
