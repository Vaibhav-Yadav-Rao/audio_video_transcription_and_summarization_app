
/* ================================================================
   VoiceScript AI — Dashboard JavaScript
   All API calls use JSON. Handles upload progress, transcription
   loading, summarization loading, downloads, and history.
================================================================ */

'use strict';

// ── State ──────────────────────────────────────────────────────────
let currentTranscript = '';
let currentSummary    = '';

// ── Utility: show/hide loading overlay ────────────────────────────
function showLoader(phase) {
  const overlay  = document.getElementById('loadingOverlay');
  const phaseEl  = document.getElementById('loaderPhase');
  const stepsEl  = document.getElementById('loaderSteps');
  const steps = {
    upload:      ['Uploading your file…',  'Extracting audio…',    'Preparing for AI…'],
    transcribe:  ['Analysing audio…',      'Running Whisper AI…',  'Converting speech to text…'],
    summarize:   ['Reading transcript…',   'Chunking content…',    'Writing your summary…'],
  };
  overlay.classList.remove('hidden');
  let idx = 0;
  phaseEl.textContent = steps[phase][0];
  const interval = setInterval(() => {
    idx = (idx + 1) % steps[phase].length;
    phaseEl.textContent = steps[phase][idx];
  }, 2800);
  overlay._interval = interval;
}

function hideLoader() {
  const overlay = document.getElementById('loadingOverlay');
  clearInterval(overlay._interval);
  overlay.classList.add('hidden');
}

// ── Utility: toast notifications ──────────────────────────────────
function toast(msg, type = 'info') {
  const container = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.innerHTML = `<span class="toast-icon">${type === 'error' ? '✕' : type === 'success' ? '✓' : 'ℹ'}</span><span>${msg}</span>`;
  container.appendChild(t);
  requestAnimationFrame(() => t.classList.add('show'));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 4000);
}

// ── Upload & Transcribe ────────────────────────────────────────────
function uploadFile() {
  const fileInput = document.getElementById('fileInput');
  if (!fileInput.files.length) {
    toast('Please select an audio or video file first.', 'error');
    return;
  }

  const file    = fileInput.files[0];
  const maxSize = 500 * 1024 * 1024; // 500 MB
  if (file.size > maxSize) {
    toast('File is too large. Maximum size is 500 MB.', 'error');
    return;
  }

  const data = new FormData();
  data.append('file', file);

  // Reset UI
  document.getElementById('resultSection').classList.add('hidden');
  document.getElementById('summarySection').classList.add('hidden');
  document.getElementById('progressWrap').classList.remove('hidden');
  const bar = document.getElementById('progressBar');
  bar.style.width = '0%';
  bar.textContent = '0%';

  showLoader('upload');

  const xhr = new XMLHttpRequest();
  xhr.open('POST', '/upload', true);

  xhr.upload.onprogress = (e) => {
    if (e.lengthComputable) {
      const pct = Math.round((e.loaded / e.total) * 100);
      bar.style.width = pct + '%';
      bar.textContent = pct + '%';
      if (pct === 100) showLoader('transcribe');
    }
  };

  xhr.onload = () => {
    hideLoader();
    document.getElementById('progressWrap').classList.add('hidden');

    let res;
    try { res = JSON.parse(xhr.responseText); }
    catch { toast('Unexpected server response.', 'error'); return; }

    if (xhr.status !== 200 || res.error) {
      toast(res.error || 'Upload failed. Please try again.', 'error');
      return;
    }

    currentTranscript = res.transcript;
    document.getElementById('transcriptArea').value = res.transcript;
    document.getElementById('durationBadge').textContent =
      res.duration > 0 ? `${res.duration} min` : 'Unknown duration';
    document.getElementById('filenameBadge').textContent = res.filename;
    document.getElementById('wordCountBadge').textContent =
      res.transcript.split(/\s+/).filter(Boolean).length + ' words';
    document.getElementById('resultSection').classList.remove('hidden');
    document.getElementById('resultSection').scrollIntoView({ behavior: 'smooth' });
    toast('Transcription complete!', 'success');
  };

  xhr.onerror = () => {
    hideLoader();
    document.getElementById('progressWrap').classList.add('hidden');
    toast('Network error. Check your connection and try again.', 'error');
  };

  xhr.send(data);
}

// ── Summarize ──────────────────────────────────────────────────────
function summarizeText() {
  const text = document.getElementById('transcriptArea').value.trim();
  if (!text) { toast('Transcript is empty — nothing to summarize.', 'error'); return; }

  showLoader('summarize');
  document.getElementById('summarySection').classList.add('hidden');

  fetch('/summarize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  .then(r => r.json())
  .then(res => {
    hideLoader();
    if (res.error) { toast(res.error, 'error'); return; }
    currentSummary = res.summary;
    document.getElementById('summaryArea').value = res.summary;
    document.getElementById('summarySection').classList.remove('hidden');
    document.getElementById('summarySection').scrollIntoView({ behavior: 'smooth' });
    toast('Summary ready!', 'success');
  })
  .catch(() => {
    hideLoader();
    toast('Summarization failed. Please try again.', 'error');
  });
}

// ── Downloads ──────────────────────────────────────────────────────
function downloadText(text, filename) {
  if (!text.trim()) { toast('Nothing to download yet.', 'error'); return; }
  const blob = new Blob([text], { type: 'text/plain' });
  const a    = document.createElement('a');
  a.href     = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function downloadTranscript() { downloadText(document.getElementById('transcriptArea').value, 'transcript.txt'); }
function downloadSummary()    { downloadText(document.getElementById('summaryArea').value,    'summary.txt');    }

// ── Copy to clipboard ──────────────────────────────────────────────
function copyToClipboard(id) {
  const el = document.getElementById(id);
  navigator.clipboard.writeText(el.value).then(() => toast('Copied to clipboard!', 'success'));
}

// ── File drag & drop ──────────────────────────────────────────────
function initDragDrop() {
  const zone = document.getElementById('dropZone');
  if (!zone) return;

  ['dragenter', 'dragover'].forEach(ev =>
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('drag-over'); })
  );
  ['dragleave', 'drop'].forEach(ev =>
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('drag-over'); })
  );
  zone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file) {
      document.getElementById('fileInput').files = e.dataTransfer.files;
      updateFileLabel(file);
    }
  });
}

function updateFileLabel(file) {
  const label = document.getElementById('fileLabel');
  if (label) label.textContent = file ? file.name : 'Drag & drop or click to browse';
}

// ── Word count live update ─────────────────────────────────────────
function updateWordCount() {
  const text  = document.getElementById('transcriptArea').value;
  const words = text.split(/\s+/).filter(Boolean).length;
  document.getElementById('wordCountBadge').textContent = words + ' words';
}

// ── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initDragDrop();

  const fileInput = document.getElementById('fileInput');
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) updateFileLabel(fileInput.files[0]);
    });
  }

  const ta = document.getElementById('transcriptArea');
  if (ta) ta.addEventListener('input', updateWordCount);
});
