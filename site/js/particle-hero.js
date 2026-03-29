/**
 * Theosis Library — World-class 3D Particle Portrait
 * Three.js Points + custom GLSL shaders + UnrealBloomPass
 * 300k full-color particles with brightness-mapped 3D depth
 */

import * as THREE from 'https://esm.sh/three@0.170.0';
import { EffectComposer } from 'https://esm.sh/three@0.170.0/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'https://esm.sh/three@0.170.0/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'https://esm.sh/three@0.170.0/addons/postprocessing/UnrealBloomPass.js';

(function () {
  'use strict';

  const container = document.getElementById('particle-hero');
  if (!container) return;

  // --- Config ---
  const isMobile = window.innerWidth < 768;
  const SAMPLE_W = isMobile ? 320 : 640;
  const DEPTH_SCALE = 40;
  const SPREAD = 200;
  const BLOOM_STRENGTH = 0.3;
  const BLOOM_RADIUS = 0.4;
  const BLOOM_THRESHOLD = 0.7;
  const MORPH_INTERVAL = 8000;
  const MORPH_SPEED = 0.015;

  const IMAGES = [
    '/assets/christ-portrait.jpg',
    '/assets/timeline/gilgamesh-tablet.jpg',
    '/assets/timeline/book-of-dead.jpg',
    '/assets/timeline/codex-sinaiticus.jpg',
  ];

  // --- Scene setup ---
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0xf4ede4, 1);
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4ede4);

  const camera = new THREE.PerspectiveCamera(50, 1, 1, 1000);
  camera.position.set(0, 0, 280);

  // --- Post-processing ---
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(1, 1), BLOOM_STRENGTH, BLOOM_RADIUS, BLOOM_THRESHOLD
  );
  composer.addPass(bloomPass);

  // --- Shaders ---
  const vertexShader = `
    attribute vec3 aColor;
    attribute float aSize;
    attribute vec3 aTarget;
    attribute vec3 aTargetColor;
    attribute float aTargetSize;
    attribute float aRandom;

    uniform float uTime;
    uniform float uMorph;
    uniform vec2 uMouse;
    uniform float uPointScale;

    varying vec3 vColor;
    varying float vAlpha;

    // Simplex noise (simplified)
    float hash(float n) { return fract(sin(n) * 43758.5453); }
    float noise(float x) {
      float i = floor(x);
      float f = fract(x);
      f = f * f * (3.0 - 2.0 * f);
      return mix(hash(i), hash(i + 1.0), f);
    }

    void main() {
      // Morph between current and target position
      vec3 pos = mix(position, aTarget, uMorph);
      vec3 col = mix(aColor, aTargetColor, uMorph);
      float sz = mix(aSize, aTargetSize, uMorph);

      // Organic breathing drift
      float t = uTime * 0.5 + aRandom * 6.28;
      pos.x += sin(t + aRandom * 10.0) * 0.8;
      pos.y += cos(t * 0.8 + aRandom * 7.0) * 0.6;
      pos.z += sin(t * 0.6 + aRandom * 5.0) * 0.5;

      // Mouse repulsion
      vec4 mvPos = modelViewMatrix * vec4(pos, 1.0);
      vec4 projected = projectionMatrix * mvPos;
      vec2 ndc = projected.xy / projected.w;
      vec2 diff = ndc - uMouse;
      float dist = length(diff);
      if (dist < 0.2) {
        float force = (1.0 - dist / 0.2) * 15.0;
        pos.x += normalize(diff).x * force;
        pos.y += normalize(diff).y * force;
        pos.z += 5.0 * (1.0 - dist / 0.2);
      }

      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);

      // Size attenuation (perspective)
      float depth = -mvPos.z;
      gl_PointSize = sz * uPointScale * (200.0 / depth);
      gl_PointSize = clamp(gl_PointSize, 0.5, 30.0);

      vColor = col;
      // Slight alpha variation for depth
      vAlpha = 0.75 + 0.25 * (1.0 - smoothstep(200.0, 350.0, depth));
    }
  `;

  const fragmentShader = `
    varying vec3 vColor;
    varying float vAlpha;

    void main() {
      // Soft circular particle
      vec2 c = gl_PointCoord - 0.5;
      float d = length(c);
      if (d > 0.5) discard;

      float alpha = vAlpha * (1.0 - smoothstep(0.25, 0.5, d));
      gl_FragColor = vec4(vColor, alpha);
    }
  `;

  // --- State ---
  let geometry, material, points;
  let imageDataSets = [];
  let currentIdx = 0;
  let morphProgress = 1.0;
  let lastMorphTime = 0;
  let mouse = new THREE.Vector2(-10, -10);
  let cameraAngle = 0;
  let particleCount = 0;

  // --- Image sampling ---
  function sampleImage(img) {
    const sCanvas = document.createElement('canvas');
    const sCtx = sCanvas.getContext('2d');
    const aspect = img.height / img.width;
    const sW = SAMPLE_W;
    const sH = Math.round(sW * aspect);
    sCanvas.width = sW;
    sCanvas.height = sH;
    sCtx.drawImage(img, 0, 0, sW, sH);
    const data = sCtx.getImageData(0, 0, sW, sH).data;

    const result = { positions: [], colors: [], sizes: [] };
    const imgAspect = sW / sH;

    for (let y = 0; y < sH; y++) {
      for (let x = 0; x < sW; x++) {
        const i = (y * sW + x) * 4;
        const r = data[i] / 255;
        const g = data[i + 1] / 255;
        const b = data[i + 2] / 255;
        const bright = 0.299 * r + 0.587 * g + 0.114 * b;

        // Skip very bright pixels (background)
        if (bright > 0.88) continue;

        const nx = ((x / sW) - 0.5) * SPREAD * imgAspect;
        const ny = -((y / sH) - 0.5) * SPREAD;
        const nz = (1.0 - bright) * DEPTH_SCALE - DEPTH_SCALE * 0.3;

        result.positions.push(nx, ny, nz);
        result.colors.push(r, g, b);
        result.sizes.push(1.0 + (1.0 - bright) * 2.5);
      }
    }

    return result;
  }

  function normalizeDataSet(dataset, targetCount) {
    const count = dataset.positions.length / 3;
    if (count >= targetCount) {
      // Trim
      dataset.positions = dataset.positions.slice(0, targetCount * 3);
      dataset.colors = dataset.colors.slice(0, targetCount * 3);
      dataset.sizes = dataset.sizes.slice(0, targetCount);
    } else {
      // Pad by duplicating random existing particles
      while (dataset.positions.length / 3 < targetCount) {
        const idx = Math.floor(Math.random() * count);
        dataset.positions.push(
          dataset.positions[idx * 3] + (Math.random() - 0.5) * 2,
          dataset.positions[idx * 3 + 1] + (Math.random() - 0.5) * 2,
          dataset.positions[idx * 3 + 2] + (Math.random() - 0.5) * 2
        );
        dataset.colors.push(dataset.colors[idx * 3], dataset.colors[idx * 3 + 1], dataset.colors[idx * 3 + 2]);
        dataset.sizes.push(dataset.sizes[idx]);
      }
    }
  }

  function buildParticles() {
    // Use the first image's count as our particle count (after trimming)
    const maxCount = imageDataSets.reduce((max, ds) => Math.max(max, ds.positions.length / 3), 0);
    particleCount = Math.min(maxCount, isMobile ? 80000 : 300000);

    // Normalize all datasets to same count
    imageDataSets.forEach(ds => normalizeDataSet(ds, particleCount));

    const first = imageDataSets[0];
    const second = imageDataSets[1 % imageDataSets.length];

    geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(first.positions, 3));
    geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(first.colors, 3));
    geometry.setAttribute('aSize', new THREE.Float32BufferAttribute(first.sizes, 1));
    geometry.setAttribute('aTarget', new THREE.Float32BufferAttribute(second.positions, 3));
    geometry.setAttribute('aTargetColor', new THREE.Float32BufferAttribute(second.colors, 3));
    geometry.setAttribute('aTargetSize', new THREE.Float32BufferAttribute(second.sizes, 1));

    // Random per-particle seed
    const randoms = new Float32Array(particleCount);
    for (let i = 0; i < particleCount; i++) randoms[i] = Math.random();
    geometry.setAttribute('aRandom', new THREE.Float32BufferAttribute(randoms, 1));

    material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms: {
        uTime: { value: 0 },
        uMorph: { value: 0 },
        uMouse: { value: mouse },
        uPointScale: { value: isMobile ? 0.8 : 1.2 },
      },
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      depthTest: false,
    });

    points = new THREE.Points(geometry, material);
    scene.add(points);
  }

  function setMorphTarget(nextIdx) {
    const next = imageDataSets[nextIdx];
    geometry.setAttribute('aTarget', new THREE.Float32BufferAttribute(next.positions, 3));
    geometry.setAttribute('aTargetColor', new THREE.Float32BufferAttribute(next.colors, 3));
    geometry.setAttribute('aTargetSize', new THREE.Float32BufferAttribute(next.sizes, 1));
    morphProgress = 0;
  }

  function completeMorph() {
    // Swap current attributes to the target
    const target = imageDataSets[currentIdx];
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(target.positions, 3));
    geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(target.colors, 3));
    geometry.setAttribute('aSize', new THREE.Float32BufferAttribute(target.sizes, 1));
  }

  // --- Resize ---
  function resize() {
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
    composer.setSize(w, h);
    bloomPass.resolution.set(w, h);
  }

  // --- Animation ---
  function animate(time) {
    const t = time * 0.001;
    material.uniforms.uTime.value = t;

    // Morph progress
    if (morphProgress < 1.0) {
      morphProgress = Math.min(morphProgress + MORPH_SPEED, 1.0);
      material.uniforms.uMorph.value = morphProgress * morphProgress * (3 - 2 * morphProgress); // smoothstep

      if (morphProgress >= 1.0) {
        completeMorph();
        material.uniforms.uMorph.value = 0;
      }
    }

    // Trigger next morph
    if (time - lastMorphTime > MORPH_INTERVAL && morphProgress >= 1.0) {
      const nextIdx = (currentIdx + 1) % imageDataSets.length;
      setMorphTarget(nextIdx);
      currentIdx = nextIdx;
      lastMorphTime = time;
    }

    // Slow camera orbit
    cameraAngle = Math.sin(t * 0.08) * 0.08;
    camera.position.x = Math.sin(cameraAngle) * 280;
    camera.position.z = Math.cos(cameraAngle) * 280;
    camera.position.y = Math.sin(t * 0.05) * 8;
    camera.lookAt(0, 0, 0);

    composer.render();
    requestAnimationFrame(animate);
  }

  // --- Mouse ---
  container.addEventListener('mousemove', (e) => {
    const rect = container.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  });

  container.addEventListener('mouseleave', () => {
    mouse.x = -10;
    mouse.y = -10;
  });

  window.addEventListener('resize', resize);

  // --- Init ---
  function loadImages(urls) {
    return Promise.all(urls.map(url => new Promise((resolve) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => resolve(img);
      img.onerror = () => resolve(null);
      img.src = url;
    })));
  }

  loadImages(IMAGES).then(imgs => {
    imgs.filter(Boolean).forEach(img => {
      imageDataSets.push(sampleImage(img));
    });

    if (!imageDataSets.length) return;

    resize();
    buildParticles();
    lastMorphTime = performance.now();
    requestAnimationFrame(animate);
  });

  // Pause when hidden
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && points) {
      lastMorphTime = performance.now();
    }
  });
})();
