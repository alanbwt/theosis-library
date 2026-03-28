/**
 * Theosis Library — Scan lightbox viewer
 * Minimal dialog-based viewer with zoom.
 */

(function () {
  'use strict';

  // Create dialog element once
  var dialog = document.createElement('dialog');
  dialog.className = 'scan-lightbox';
  dialog.innerHTML =
    '<div class="scan-lightbox-inner">' +
    '  <button class="scan-lightbox-close" aria-label="Close">&times;</button>' +
    '  <img class="scan-lightbox-img" src="" alt="Manuscript scan">' +
    '  <div class="scan-lightbox-hint">Scroll to zoom · Click outside to close</div>' +
    '</div>';
  document.body.appendChild(dialog);

  var img = dialog.querySelector('.scan-lightbox-img');
  var scale = 1;
  var MIN_SCALE = 0.5;
  var MAX_SCALE = 4;

  dialog.querySelector('.scan-lightbox-close').addEventListener('click', function () {
    dialog.close();
  });

  dialog.addEventListener('click', function (e) {
    if (e.target === dialog) dialog.close();
  });

  dialog.addEventListener('close', function () {
    scale = 1;
    img.style.transform = '';
  });

  // Scroll to zoom
  dialog.addEventListener('wheel', function (e) {
    e.preventDefault();
    var delta = e.deltaY > 0 ? -0.15 : 0.15;
    scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale + delta));
    img.style.transform = 'scale(' + scale + ')';
  }, { passive: false });

  // Pinch to zoom (mobile)
  var lastPinchDist = 0;
  dialog.addEventListener('touchstart', function (e) {
    if (e.touches.length === 2) {
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      lastPinchDist = Math.sqrt(dx * dx + dy * dy);
    }
  });

  dialog.addEventListener('touchmove', function (e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      var dx = e.touches[0].clientX - e.touches[1].clientX;
      var dy = e.touches[0].clientY - e.touches[1].clientY;
      var dist = Math.sqrt(dx * dx + dy * dy);
      var delta = (dist - lastPinchDist) * 0.005;
      scale = Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale + delta));
      img.style.transform = 'scale(' + scale + ')';
      lastPinchDist = dist;
    }
  }, { passive: false });

  // Global function called from onclick
  window.openScan = function (src) {
    scale = 1;
    img.style.transform = '';
    img.src = src;
    dialog.showModal();
  };
})();
