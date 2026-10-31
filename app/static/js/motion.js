/**
 * ClubHub Design System Motion Engine
 * Tesla Architectural Interactions & Motion Language
 */

document.addEventListener("DOMContentLoaded", () => {
  initHeaderScroll();
  initSideDrawer();
  initScrollReveal();
  initNumberCounters();
  initAlertsAutoDismiss();
  initDeleteConfirmations();
});

/**
 * 1. Fixed Header Frosted Scroll State
 * Transparent over hero, frosted at >8px scroll
 */
function initHeaderScroll() {
  const header = document.querySelector(".app-header");
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 8) {
      header.classList.add("is-scrolled");
    } else {
      header.classList.remove("is-scrolled");
    }
  };

  window.addEventListener("scroll", handleScroll, { passive: true });
  handleScroll(); // Initial check
}

/**
 * 2. Tesla Side Menu Drawer
 * Slides in from right, full height, with backdrop, focus trap, and ESC close
 */
function initSideDrawer() {
  const menuBtn = document.querySelector(".menu-trigger-btn");
  const drawerBackdrop = document.querySelector(".drawer-backdrop");
  const closeBtn = document.querySelector(".drawer-close-btn");

  if (!menuBtn || !drawerBackdrop) return;

  const openDrawer = () => {
    drawerBackdrop.classList.add("is-open");
    drawerBackdrop.setAttribute("aria-hidden", "false");
    menuBtn.setAttribute("aria-expanded", "true");
    document.body.style.overflow = "hidden";

    // Focus close button
    if (closeBtn) closeBtn.focus();
  };

  const closeDrawer = () => {
    drawerBackdrop.classList.remove("is-open");
    drawerBackdrop.setAttribute("aria-hidden", "true");
    menuBtn.setAttribute("aria-expanded", "false");
    document.body.style.overflow = "";
    menuBtn.focus();
  };

  menuBtn.addEventListener("click", openDrawer);

  if (closeBtn) {
    closeBtn.addEventListener("click", closeDrawer);
  }

  drawerBackdrop.addEventListener("click", (e) => {
    if (e.target === drawerBackdrop) {
      closeDrawer();
    }
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawerBackdrop.classList.contains("is-open")) {
      closeDrawer();
    }
  });
}

/**
 * 3. IntersectionObserver Scroll Reveal
 */
function initScrollReveal() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.querySelectorAll(".reveal-on-scroll").forEach((el) => {
      el.classList.add("is-visible");
    });
    return;
  }

  const revealElements = document.querySelectorAll(".reveal-on-scroll");
  if (!revealElements.length) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        obs.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: "0px 0px -40px 0px"
  });

  revealElements.forEach((el) => observer.observe(el));
}

/**
 * 4. Animated Number Counters for Statistics
 */
function initNumberCounters() {
  const counters = document.querySelectorAll("[data-counter]");
  if (!counters.length) return;

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    counters.forEach(c => {
      c.textContent = c.getAttribute("data-counter");
    });
    return;
  }

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.getAttribute("data-counter"), 10) || 0;
        let count = 0;
        const duration = 1200; // ms
        const stepTime = 20;
        const totalSteps = duration / stepTime;
        const increment = target / totalSteps;

        const timer = setInterval(() => {
          count += increment;
          if (count >= target) {
            el.textContent = target;
            clearInterval(timer);
          } else {
            el.textContent = Math.floor(count);
          }
        }, stepTime);

        obs.unobserve(el);
      }
    });
  }, { threshold: 0.3 });

  counters.forEach(c => observer.observe(c));
}

/**
 * 5. Auto-Dismiss Alerts
 */
function initAlertsAutoDismiss() {
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
        const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
        if (bsAlert) bsAlert.close();
      } else {
        alert.remove();
      }
    }, 6000);
  });
}

/**
 * 6. Delete Action Confirmation Modal / Prompt
 */
function initDeleteConfirmations() {
  const deleteForms = document.querySelectorAll("form.delete-form");
  deleteForms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      const entity = form.dataset.entity || "record";
      if (!confirm(`Are you sure you want to delete this ${entity}? This action is irreversible.`)) {
        e.preventDefault();
      }
    });
  });
}
