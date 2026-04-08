/**
 * Theosis Library — Corinthian Column Frames
 * Decorative columns on left and right edges of the viewport.
 * Capitals at the top, bases at the bottom, fluted shafts that scale with page height.
 * Only visible on screens >= 1200px wide.
 */

(function () {
  'use strict';

  // Skip on narrow screens
  if (window.innerWidth < 1200) return;

  var COLUMN_WIDTH = 48;
  var OPACITY = 0.12;
  var COLOR = '#8a7e6f';

  // Corinthian capital SVG (simplified acanthus leaf design)
  var capitalSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 100" fill="' + COLOR + '">' +
    // Abacus (top slab)
    '<rect x="0" y="0" width="80" height="8" rx="1"/>' +
    // Volutes
    '<path d="M8 8 Q10 20 20 22 Q12 24 10 30 Q8 24 6 22 Q2 20 8 8z"/>' +
    '<path d="M72 8 Q70 20 60 22 Q68 24 70 30 Q72 24 74 22 Q78 20 72 8z"/>' +
    // Central acanthus leaves
    '<path d="M40 10 Q35 30 28 35 Q33 32 38 40 Q40 32 42 40 Q47 32 52 35 Q45 30 40 10z"/>' +
    // Outer leaves
    '<path d="M20 25 Q18 40 14 48 Q20 44 24 50 Q22 42 20 25z"/>' +
    '<path d="M60 25 Q62 40 66 48 Q60 44 56 50 Q58 42 60 25z"/>' +
    // Bell shape
    '<path d="M14 48 Q16 60 20 65 Q28 58 40 55 Q52 58 60 65 Q64 60 66 48 Q60 55 40 52 Q20 55 14 48z"/>' +
    // Neck ring
    '<rect x="18" y="65" width="44" height="4" rx="2"/>' +
    // Astragal (bead molding)
    '<ellipse cx="24" cy="72" rx="3" ry="2.5"/>' +
    '<ellipse cx="33" cy="72" rx="3" ry="2.5"/>' +
    '<ellipse cx="42" cy="72" rx="3" ry="2.5"/>' +
    '<ellipse cx="51" cy="72" rx="3" ry="2.5"/>' +
    '<ellipse cx="60" cy="72" rx="3" ry="2.5"/>' +
    // Shaft top
    '<rect x="16" y="76" width="48" height="24" rx="1"/>' +
    // Fluting hints at top
    '<line x1="24" y1="76" x2="24" y2="100" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="32" y1="76" x2="32" y2="100" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="40" y1="76" x2="40" y2="100" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="48" y1="76" x2="48" y2="100" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="56" y1="76" x2="56" y2="100" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '</svg>';

  // Column base SVG (Attic base with torus and plinth)
  var baseSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 60" fill="' + COLOR + '">' +
    // Shaft bottom
    '<rect x="16" y="0" width="48" height="10" rx="1"/>' +
    // Fluting at bottom
    '<line x1="24" y1="0" x2="24" y2="10" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="32" y1="0" x2="32" y2="10" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="40" y1="0" x2="40" y2="10" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="48" y1="0" x2="48" y2="10" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    '<line x1="56" y1="0" x2="56" y2="10" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.5"/>' +
    // Apophyge (curve into base)
    '<path d="M16 10 Q14 14 12 16 L68 16 Q66 14 64 10z"/>' +
    // Upper torus
    '<ellipse cx="40" cy="20" rx="32" ry="5"/>' +
    // Scotia (concave molding)
    '<path d="M10 25 Q12 30 14 32 L66 32 Q68 30 70 25 L10 25z"/>' +
    // Lower torus
    '<ellipse cx="40" cy="36" rx="34" ry="5.5"/>' +
    // Plinth
    '<rect x="4" y="42" width="72" height="14" rx="2"/>' +
    // Plinth shadow line
    '<line x1="4" y1="49" x2="76" y2="49" stroke="' + COLOR + '" stroke-width="0.5" opacity="0.3"/>' +
    '</svg>';

  function createColumn(side) {
    // Container
    var col = document.createElement('div');
    col.className = 'corinthian-column corinthian-column--' + side;
    col.style.cssText = 'position:fixed;top:0;' + side + ':0;width:' + COLUMN_WIDTH + 'px;height:100vh;z-index:50;pointer-events:none;opacity:' + OPACITY + ';display:flex;flex-direction:column;';

    // Capital
    var cap = document.createElement('div');
    cap.className = 'column-capital';
    cap.innerHTML = capitalSVG;
    cap.style.cssText = 'width:100%;flex-shrink:0;';
    if (side === 'right') cap.style.transform = 'scaleX(-1)';

    // Shaft (fills middle, repeating fluted pattern)
    var shaft = document.createElement('div');
    shaft.className = 'column-shaft';
    shaft.style.cssText = 'flex:1;position:relative;overflow:hidden;';

    // Create fluting with CSS
    var fluteSVG = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="20" viewBox="0 0 48 20">' +
      '<rect x="0" y="0" width="48" height="20" fill="' + COLOR + '"/>' +
      '<line x1="8" y1="0" x2="8" y2="20" stroke="#f4ede4" stroke-width="1" opacity="0.4"/>' +
      '<line x1="16" y1="0" x2="16" y2="20" stroke="#f4ede4" stroke-width="1" opacity="0.4"/>' +
      '<line x1="24" y1="0" x2="24" y2="20" stroke="#f4ede4" stroke-width="1" opacity="0.4"/>' +
      '<line x1="32" y1="0" x2="32" y2="20" stroke="#f4ede4" stroke-width="1" opacity="0.4"/>' +
      '<line x1="40" y1="0" x2="40" y2="20" stroke="#f4ede4" stroke-width="1" opacity="0.4"/>' +
      '</svg>';
    var encoded = 'data:image/svg+xml,' + encodeURIComponent(fluteSVG);
    shaft.style.backgroundImage = 'url("' + encoded + '")';
    shaft.style.backgroundRepeat = 'repeat-y';
    shaft.style.backgroundPosition = 'center';
    shaft.style.backgroundSize = COLUMN_WIDTH + 'px auto';
    // Slight entasis (widening at middle)
    shaft.style.marginLeft = side === 'left' ? '16px' : '0';
    shaft.style.marginRight = side === 'right' ? '16px' : '0';
    shaft.style.width = (COLUMN_WIDTH - 16) + 'px';

    // Base
    var base = document.createElement('div');
    base.className = 'column-base';
    base.innerHTML = baseSVG;
    base.style.cssText = 'width:100%;flex-shrink:0;';
    if (side === 'right') base.style.transform = 'scaleX(-1)';

    col.appendChild(cap);
    col.appendChild(shaft);
    col.appendChild(base);

    return col;
  }

  // Add columns to body
  document.body.appendChild(createColumn('left'));
  document.body.appendChild(createColumn('right'));

  // Handle resize
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var cols = document.querySelectorAll('.corinthian-column');
      for (var i = 0; i < cols.length; i++) {
        cols[i].style.display = window.innerWidth >= 1200 ? 'flex' : 'none';
      }
    }, 200);
  });
})();
