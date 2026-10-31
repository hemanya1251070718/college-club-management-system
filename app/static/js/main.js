/**
 * ClubHub Luxury Automotive 3D & Micro-Interaction Engine
 * Inspired by Tesla, Audi & BMW Digital Experiences
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Initialize 3D Ambient WebGL Canvas (Three.js)
  init3DBackground();

  // 2. Initialize 3D Card Interactive Tilt
  init3DCardTilt();

  // 3. Confirm Delete Handlers
  initDeleteConfirmations();

  // 4. Auto Dismiss Alerts
  initAlertsAutoDismiss();
});

/**
 * Interactive 3D Particle Constellation Wave
 */
function init3DBackground() {
  const canvas = document.getElementById("webgl-bg-canvas");
  if (!canvas || typeof THREE === "undefined") return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
  camera.position.z = 240;
  camera.position.y = 40;

  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  // Particle Mesh Constellation
  const particleCount = 750;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(particleCount * 3);
  const scales = new Float32Array(particleCount);

  let i = 0;
  for (let ix = 0; ix < 50; ix++) {
    for (let iy = 0; iy < 15; iy++) {
      positions[i] = (ix - 25) * 18; // x
      positions[i + 1] = 0;          // y
      positions[i + 2] = (iy - 7.5) * 18; // z
      scales[i / 3] = 1.2;
      i += 3;
    }
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  // Create subtle circular texture
  const pCanvas = document.createElement('canvas');
  pCanvas.width = 16;
  pCanvas.height = 16;
  const pCtx = pCanvas.getContext('2d');
  const gradient = pCtx.createRadialGradient(8, 8, 0, 8, 8, 8);
  gradient.addColorStop(0, 'rgba(56, 189, 248, 1)');
  gradient.addColorStop(0.5, 'rgba(0, 242, 254, 0.4)');
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
  pCtx.fillStyle = gradient;
  pCtx.fillRect(0, 0, 16, 16);
  const pTexture = new THREE.CanvasTexture(pCanvas);

  const material = new THREE.PointsMaterial({
    size: 4.5,
    map: pTexture,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  const particles = new THREE.Points(geometry, material);
  scene.add(particles);

  // Mouse Parallax
  let mouseX = 0;
  let mouseY = 0;
  let targetX = 0;
  let targetY = 0;

  window.addEventListener('mousemove', (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.05;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.05;
  });

  // Smooth Sine Wave Animation Loop
  let step = 0;
  function animate() {
    requestAnimationFrame(animate);

    step += 0.025;
    targetX += (mouseX - targetX) * 0.04;
    targetY += (mouseY - targetY) * 0.04;

    camera.position.x = targetX;
    camera.position.y = 40 - targetY;
    camera.lookAt(0, 0, 0);

    const pos = particles.geometry.attributes.position.array;
    let idx = 0;
    for (let ix = 0; ix < 50; ix++) {
      for (let iy = 0; iy < 15; iy++) {
        // Fluid sine-cosine wave
        pos[idx + 1] = Math.sin((ix + step) * 0.3) * 12 + Math.cos((iy + step) * 0.5) * 12;
        idx += 3;
      }
    }
    particles.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }
  animate();

  // Responsive Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

/**
 * 3D Card Interactive Tilt Effect (Automotive Glass Hover)
 */
function init3DCardTilt() {
  const cards = document.querySelectorAll(".card, .stat-card");
  cards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -4;
      const rotateY = ((x - centerX) / centerX) * 4;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)`;
    });
  });
}

/**
 * Delete confirmation dialogs
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

/**
 * Alerts auto-dismiss
 */
function initAlertsAutoDismiss() {
  const alerts = document.querySelectorAll(".alert-dismissible");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 7000);
  });
}
