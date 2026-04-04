/**
 * Theosis Library — Headline decode animation
 * Headlines scramble from random characters to their actual text
 * as they scroll into view.
 */

(function () {
  'use strict';

  var CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,"^`\'. ';
  var DECODE_DURATION = 800; // ms
  var STAGGER = 0.6; // how much to stagger character reveals (0-1)

  function decodeElement(el) {
    if (el.dataset.decoded) return;
    el.dataset.decoded = '1';

    var original = el.textContent;
    var len = original.length;
    var startTime = performance.now();

    // Assign each character a random reveal time
    var timings = [];
    for (var i = 0; i < len; i++) {
      timings.push(Math.random() * STAGGER);
    }

    function tick(now) {
      var elapsed = now - startTime;
      var progress = Math.min(elapsed / DECODE_DURATION, 1.0);
      var result = '';

      for (var i = 0; i < len; i++) {
        if (original[i] === ' ') {
          result += ' ';
        } else if (progress >= timings[i] + (1 - STAGGER)) {
          // Settled on real character
          result += original[i];
        } else if (progress >= timings[i]) {
          // Scrambling phase
          result += CHARS[Math.floor(Math.random() * CHARS.length)];
        } else {
          // Not yet started
          result += CHARS[Math.floor(Math.random() * CHARS.length)];
        }
      }

      el.textContent = result;

      if (progress < 1.0) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = original;
      }
    }

    requestAnimationFrame(tick);
  }

  // Observe all h1 and h2 elements
  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        decodeElement(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  // Wait for DOM
  function init() {
    var headings = document.querySelectorAll('h1, h2');
    headings.forEach(function (h) {
      // Store original text and start with scrambled
      var original = h.textContent;
      h.dataset.original = original;
      // Don't pre-scramble h1 (it's above fold, visible immediately)
      if (h.tagName === 'H1') {
        decodeElement(h);
      } else {
        observer.observe(h);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
