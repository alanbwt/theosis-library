/**
 * Theosis Library — Headline reveal animation
 * Soft fade-in + slide up as headings enter viewport.
 */

(function () {
  'use strict';

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  function init() {
    var headings = document.querySelectorAll('h1, h2');
    headings.forEach(function (h) {
      h.classList.add('reveal-heading');
      observer.observe(h);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
