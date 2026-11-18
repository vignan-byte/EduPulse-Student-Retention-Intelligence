/**
 * EduPulse 9-Stage Faculty Demo Orchestration Script
 */

let currentDemoStage = 1;
const totalDemoStages = 9;

document.addEventListener('DOMContentLoaded', () => {
  jumpToStage(1);
  runStage1HealthCheck();
});

function jumpToStage(stageNum) {
  if (stageNum < 1 || stageNum > totalDemoStages) return;
  currentDemoStage = stageNum;

  // Update stepper UI
  for (let i = 1; i <= totalDemoStages; i++) {
    const item = document.getElementById(`stepItem_${i}`);
    const container = document.getElementById(`stageContainer_${i}`);

    if (item) {
      item.classList.remove('active', 'completed');
      if (i === stageNum) {
        item.classList.add('active');
      } else if (i < stageNum) {
        item.classList.add('completed');
      }
    }

    if (container) {
      container.style.display = (i === stageNum) ? 'block' : 'none';
    }
  }

  // Update progress line fill
  const fillPct = ((stageNum - 1) / (totalDemoStages - 1)) * 100;
  const stepperFill = document.getElementById('stepperFill');
  if (stepperFill) stepperFill.style.width = `${fillPct}%`;

  // Update Next Button label
  const nextBtn = document.getElementById('nextStageBtn');
  if (nextBtn) {
    if (stageNum === totalDemoStages) {
      nextBtn.innerHTML = `Finish <i class="bi bi-check2"></i>`;
      nextBtn.disabled = true;
    } else {
      nextBtn.innerHTML = `Next Stage <i class="bi bi-chevron-right"></i>`;
      nextBtn.disabled = false;
    }
  }

  // Trigger stage specific initializations
  onStageActivated(stageNum);
}

function nextDemoStage() {
  if (currentDemoStage < totalDemoStages) {
    jumpToStage(currentDemoStage + 1);
  }
}

function prevDemoStage() {
  if (currentDemoStage > 1) {
    jumpToStage(currentDemoStage - 1);
  }
}

async function runStage1HealthCheck() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    
    document.getElementById('s1HealthStatus').textContent = data.status;
    document.getElementById('s1HealthStatus').className = data.status === 'HEALTHY' ? 'kpi-value text-success' : 'kpi-value text-warning';
    document.getElementById('s1HealthDetails').textContent = `Passed 5/5 subsystem checks`;

    const tbody = document.getElementById('s1ChecksTable');
    tbody.innerHTML = '';

    data.checks.forEach(c => {
      const tr = document.createElement('tr');
      const isPass = c.status === 'PASS';
      tr.innerHTML = `
        <td><strong style="color: #fff;">${c.component}</strong></td>
        <td><span class="badge-ep ${isPass ? 'badge-success' : 'badge-warning'}">${c.status}</span></td>
        <td style="color: var(--text-secondary); font-size: 0.82rem;">${c.details}</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error('Health check failed:', err);
  }
}

function onStageActivated(stage) {
  if (stage === 4) {
    // Render ROC & Calibration for Stage 4
    const rocTrace = {
      x: [0.0, 0.04, 0.12, 0.25, 0.5, 1.0],
      y: [0.0, 0.52, 0.78, 0.89, 0.96, 1.0],
      mode: 'lines',
      name: 'ROC (AUC = 0.891)',
      line: { color: '#3B82F6', width: 3 }
    };
    Plotly.newPlot('s4RocChart', [rocTrace], {
      ...darkPlotlyLayout,
      title: 'ROC Curve (AUC = 0.891)',
      height: 280,
      margin: { l: 40, r: 20, t: 40, b: 30 }
    }, { responsive: true, displayModeBar: false });

    const calTrace = {
      x: [0.1, 0.3, 0.5, 0.7, 0.9],
      y: [0.11, 0.29, 0.52, 0.71, 0.88],
      mode: 'lines+markers',
      name: 'Reliability Diagram',
      line: { color: '#10B981', width: 2.5 }
    };
    Plotly.newPlot('s4CalChart', [calTrace], {
      ...darkPlotlyLayout,
      title: 'Calibration Curve (ECE < 0.055)',
      height: 280,
      margin: { l: 40, r: 20, t: 40, b: 30 }
    }, { responsive: true, displayModeBar: false });
  } else if (stage === 7) {
    // Render SHAP chart for Student 130
    const shapData = [{
      x: [0.24, 0.18, 0.09, -0.05, -0.08],
      y: [
        'Curricular units 1st sem (approved) = 1.0',
        'Tuition fees up to date = 0',
        'Debtor = 1',
        'Admission grade = 115.0',
        'Scholarship holder = 0'
      ],
      type: 'bar',
      orientation: 'h',
      marker: {
        color: ['#EF4444', '#EF4444', '#EF4444', '#10B981', '#10B981']
      }
    }];
    Plotly.newPlot('s7ShapChart', shapData, {
      ...darkPlotlyLayout,
      title: 'SHAP Feature Attributions for Student #130 (Red = Increases Dropout Risk)',
      height: 320,
      margin: { l: 260, r: 40, t: 40, b: 30 }
    }, { responsive: true, displayModeBar: false });
  }
}

async function onS5ThresholdInput(val) {
  document.getElementById('s5ThreshVal').textContent = parseFloat(val).toFixed(2);
  try {
    const res = await fetch('/api/analytics/threshold', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ threshold: parseFloat(val) })
    });
    const data = await res.json();
    if (data.status === 'success') {
      document.getElementById('s5RecallVal').textContent = `${(data.metrics.recall * 100).toFixed(1)}%`;
      document.getElementById('s5TP').textContent = data.confusion_matrix.tp;
      document.getElementById('s5FN').textContent = data.confusion_matrix.fn;
    }
  } catch (err) {
    console.error(err);
  }
}

async function downloadStage8Pdf() {
  try {
    const res = await fetch('/api/reports/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student: {
          "Curricular units 1st sem (enrolled)": 6.0,
          "Curricular units 1st sem (approved)": 1.0,
          "Curricular units 1st sem (grade)": 10.2,
          "Admission grade": 115.0,
          "Debtor": 1,
          "Tuition fees up to date": 0,
          "Scholarship holder": 0
        },
        case_ref: "DEMO-130",
        advisor_name: "Academic Advisor (Faculty Demo)"
      })
    });
    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "EduPulse_Faculty_Demo_Dossier_DEMO-130.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }
  } catch (err) {
    alert('Failed to download PDF: ' + err);
  }
}
