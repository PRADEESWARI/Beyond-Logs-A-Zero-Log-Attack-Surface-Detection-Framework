// static/js/dashboard.js
let gaugeChart = null;

function renderGauge(score) {
  const ctx = document.getElementById('scoreGauge').getContext('2d');
  if (gaugeChart) gaugeChart.destroy();
  gaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Threat', 'Safe'],
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: ['#ef4444', '#0ea5a4'],
        borderWidth: 0
      }]
    },
    options: {
      cutout: '70%',
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false }
      }
    }
  });
  document.getElementById('scoreLabel').innerText = score + '%';
}

function formatTimestamp(ts) {
  const d = new Date(ts * 1000);
  return d.toLocaleString();
}

async function fetchStatus() {
  try {
    const res = await fetch('/api/status');
    const j = await res.json();
    const status = j.status;
    document.getElementById('last-updated').innerText = 'Last update: ' + new Date(status.generated_at*1000).toLocaleString();

    renderGauge(status.threat_score);

    // alerts
    const alertsList = document.getElementById('alerts-list');
    alertsList.innerHTML = '';
    if (status.alerts && status.alerts.length) {
      status.alerts.forEach(a => {
        const li = document.createElement('li');
        li.innerText = a;
        alertsList.appendChild(li);
      });
    } else {
      alertsList.innerHTML = '<li>No alerts</li>';
    }

    // tiles
    document.getElementById('honeypot-count').innerText = status.counts.honeypot || 0;
    document.getElementById('absence-count').innerText = status.counts.absence || 0;
    document.getElementById('drift-count').innerText = status.counts.drift || 0;

    // recent events
    const re = document.getElementById('recent-events');
    re.innerHTML = '';
    if (j.recent_events && j.recent_events.length) {
      j.recent_events.slice().reverse().forEach(ev => {
        const li = document.createElement('li');
        li.innerText = `[${formatTimestamp(ev.ts)}] ${ev.type} - ${ev.details || ev.subtype || ''}`;
        re.appendChild(li);
      });
    } else {
      re.innerHTML = '<li>no recent events</li>';
    }

    // recommendation text
    const rec = document.getElementById('recommendations');
    if (status.threat_score >= 70) {
      rec.innerHTML = '<div class="recommend-high">High risk detected — isolate system, gather forensics, rotate credentials.</div>';
    } else if (status.threat_score >= 30) {
      rec.innerHTML = 'Medium risk — investigate configured changes and validate backups.';
    } else {
      rec.innerText = 'No immediate action required.';
    }

  } catch (e) {
    console.error('fetch error', e);
  }
}

// initial run
fetchStatus();
// poll every 4 seconds
setInterval(fetchStatus, 4000);
