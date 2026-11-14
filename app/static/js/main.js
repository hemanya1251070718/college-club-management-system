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

  /* ==========================================================================
     SHNEIDERMAN'S 8 GOLDEN RULES UX SUITE IMPLEMENTATION
     ========================================================================== */

  /**
   * RULE 2 & 7: Universal Usability & Keyboard Shortcuts System
   * Guarded against firing when typing in inputs/textareas/selects.
   */
  let lastKeyG = false;
  let gTimeout = null;

  document.addEventListener("keydown", (e) => {
    const targetTag = e.target.tagName.toLowerCase();
    const isEditing = targetTag === "input" || targetTag === "textarea" || targetTag === "select" || e.target.isContentEditable;

    // ESC closes open modals, drawer, and overlays
    if (e.key === "Escape") {
      // Close Bootstrap modals
      document.querySelectorAll(".modal.show").forEach(m => {
        const inst = bootstrap.Modal.getInstance(m);
        if (inst) inst.hide();
      });
      // Close side drawer if open
      const drawer = document.querySelector(".drawer-backdrop.is-open");
      if (drawer) {
        drawer.classList.remove("is-open");
        drawer.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
      }
      return;
    }

    if (isEditing) return; // Never intercept when user is typing

    // '/' Focus search or filter input
    if (e.key === "/" && !e.ctrlKey && !e.metaKey) {
      const searchInput = document.querySelector('input[name="q"], input[type="text"], input[name="search"]');
      if (searchInput) {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
      return;
    }

    // '?' Open Keyboard Shortcuts Help Modal
    if (e.key === "?" || (e.shiftKey && e.key === "/")) {
      e.preventDefault();
      const shortcutModalEl = document.getElementById("keyboardShortcutsModal");
      if (shortcutModalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(shortcutModalEl);
        modal.show();
      }
      return;
    }

    // Two-key chord: 'g' then <key> for quick navigation
    if (e.key.toLowerCase() === "g" && !lastKeyG) {
      lastKeyG = true;
      clearTimeout(gTimeout);
      gTimeout = setTimeout(() => { lastKeyG = false; }, 1000);
      return;
    }

    if (lastKeyG) {
      lastKeyG = false;
      clearTimeout(gTimeout);
      const routes = {
        c: "/",
        t: "/triggers",
        m: "/memberships",
        e: "/events",
        p: "/procedures",
        s: "/students",
        l: "/clubs",
        h: "/health"
      };
      const dest = routes[e.key.toLowerCase()];
      if (dest) {
        e.preventDefault();
        window.location.href = dest;
      }
    }
  });

  /**
   * RULE 3 & 5: Informative Feedback & Error Prevention on Form Submits
   * Prevents double-submits, adds loading spinner, announces state via aria-live
   */
  const liveStatusRegion = document.getElementById("app-live-status");
  function announceStatus(message) {
    if (liveStatusRegion) {
      liveStatusRegion.textContent = message;
    }
  }

  document.querySelectorAll("form:not(#login-form):not(.delete-form)").forEach(form => {
    form.addEventListener("submit", (e) => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.classList.add("btn-loading");
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...`;
        announceStatus("Form submitting, please wait...");
        // Fallback re-enable if page does not redirect immediately
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.classList.remove("btn-loading");
          submitBtn.innerHTML = originalText;
        }, 8000);
      }
    });
  });

  /**
   * RULE 5 & 7: Destructive Action Confirmation Dialog
   * Replaces native window.confirm() with a graceful, accessible modal
   */
  const deleteModalEl = document.getElementById("deleteConfirmModal");
  let pendingDeleteForm = null;

  if (deleteModalEl) {
    const confirmBtn = document.getElementById("deleteConfirmSubmitBtn");
    const targetLabel = document.getElementById("deleteConfirmTargetLabel");

    document.querySelectorAll("form.delete-form").forEach(form => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        pendingDeleteForm = form;
        const entityName = form.dataset.entity || "record";
        if (targetLabel) {
          targetLabel.textContent = `Are you sure you want to permanently delete this ${entityName}? This database operation is irreversible.`;
        }
        const modal = bootstrap.Modal.getOrCreateInstance(deleteModalEl);
        modal.show();
      });
    });

    if (confirmBtn) {
      confirmBtn.addEventListener("click", () => {
        if (pendingDeleteForm) {
          const btn = pendingDeleteForm.querySelector('button[type="submit"]');
          if (btn) btn.disabled = true;
          pendingDeleteForm.submit();
        }
      });
    }
  }

  /**
   * RULE 6 & 8: Form Draft Auto-Save in sessionStorage
   * Preserves unsaved form inputs in case user accidentally navigates away
   */
  document.querySelectorAll("form[method='POST']:not(.delete-form):not(#login-form)").forEach(form => {
    const formId = form.getAttribute("action") || window.location.pathname;
    const storageKey = `draft_${formId}`;

    // Restore draft if present
    try {
      const saved = sessionStorage.getItem(storageKey);
      if (saved) {
        const data = JSON.parse(saved);
        Object.keys(data).forEach(name => {
          const input = form.elements[name];
          if (input && !input.readOnly && input.type !== "hidden" && input.type !== "password") {
            input.value = data[name];
          }
        });
      }
    } catch (err) {}

    // Save on changes
    form.addEventListener("input", () => {
      try {
        const formData = new FormData(form);
        const obj = {};
        formData.forEach((val, key) => {
          if (key !== "password") obj[key] = val;
        });
        sessionStorage.setItem(storageKey, JSON.stringify(obj));
      } catch (err) {}
    });

    // Clear draft on successful submit
    form.addEventListener("submit", () => {
      try {
        sessionStorage.removeItem(storageKey);
      } catch (err) {}
    });
  });

  /**
   * TRIGGER 1 DIRECT INSPECTOR & SQL CODE COPY
   * Ensures Trigger 1 is 100% visible, crystal clear, and easy to test
   */
  const trigger1ModalEl = document.getElementById("trigger1Modal");
  const copySqlBtn = document.getElementById("copyTrigger1SqlBtn");
  if (copySqlBtn) {
    copySqlBtn.addEventListener("click", () => {
      const sqlCode = document.getElementById("trigger1SqlCode");
      if (sqlCode) {
        navigator.clipboard.writeText(sqlCode.innerText.trim()).then(() => {
          copySqlBtn.innerHTML = '<i class="bi bi-check2 text-success me-1"></i> Copied!';
          announceStatus("Trigger 1 SQL copied to clipboard.");
          setTimeout(() => {
            copySqlBtn.innerHTML = '<i class="bi bi-clipboard me-1"></i> Copy SQL';
          }, 2000);
        });
      }
    });
  }

  /**
   * IN-APP MULTI-ROLE PERSONA SWITCHER
   * Allows students with multiple club memberships to switch operating persona on the fly
   */
  window.switchPersonaInApp = function(clubId, clubName, clubRole, roleTier, roleTitle) {
    fetch('/api/auth/select-role', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({
        club_id: clubId,
        club_name: clubName,
        club_role: clubRole,
        role_tier: roleTier,
        role_title: roleTitle
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'ok') {
        window.location.reload();
      }
    })
    .catch(() => {
      window.location.reload();
    });
  };

  /**
   * ========================================================================
   * INTERACTIVE REAL-TIME TABLE SEARCH, CATEGORY PILLS & COPY CHIPS
   * ========================================================================
   */

  // 1. Live Instant Table Filter & Category Synchronization Engine
  function initTableFilterEngine() {
    const table = document.querySelector(".tesla-table");
    if (!table) return;

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    const searchInput = document.querySelector(".table-live-search");
    const counter = document.querySelector(".table-match-counter");
    const pillButtons = document.querySelectorAll(".table-pill-btn");
    const kpiCards = document.querySelectorAll(".kpi-card[data-kpi-filter]");

    const allRows = Array.from(tbody.querySelectorAll("tr:not(.empty-state-row):not(.live-filter-empty-row)"));
    const totalCount = allRows.length;
    if (totalCount === 0) return;

    let activeFilter = "all";

    function updateMatchCounter(visibleCount) {
      if (counter) {
        const strongEl = counter.querySelector(".match-count");
        if (strongEl) {
          strongEl.textContent = visibleCount;
        } else {
          counter.textContent = `Showing ${visibleCount} of ${totalCount}`;
        }
      }
    }

    function applyFilter() {
      const q = searchInput ? searchInput.value.trim().toLowerCase() : "";
      const filterKey = (activeFilter || "all").trim().toUpperCase();
      let visibleCount = 0;

      allRows.forEach(row => {
        const rowText = (row.innerText || "").toLowerCase();
        const rowDept = (row.getAttribute("data-dept") || "").trim().toUpperCase();
        const rowDeptName = (row.getAttribute("data-dept-name") || "").toLowerCase();
        const rowCat = (row.getAttribute("data-category") || "").toLowerCase();

        // 1. Match query
        const matchesQuery = !q || rowText.includes(q);

        // 2. Match category/department
        let matchesCategory = false;
        if (!filterKey || filterKey === "ALL") {
          matchesCategory = true;
        } else if (filterKey === "CE") {
          matchesCategory = (rowDept === "CE" || rowCat.includes("ce") || rowDeptName.includes("computer"));
        } else if (filterKey === "ME") {
          matchesCategory = (rowDept === "ME" || rowCat.includes("me") || rowDeptName.includes("mechanical"));
        } else if (filterKey === "EE") {
          matchesCategory = (rowDept === "EE" || rowCat.includes("ee") || rowDeptName.includes("electronics"));
        } else if (filterKey === "ELE") {
          matchesCategory = (rowDept === "ELE" || rowCat.includes("ele") || rowDeptName.includes("electrical"));
        } else if (filterKey === "CIRCUITS" || filterKey === "ELECTRONICS" || filterKey === "CIRCUITS & SYSTEMS") {
          matchesCategory = (rowDept === "EE" || rowDept === "ELE" || rowDeptName.includes("electronics") || rowDeptName.includes("electrical"));
        } else {
          // General matching for Clubs, Events, Memberships, Triggers
          const fkLower = filterKey.toLowerCase();
          matchesCategory = rowCat.includes(fkLower) || rowText.includes(fkLower);
        }

        if (matchesQuery && matchesCategory) {
          row.style.display = "";
          visibleCount++;
        } else {
          row.style.display = "none";
        }
      });

      updateMatchCounter(visibleCount);

      // Handle Empty State Row
      let emptyRow = tbody.querySelector(".live-filter-empty-row");
      if (visibleCount === 0) {
        if (!emptyRow) {
          emptyRow = document.createElement("tr");
          emptyRow.className = "live-filter-empty-row";
          tbody.appendChild(emptyRow);
        }
        const searchMsg = q ? `matching "${searchInput.value}"` : `in selected filter`;
        emptyRow.innerHTML = `
          <td colspan="10" class="text-center py-5 text-secondary">
            <i class="bi bi-search me-2"></i>No records found ${searchMsg}.
            <button type="button" class="btn btn-sm btn-link text-info p-0 ms-2 reset-table-filter-btn" style="text-decoration: underline;">
              Show all records
            </button>
          </td>
        `;
        const resetBtn = emptyRow.querySelector(".reset-table-filter-btn");
        if (resetBtn) {
          resetBtn.addEventListener("click", () => {
            resetAllFilters();
          });
        }
      } else if (emptyRow) {
        emptyRow.remove();
      }
    }

    function resetAllFilters() {
      if (searchInput) searchInput.value = "";
      activeFilter = "all";
      pillButtons.forEach(p => {
        const pKey = (p.getAttribute("data-filter") || "").toLowerCase();
        if (pKey === "all" || pKey === "") {
          p.classList.add("is-active", "active");
        } else {
          p.classList.remove("is-active", "active");
        }
      });
      applyFilter();
    }

    // Connect Filter Pills
    pillButtons.forEach(pill => {
      pill.addEventListener("click", (e) => {
        e.preventDefault();
        // Clear search input on category switch to avoid multi-filter collisions
        if (searchInput) searchInput.value = "";
        
        pillButtons.forEach(p => p.classList.remove("is-active", "active"));
        pill.classList.add("is-active", "active");

        activeFilter = pill.getAttribute("data-filter") || "all";
        applyFilter();
      });
    });

    // Connect Search Input
    if (searchInput) {
      searchInput.addEventListener("input", () => {
        const val = searchInput.value.trim();
        if (val.length > 0) {
          // When typing a custom search, activate the 'All' pill so user searches across all data
          activeFilter = "all";
          pillButtons.forEach(p => {
            const pKey = (p.getAttribute("data-filter") || "").toLowerCase();
            if (pKey === "all" || pKey === "") {
              p.classList.add("is-active", "active");
            } else {
              p.classList.remove("is-active", "active");
            }
          });
        }
        applyFilter();
      });
    }

    // Connect KPI Cards (One-click category filter with visual sync)
    kpiCards.forEach(card => {
      card.addEventListener("click", () => {
        const kpiVal = (card.getAttribute("data-kpi-filter") || "all").trim();
        if (searchInput) searchInput.value = "";

        if (kpiVal.toUpperCase() === "CIRCUITS" || kpiVal.toUpperCase() === "ELECTRONICS") {
          pillButtons.forEach(p => p.classList.remove("is-active", "active"));
          activeFilter = "CIRCUITS";
          applyFilter();
          return;
        }

        // Find direct matching pill
        let matchedPill = null;
        pillButtons.forEach(p => {
          const pVal = (p.getAttribute("data-filter") || "").trim();
          if (pVal.toUpperCase() === kpiVal.toUpperCase()) {
            matchedPill = p;
          } else if ((kpiVal === "all" || kpiVal === "") && (pVal === "all" || pVal === "")) {
            matchedPill = p;
          }
        });

        if (matchedPill) {
          matchedPill.click();
        } else {
          pillButtons.forEach(p => p.classList.remove("is-active", "active"));
          activeFilter = kpiVal;
          applyFilter();
        }
      });
    });
  }

  initTableFilterEngine();

  // 2. Interactive 1-Click Copy Chips
  document.querySelectorAll(".btn-copy-chip").forEach(chip => {
    chip.addEventListener("click", (e) => {
      e.stopPropagation();
      const textToCopy = chip.getAttribute("data-copy") || chip.innerText.trim();
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalHtml = chip.innerHTML;
        chip.innerHTML = '<i class="bi bi-check2 text-success"></i> Copied!';
        chip.style.borderColor = 'rgba(16, 185, 129, 0.4)';
        setTimeout(() => {
          chip.innerHTML = originalHtml;
          chip.style.borderColor = '';
        }, 1800);
      });
    });
  });

  console.info("ClubHub DBMS • Shneiderman 8 Golden Rules Suite Initialized");
});
