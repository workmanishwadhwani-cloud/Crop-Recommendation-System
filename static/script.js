// ────── Form Submission ──────
const form = document.getElementById('cropForm');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoading = submitBtn.querySelector('.btn-loading');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const errorBox = document.getElementById('errorBox');
const errorMessage = document.getElementById('errorMessage');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  setLoading(true);
  hideError();
  resultsSection.style.display = 'none';

  const payload = {
    Nitrogen: document.getElementById('Nitrogen').value,
    Phosporus: document.getElementById('Phosporus').value,
    Potassium: document.getElementById('Potassium').value,
    Temperature: document.getElementById('Temperature').value,
    Humidity: document.getElementById('Humidity').value,
    Ph: document.getElementById('Ph').value,
    Rainfall: document.getElementById('Rainfall').value,
  };

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();

    if (!res.ok || data.error) {
      showError(data.error || 'Something went wrong. Please try again.');
    } else {
      renderResults(data.recommendations);
      loadHistory();
    }
  } catch (err) {
    showError('Network error. Please check your connection and try again.');
  } finally {
    setLoading(false);
  }
});

// ────── Render Result Cards ──────
function renderResults(recs) {
  resultsGrid.innerHTML = '';

  recs.forEach((crop, i) => {
    const rankClass = ['rank-1', 'rank-2', 'rank-3'][i] || 'rank-3';
    const rankLabel = ['🥇 Best Match', '🥈 2nd Match', '🥉 3rd Match'][i] || `#${i + 1}`;
    const barWidth = Math.max(crop.confidence, 2);

    const card = document.createElement('div');
    card.className = `result-card ${rankClass}`;
    card.innerHTML = `
      <span class="result-badge">${rankLabel}</span>
      <span class="result-emoji">${crop.emoji}</span>
      <div class="result-name">${crop.name}</div>
      <div class="result-confidence-bar">
        <div class="result-confidence-fill" data-width="${barWidth}"></div>
      </div>
      <div class="result-conf-text">Confidence: <span class="conf-value">${crop.confidence}%</span></div>
      <div class="result-meta">
        <div class="meta-item"><span class="meta-icon">📅</span> ${crop.season}</div>
        <div class="meta-item"><span class="meta-icon">💧</span> Water: ${crop.water}</div>
      </div>
      <div class="result-tip">${crop.tip}</div>
    `;
    resultsGrid.appendChild(card);

    // Animate confidence bar after DOM insert
    setTimeout(() => {
      card.querySelector('.result-confidence-fill').style.width = barWidth + '%';
    }, 100);
  });

  resultsSection.style.display = 'block';
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ────── History ──────
async function loadHistory() {
  const tbody = document.getElementById('historyBody');
  try {
    const res = await fetch('/api/history');
    const data = await res.json();

    if (!data.history || data.history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="11" class="empty-state">No predictions yet. Make your first prediction above! 🌱</td></tr>';
      return;
    }

    tbody.innerHTML = data.history.map(r => {
      const info = cropInfoMap[r.result] || { emoji: '🌱' };
      return `<tr>
        <td>${r.id}</td>
        <td><span class="crop-pill">${info.emoji} ${r.result}</span></td>
        <td class="conf-badge">${r.confidence}%</td>
        <td>${r.N}</td>
        <td>${r.P}</td>
        <td>${r.K}</td>
        <td>${r.temperature}</td>
        <td>${r.humidity}</td>
        <td>${r.ph}</td>
        <td>${r.rainfall}</td>
        <td>${r.timestamp}</td>
      </tr>`;
    }).join('');
  } catch {
    tbody.innerHTML = '<tr><td colspan="11" class="empty-state">Could not load history.</td></tr>';
  }
}

// ────── Crop emoji map for history table ──────
const cropInfoMap = {
  Rice: "🌾", Maize: "🌽", Jute: "🌿", Cotton: "🌸", Coconut: "🥥",
  Papaya: "🍈", Orange: "🍊", Apple: "🍎", Muskmelon: "🍈", Watermelon: "🍉",
  Grapes: "🍇", Mango: "🥭", Banana: "🍌", Pomegranate: "🍹", Lentil: "🫘",
  Blackgram: "🫘", Mungbean: "🫘", Mothbeans: "🫘", Pigeonpeas: "🫘",
  Kidneybeans: "🫘", Chickpea: "🫘", Coffee: "☕"
};
// Reformat so history table gets the emoji
Object.keys(cropInfoMap).forEach(k => cropInfoMap[k] = { emoji: cropInfoMap[k] });

// ────── Helpers ──────
function setLoading(state) {
  submitBtn.disabled = state;
  btnText.style.display = state ? 'none' : 'flex';
  btnLoading.style.display = state ? 'flex' : 'none';
}

function showError(msg) {
  errorMessage.textContent = msg;
  errorBox.style.display = 'flex';
  errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
  errorBox.style.display = 'none';
}

function resetForm() {
  form.reset();
  resultsSection.style.display = 'none';
  hideError();
}

function scrollToHistory() {
  document.getElementById('historySection').scrollIntoView({ behavior: 'smooth' });
}

// ────── Load history on page ready ──────
document.addEventListener('DOMContentLoaded', loadHistory);
