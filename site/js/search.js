/**
 * Theosis Library — Full-text search with MiniSearch
 * Searches across English, Greek, Latin at the passage level.
 * Faceted filtering by era, tradition, language, category.
 */

import MiniSearch from 'https://esm.sh/minisearch@7.1.1';

(function () {
  'use strict';

  var searchInput = document.getElementById('search-input');
  var resultsInfo = document.getElementById('search-results-info');
  var resultsContainer = document.getElementById('search-results');
  if (!searchInput) return;

  // Create results container if it doesn't exist
  if (!resultsContainer) {
    resultsContainer = document.createElement('div');
    resultsContainer.id = 'search-results';
    resultsContainer.className = 'search-results';
    searchInput.parentElement.after(resultsContainer);
  }

  var miniSearch = null;
  var indexLoaded = false;
  var indexLoading = false;
  var metaData = null;
  var questionMap = null;

  // Load question map for natural language queries
  fetch('/data/question-map.json')
    .then(function (r) { return r.json(); })
    .then(function (data) { questionMap = data; })
    .catch(function () {});

  function expandQuery(q) {
    if (!questionMap) return q;
    var lower = q.toLowerCase();
    for (var i = 0; i < questionMap.questions.length; i++) {
      var qm = questionMap.questions[i];
      for (var j = 0; j < qm.patterns.length; j++) {
        if (lower.indexOf(qm.patterns[j]) !== -1) {
          return qm.search;
        }
      }
    }
    return q;
  }

  // Load metadata immediately (small file)
  fetch('/data/texts-meta.json')
    .then(function (r) { return r.json(); })
    .then(function (data) { metaData = data; })
    .catch(function () {});

  function loadSearchIndex() {
    if (indexLoaded || indexLoading) return Promise.resolve();
    indexLoading = true;

    return fetch('/data/search-index.json')
      .then(function (r) { return r.json(); })
      .then(function (passages) {
        miniSearch = new MiniSearch({
          fields: ['en', 'orig', 'title', 'author'],
          storeFields: ['pid', 'tid', 's', 'en', 'orig', 'title', 'author', 'slug'],
          idField: 'pid',
          searchOptions: {
            boost: { title: 3, en: 2, orig: 1.5, author: 1 },
            prefix: true,
            fuzzy: 0.2,
          },
          // Normalize Greek diacritics for search
          processTerm: function (term) {
            return term
              .normalize('NFD')
              .replace(/[\u0300-\u036f]/g, '')
              .toLowerCase();
          }
        });

        miniSearch.addAll(passages);
        indexLoaded = true;
        indexLoading = false;
      })
      .catch(function (err) {
        console.error('Search index failed to load:', err);
        indexLoading = false;
      });
  }

  function highlightMatch(text, terms) {
    if (!text || !terms.length) return text;
    // Truncate to ~200 chars around first match
    var lowerText = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    var firstMatch = -1;
    for (var i = 0; i < terms.length; i++) {
      var pos = lowerText.indexOf(terms[i].normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase());
      if (pos !== -1 && (firstMatch === -1 || pos < firstMatch)) firstMatch = pos;
    }

    var start = Math.max(0, firstMatch - 80);
    var end = Math.min(text.length, firstMatch + 150);
    var snippet = (start > 0 ? '...' : '') + text.slice(start, end) + (end < text.length ? '...' : '');

    // Bold the matching terms
    for (var i = 0; i < terms.length; i++) {
      var re = new RegExp('(' + terms[i].replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
      snippet = snippet.replace(re, '<mark>$1</mark>');
    }
    return snippet;
  }

  function renderResults(results, query) {
    if (!results.length) {
      resultsContainer.innerHTML = '<div class="search-no-results">No passages found for "' + query + '"</div>';
      resultsInfo.textContent = '0 results';
      resultsInfo.style.display = 'block';
      return;
    }

    var terms = query.trim().split(/\s+/);
    var html = '';

    // Group by text
    var grouped = {};
    results.forEach(function (r) {
      if (!grouped[r.tid]) grouped[r.tid] = { title: r.title, author: r.author, slug: r.slug, passages: [] };
      grouped[r.tid].passages.push(r);
    });

    var textIds = Object.keys(grouped);
    for (var i = 0; i < textIds.length; i++) {
      var group = grouped[textIds[i]];
      html += '<div class="search-group">';
      html += '<div class="search-group-title">' + group.author + ', <em>' + group.title + '</em></div>';

      for (var j = 0; j < group.passages.length; j++) {
        var p = group.passages[j];
        var snippet = highlightMatch(p.en, terms) || highlightMatch(p.orig, terms) || p.en.slice(0, 200);
        var sectionAnchor = p.s.replace(/[.:]/g, '-');
        html += '<a href="/library/' + group.slug + '.html#s' + sectionAnchor + '" class="search-result">';
        html += '<span class="search-result-ref">§' + p.s + '</span>';
        html += '<span class="search-result-snippet">' + snippet + '</span>';
        html += '</a>';
      }

      html += '</div>';
    }

    resultsContainer.innerHTML = html;
    resultsInfo.textContent = results.length + ' passage' + (results.length !== 1 ? 's' : '') + ' across ' + textIds.length + ' text' + (textIds.length !== 1 ? 's' : '');
    resultsInfo.style.display = 'block';
  }

  // Also keep the basic DOM filtering for the library view tabs
  var textItems = document.querySelectorAll('.text-item');

  function domFilter(query) {
    if (!query) {
      for (var i = 0; i < textItems.length; i++) textItems[i].style.display = '';
      resultsContainer.innerHTML = '';
      resultsInfo.style.display = 'none';
      return;
    }

    var terms = query.toLowerCase().split(/\s+/);
    var visible = 0;
    for (var i = 0; i < textItems.length; i++) {
      var item = textItems[i];
      var searchable = (
        (item.getAttribute('data-author') || '') + ' ' +
        (item.getAttribute('data-title') || '') + ' ' +
        (item.getAttribute('data-themes') || '') + ' ' +
        (item.querySelector('.text-description') || {}).textContent || ''
      ).toLowerCase();

      var match = terms.every(function (t) { return searchable.indexOf(t) !== -1; });
      item.style.display = match ? '' : 'none';
      if (match) visible++;
    }
  }

  var debounceTimer;
  searchInput.addEventListener('input', function () {
    var query = this.value.trim();

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function () {
      // DOM filter for the text list
      domFilter(query);

      // Full-text passage search
      if (query.length < 2) {
        resultsContainer.innerHTML = '';
        resultsInfo.style.display = 'none';
        return;
      }

      if (!indexLoaded) {
        resultsInfo.textContent = 'Loading search index...';
        resultsInfo.style.display = 'block';
        loadSearchIndex().then(function () {
          if (miniSearch) {
            var results = miniSearch.search(expandQuery(query), { limit: 50 });
            renderResults(results, query);
          }
        });
      } else if (miniSearch) {
        var results = miniSearch.search(expandQuery(query), { limit: 50 });
        renderResults(results, query);
      }
    }, 200);
  });
  // Auto-search from URL ?q= param
  var urlQ = new URLSearchParams(window.location.search).get('q');
  if (urlQ && searchInput) {
    searchInput.value = urlQ;
    searchInput.dispatchEvent(new Event('input'));
  }
})();
