/**
 * Selective WebGL Hero Motion (Active Theory / Tesla Aesthetic)
 * Restricted STRICTLY to landing page hero section.
 * Zero presence or overhead on inner data pages and tables.
 */

(function () {
  const canvas = document.getElementById("hero-webgl-canvas");
  if (!canvas) return;

  // Accessibility & performance checks
  const params = new URLSearchParams(window.location.search);
  if (params.get("webgl") === "off" || localStorage.getItem("webgl_effects") === "off") {
    canvas.style.display = "none";
    return;
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    canvas.style.display = "none";
    return;
  }

  if (typeof THREE === "undefined") return;

  // Scene setup
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(55, canvas.clientWidth / canvas.clientHeight, 1, 1000);
  camera.position.z = 180;
  camera.position.y = 20;

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
  } catch (e) {
    canvas.style.display = "none";
    return;
  }

  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));

  // Flow Field Particle Mesh in Rich Blue & Rich Violet
  const count = 500;
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);

  const colBlue = new THREE.Color("#2F5BEA");
  const colViolet = new THREE.Color("#7C3AED");

  let idx = 0;
  for (let ix = 0; ix < 25; ix++) {
    for (let iy = 0; iy < 20; iy++) {
      positions[idx] = (ix - 12.5) * 16;
      positions[idx + 1] = 0;
      positions[idx + 2] = (iy - 10) * 16;

      const mixRatio = (ix + iy) / 45;
      const c = colBlue.clone().lerp(colViolet, mixRatio);
      colors[idx] = c.r;
      colors[idx + 1] = c.g;
      colors[idx + 2] = c.b;

      idx += 3;
    }
  }

  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  // Point Texture
  const pCanvas = document.createElement("canvas");
  pCanvas.width = 16;
  pCanvas.height = 16;
  const pCtx = pCanvas.getContext("2d");
  const gradient = pCtx.createRadialGradient(8, 8, 0, 8, 8, 8);
  gradient.addColorStop(0, "rgba(255, 255, 255, 0.95)");
  gradient.addColorStop(0.3, "rgba(79, 124, 255, 0.6)");
  gradient.addColorStop(1, "rgba(5, 6, 11, 0)");
  pCtx.fillStyle = gradient;
  pCtx.fillRect(0, 0, 16, 16);
  const texture = new THREE.CanvasTexture(pCanvas);

  const material = new THREE.PointsMaterial({
    size: 4.5,
    vertexColors: true,
    map: texture,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  });

  const points = new THREE.Points(geometry, material);
  scene.add(points);

  // Parallax tracking
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;
  let isVisible = true;
  let animationId = null;

  window.addEventListener("mousemove", (e) => {
    mouseX = (e.clientX - window.innerWidth / 2) * 0.02;
    mouseY = (e.clientY - window.innerHeight / 2) * 0.02;
  }, { passive: true });

  // Pause when off-screen
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      isVisible = entry.isIntersecting;
      if (isVisible && !animationId) {
        animate();
      }
    });
  }, { threshold: 0.05 });
  observer.observe(canvas);

  // Pause when document is hidden
  document.addEventListener("visibilitychange", () => {
    isVisible = (document.visibilityState === "visible");
  });

  let step = 0;
  function animate() {
    if (!isVisible) {
      animationId = null;
      return;
    }
    animationId = requestAnimationFrame(animate);

    step += 0.015;
    targetX += (mouseX - targetX) * 0.03;
    targetY += (mouseY - targetY) * 0.03;

    camera.position.x = targetX;
    camera.position.y = 20 - targetY;
    camera.lookAt(0, 0, 0);

    const pos = points.geometry.attributes.position.array;
    let pIdx = 0;
    for (let ix = 0; ix < 25; ix++) {
      for (let iy = 0; iy < 20; iy++) {
        pos[pIdx + 1] = Math.sin((ix + step) * 0.35) * 8 + Math.cos((iy + step) * 0.4) * 8;
        pIdx += 3;
      }
    }
    points.geometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  }

  animate();

  // Resize listener
  window.addEventListener("resize", () => {
    if (!canvas.clientWidth || !canvas.clientHeight) return;
    camera.aspect = canvas.clientWidth / canvas.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  }, { passive: true });
})();
