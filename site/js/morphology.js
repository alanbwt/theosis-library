/**
 * Theosis Library — Morphological word popups
 * Click any Greek or Latin word in the original text to see:
 * lemma, parsing, and English meaning.
 */

(function () {
  'use strict';

  var morphData = null;
  var popup = null;
  var loaded = false;
  var loading = false;

  function createPopup() {
    popup = document.createElement('div');
    popup.className = 'morph-popup';
    popup.innerHTML = '<div class="morph-popup-inner">' +
      '<div class="morph-close" onclick="this.parentElement.parentElement.classList.remove(\'visible\')">&times;</div>' +
      '<div class="morph-word"></div>' +
      '<div class="morph-lemma"></div>' +
      '<div class="morph-parse"></div>' +
      '<div class="morph-gloss"></div>' +
      '</div>';
    document.body.appendChild(popup);
  }

  function loadMorphData() {
    if (loaded || loading) return Promise.resolve();
    loading = true;
    return fetch('/data/morphology.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        morphData = data;
        loaded = true;
        loading = false;
      })
      .catch(function () { loading = false; });
  }

  function showPopup(word, rect) {
    if (!morphData || !popup) return;

    var key = word.toLowerCase();
    var entry = morphData[key];

    if (!entry) {
      // Try stripping final punctuation
      key = key.replace(/[·.,;:]+$/, '');
      entry = morphData[key];
    }

    if (!entry) return;

    popup.querySelector('.morph-word').textContent = word;
    popup.querySelector('.morph-lemma').textContent = entry.lemma ? '→ ' + entry.lemma : '';
    popup.querySelector('.morph-parse').textContent = entry.parse || '';
    popup.querySelector('.morph-gloss').textContent = entry.gloss || '';

    // Position popup near the clicked word
    var top = rect.bottom + window.scrollY + 8;
    var left = rect.left + window.scrollX;

    // Keep within viewport
    popup.style.top = top + 'px';
    popup.style.left = Math.min(left, window.innerWidth - 280) + 'px';
    popup.classList.add('visible');
  }

  function hidePopup() {
    if (popup) popup.classList.remove('visible');
  }

  // Wrap Greek words in the original text columns with clickable spans
  function wrapGreekWords() {
    var origColumns = document.querySelectorAll('.parallel-original');
    origColumns.forEach(function (col) {
      var walker = document.createTreeWalker(col, NodeFilter.SHOW_TEXT);
      var textNodes = [];
      while (walker.nextNode()) textNodes.push(walker.currentNode);

      textNodes.forEach(function (node) {
        var text = node.textContent;
        // Match Greek word sequences
        if (/[\u0370-\u03FF\u1F00-\u1FFF]/.test(text)) {
          var html = text.replace(
            /([\u0370-\u03FF\u1F00-\u1FFF\u0300-\u036F]+)/g,
            '<span class="morph-word-clickable">$1</span>'
          );
          var wrapper = document.createElement('span');
          wrapper.innerHTML = html;
          node.parentNode.replaceChild(wrapper, node);
        }
      });
    });
  }

  // Initialize
  createPopup();

  // Click handler for Greek words (delegated)
  document.addEventListener('click', function (e) {
    var target = e.target;
    if (target.classList && target.classList.contains('morph-word-clickable')) {
      e.preventDefault();

      if (!loaded) {
        loadMorphData().then(function () {
          var rect = target.getBoundingClientRect();
          showPopup(target.textContent, rect);
        });
      } else {
        var rect = target.getBoundingClientRect();
        showPopup(target.textContent, rect);
      }
    } else if (!popup.contains(target)) {
      hidePopup();
    }
  });

  // Wrap words after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wrapGreekWords);
  } else {
    wrapGreekWords();
  }
})();
