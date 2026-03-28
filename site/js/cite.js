/**
 * Theosis Library — Citation and sharing
 */

function showToast(msg) {
  var toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(function () { toast.classList.remove('show'); }, 2200);
}

function citePasage(btn) {
  var section = btn.closest('.parallel-section');
  if (!section) return;

  var author = section.getAttribute('data-author') || '';
  var title = section.getAttribute('data-title') || '';
  var sec = section.getAttribute('data-section') || '';
  var translator = section.getAttribute('data-translator') || '';
  var year = section.getAttribute('data-year') || '';
  var urlPath = section.getAttribute('data-url-path') || '';

  var url = window.location.origin + urlPath;
  var citation = author + ', ' + title + ', ' + sec +
    ', trans. ' + translator +
    ', Theosis Library (' + year + '), ' + url + '.';

  navigator.clipboard.writeText(citation).then(function () {
    showToast('Citation copied');
  }).catch(function () {
    // Fallback
    prompt('Copy this citation:', citation);
  });
}

function sharePassage(btn) {
  var section = btn.closest('.parallel-section');
  if (!section) return;

  var urlPath = section.getAttribute('data-url-path') || '';
  var url = window.location.origin + urlPath;

  if (navigator.share) {
    navigator.share({
      title: document.title,
      url: url
    });
  } else {
    navigator.clipboard.writeText(url).then(function () {
      showToast('Link copied');
    }).catch(function () {
      prompt('Copy this link:', url);
    });
  }
}
