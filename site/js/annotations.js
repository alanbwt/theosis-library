/**
 * Theosis Library — Annotation & Highlight System
 * Select text to highlight. Add notes. Saved to localStorage.
 * No accounts needed. Export as plain text.
 */

(function () {
  'use strict';

  var STORAGE_KEY = 'theosis-annotations';
  var annotations = [];
  var toolbar = null;
  var panel = null;
  var currentSlug = '';

  // Detect which text we're on from the URL
  var match = window.location.pathname.match(/\/library\/(.+)\.html/);
  if (!match) return;
  currentSlug = match[1];

  function loadAnnotations() {
    try {
      var data = localStorage.getItem(STORAGE_KEY);
      annotations = data ? JSON.parse(data) : [];
    } catch (e) {
      annotations = [];
    }
  }

  function saveAnnotations() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(annotations));
    updateBadge();
  }

  function getPageAnnotations() {
    return annotations.filter(function (a) { return a.slug === currentSlug; });
  }

  // ─── Selection Toolbar ───────────────────────────────────

  function createToolbar() {
    toolbar = document.createElement('div');
    toolbar.className = 'annot-toolbar';
    toolbar.innerHTML =
      '<button class="annot-toolbar-btn annot-highlight-btn" title="Highlight">Highlight</button>' +
      '<button class="annot-toolbar-btn annot-note-btn" title="Add note">+ Note</button>';
    document.body.appendChild(toolbar);

    toolbar.querySelector('.annot-highlight-btn').addEventListener('click', function () {
      addAnnotation(false);
    });
    toolbar.querySelector('.annot-note-btn').addEventListener('click', function () {
      addAnnotation(true);
    });
  }

  function showToolbar(rect) {
    var top = rect.top + window.scrollY - 40;
    var left = rect.left + window.scrollX + (rect.width / 2) - 75;
    toolbar.style.top = top + 'px';
    toolbar.style.left = Math.max(8, left) + 'px';
    toolbar.classList.add('visible');
  }

  function hideToolbar() {
    toolbar.classList.remove('visible');
  }

  // ─── Add annotation ──────────────────────────────────────

  function addAnnotation(withNote) {
    var sel = window.getSelection();
    if (!sel.rangeCount || sel.isCollapsed) return;

    var range = sel.getRangeAt(0);
    var text = sel.toString().trim();
    if (!text) return;

    // Find which section this is in
    var section = range.startContainer;
    while (section && !section.classList?.contains('parallel-section')) {
      section = section.parentElement;
    }
    var sectionId = section ? section.id : '';

    var note = '';
    if (withNote) {
      note = prompt('Add a note for this highlight:');
      if (note === null) return; // cancelled
    }

    var annot = {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      slug: currentSlug,
      section: sectionId,
      text: text.slice(0, 500),
      note: note || '',
      date: new Date().toISOString().split('T')[0],
    };

    annotations.push(annot);
    saveAnnotations();

    // Visual highlight
    try {
      var mark = document.createElement('mark');
      mark.className = 'annot-highlight';
      mark.dataset.annotId = annot.id;
      if (annot.note) mark.title = annot.note;
      range.surroundContents(mark);
    } catch (e) {
      // surroundContents can fail on complex selections
    }

    sel.removeAllRanges();
    hideToolbar();
    showToast(withNote ? 'Note saved' : 'Highlighted');
  }

  // ─── Annotations Panel ───────────────────────────────────

  function createPanel() {
    panel = document.createElement('div');
    panel.className = 'annot-panel';
    panel.innerHTML =
      '<div class="annot-panel-header">' +
      '  <span>My Notes</span>' +
      '  <button class="annot-panel-close" onclick="this.closest(\'.annot-panel\').classList.remove(\'open\')">&times;</button>' +
      '</div>' +
      '<div class="annot-panel-body"></div>' +
      '<div class="annot-panel-footer">' +
      '  <button class="annot-export-btn" onclick="exportAnnotations()">Export as Text</button>' +
      '</div>';
    document.body.appendChild(panel);
  }

  function updatePanel() {
    var pageAnnots = getPageAnnotations();
    var body = panel.querySelector('.annot-panel-body');

    if (!pageAnnots.length) {
      body.innerHTML = '<div class="annot-empty">No annotations on this page. Select text to highlight.</div>';
      return;
    }

    var html = '';
    pageAnnots.forEach(function (a) {
      html += '<div class="annot-item" data-id="' + a.id + '">' +
        '<div class="annot-item-text">"' + a.text.slice(0, 120) + (a.text.length > 120 ? '...' : '') + '"</div>' +
        (a.note ? '<div class="annot-item-note">' + a.note + '</div>' : '') +
        '<div class="annot-item-meta">' + a.date +
        ' · <a href="#" onclick="deleteAnnotation(\'' + a.id + '\'); return false;">Delete</a></div>' +
        '</div>';
    });
    body.innerHTML = html;
  }

  // ─── Badge + Toggle ──────────────────────────────────────

  var badge = null;

  function createBadge() {
    badge = document.createElement('button');
    badge.className = 'annot-badge';
    badge.title = 'My annotations';
    badge.innerHTML = '<span class="annot-badge-icon">Notes</span><span class="annot-badge-count">0</span>';
    badge.addEventListener('click', function () {
      updatePanel();
      panel.classList.toggle('open');
    });
    document.body.appendChild(badge);
  }

  function updateBadge() {
    var count = getPageAnnotations().length;
    badge.querySelector('.annot-badge-count').textContent = count;
    badge.style.display = count > 0 || panel.classList.contains('open') ? '' : '';
  }

  // ─── Global functions ────────────────────────────────────

  window.deleteAnnotation = function (id) {
    annotations = annotations.filter(function (a) { return a.id !== id; });
    saveAnnotations();
    // Remove visual highlight
    var mark = document.querySelector('[data-annot-id="' + id + '"]');
    if (mark) {
      var parent = mark.parentNode;
      while (mark.firstChild) parent.insertBefore(mark.firstChild, mark);
      parent.removeChild(mark);
    }
    updatePanel();
  };

  window.exportAnnotations = function () {
    var pageAnnots = getPageAnnotations();
    if (!pageAnnots.length) return;

    var title = document.querySelector('h1')?.textContent || currentSlug;
    var lines = ['Annotations: ' + title, 'URL: ' + window.location.href, ''];

    pageAnnots.forEach(function (a) {
      lines.push('§' + (a.section || '') + ' | ' + a.date);
      lines.push('"' + a.text + '"');
      if (a.note) lines.push('Note: ' + a.note);
      lines.push('');
    });

    var text = lines.join('\n');
    navigator.clipboard.writeText(text).then(function () {
      showToast('Annotations copied to clipboard');
    }).catch(function () {
      prompt('Copy your annotations:', text);
    });
  };

  function showToast(msg) {
    var toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(function () { toast.classList.remove('show'); }, 2200);
  }

  // ─── Text selection listener ─────────────────────────────

  document.addEventListener('mouseup', function (e) {
    // Don't show toolbar if clicking inside toolbar/panel/popup
    if (toolbar.contains(e.target) || panel.contains(e.target)) return;
    if (e.target.closest('.morph-popup')) return;

    setTimeout(function () {
      var sel = window.getSelection();
      if (sel.isCollapsed || !sel.toString().trim()) {
        hideToolbar();
        return;
      }

      // Only for translation content areas
      var anchor = sel.anchorNode;
      var inTranslation = false;
      var node = anchor;
      while (node) {
        if (node.classList && (
          node.classList.contains('parallel-translation') ||
          node.classList.contains('parallel-original') ||
          node.classList.contains('introduction')
        )) {
          inTranslation = true;
          break;
        }
        node = node.parentElement;
      }

      if (!inTranslation) {
        hideToolbar();
        return;
      }

      var range = sel.getRangeAt(0);
      var rect = range.getBoundingClientRect();
      showToolbar(rect);
    }, 10);
  });

  // ─── Init ────────────────────────────────────────────────

  loadAnnotations();
  createToolbar();
  createPanel();
  createBadge();
  updateBadge();
})();
