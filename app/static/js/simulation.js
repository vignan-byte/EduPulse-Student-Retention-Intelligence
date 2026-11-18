/**
 * EduPulse Simulation & Digital Twin Script
 */

let activeBaseline = {
  "Curricular units 1st sem (enrolled)": 6.0,
  "Curricular units 1st sem (approved)": 1.0,
  "Curricular units 1st sem (grade)": 10.2,
  "Admission grade": 115.0,
  "Age at enrollment": 21,
  "Scholarship holder": 0,
  "Tuition fees up to date": 0,
  "Debtor": 1
};

let currentSimulation = null;
let scenarioCounter = 1;

document.addEventListener('DOMContentLoaded', () => {
  // Initial run with student 130
  loadDtArchetype('student_130');
});

async function loadDtArchetype(key) {
  if (key === 'student_130') {
    try {
      const res = await fetch('/api/predict/student/130');
      const data = await res.json();
      if (data.status === 'success') {
        activeBaseline = data.student;
        updateBaselineDisplay();
        resetSimSliders();
        runSimulation();
      }
    } catch (err) {
      console.error('Failed to load student 130:', err);
    }
  } else if (key) {
    try {
      const res = await fetch('/api/predict/archetypes');
      const data = await res.json();
      if (data.status === 'success' && data.archetypes[key]) {
        activeBaseline = { ...data.archetypes[key] };
        updateBaselineDisplay();
        resetSimSliders();
        runSimulation();
      }
    } catch (err) {
      console.error('Failed to load preset:', err);
    }
  }
}

function updateBaselineDisplay() {
  document.getElementById('baseEnrolledText').textContent = activeBaseline["Curricular units 1st sem (enrolled)"] || 6.0;
  document.getElementById('baseApprovedText').textContent = activeBaseline["Curricular units 1st sem (approved)"] || 0.0;
  document.getElementById('baseGradeText').textContent = (activeBaseline["Curricular units 1st sem (grade)"] || 0.0).toFixed(1) + ' / 20';
  document.getElementById('baseAdmissionText').textContent = activeBaseline["Admission grade"] || 100.0;
  
  const isDebtor = activeBaseline["Debtor"] == 1 || activeBaseline["Tuition fees up to date"] == 0;
  document.getElementById('baseTuitionText').textContent = isDebtor ? 'Arrears / Past Due' : 'Paid / Current';
  document.getElementById('baseTuitionText').style.color = isDebtor ? '#F87171' : '#34D399';
  
  document.getElementById('baseScholarshipText').textContent = activeBaseline["Scholarship holder"] == 1 ? 'Yes' : 'No';
}

function resetSimSliders() {
  const maxEnr = activeBaseline["Curricular units 1st sem (enrolled)"] || 6.0;
  const currentAppr = activeBaseline["Curricular units 1st sem (approved)"] || 1.0;
  
  const apprSlider = document.getElementById('simApprovedSlider');
  apprSlider.max = maxEnr;
  apprSlider.value = Math.min(maxEnr, Math.max(currentAppr, 4));
  document.getElementById('simApprovedVal').textContent = apprSlider.value;
  
  const gradeSlider = document.getElementById('simGradeSlider');
  gradeSlider.value = 13.5;
  document.getElementById('simGradeVal').textContent = '13.5';
  
  document.getElementById('simTuitionSelect').value = '1';
  document.getElementById('simScholarshipSelect').value = activeBaseline["Scholarship holder"] || '0';
}

function onSimulationInput() {
  const appr = document.getElementById('simApprovedSlider').value;
  const grade = document.getElementById('simGradeSlider').value;
  document.getElementById('simApprovedVal').textContent = appr;
  document.getElementById('simGradeVal').textContent = grade;
  runSimulation();
}

async function runSimulation() {
  const modified = {
    ...activeBaseline,
    "Curricular units 1st sem (approved)": parseFloat(document.getElementById('simApprovedSlider').value),
    "Curricular units 1st sem (grade)": parseFloat(document.getElementById('simGradeSlider').value),
    "Tuition fees up to date": parseInt(document.getElementById('simTuitionSelect').value, 10),
    "Debtor": parseInt(document.getElementById('simTuitionSelect').value, 10) === 1 ? 0 : 1,
    "Scholarship holder": parseInt(document.getElementById('simScholarshipSelect').value, 10)
  };
  
  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        baseline: activeBaseline,
        modified: modified
      })
    });
    const result = await res.json();
    if (result.status === 'success') {
      currentSimulation = result;
      updateSimulationUI(result);
    }
  } catch (err) {
    console.error('Simulation error:', err);
  }
}

function updateSimulationUI(data) {
  // Baseline updates
  const baseRisk = (data.baseline.dropout_probability * 100).toFixed(1);
  document.getElementById('baseRiskHeadline').textContent = `${baseRisk}%`;
  document.getElementById('baseDropoutProb').textContent = `${baseRisk}%`;
  document.getElementById('baseDropoutBar').style.width = `${baseRisk}%`;
  
  const baseBadge = document.getElementById('baseRiskBadge');
  if (data.baseline.is_screened) {
    baseBadge.className = 'badge-ep badge-danger';
    baseBadge.textContent = `AT RISK (${baseRisk}%)`;
  } else {
    baseBadge.className = 'badge-ep badge-success';
    baseBadge.textContent = `ON TRACK (${baseRisk}%)`;
  }
  
  // Simulated updates
  const simRisk = (data.simulated.dropout_probability * 100).toFixed(1);
  document.getElementById('simDropoutProb').textContent = `${simRisk}%`;
  document.getElementById('simDropoutBar').style.width = `${simRisk}%`;
  
  const simBadge = document.getElementById('simRiskBadge');
  if (data.simulated.is_screened) {
    simBadge.className = 'badge-ep badge-danger';
    simBadge.textContent = `AT RISK (${simRisk}%)`;
  } else {
    simBadge.className = 'badge-ep badge-success';
    simBadge.textContent = `ON TRACK (${simRisk}%)`;
  }
  
  // Delta update
  const delta = data.delta_risk_pp;
  const deltaElem = document.getElementById('simDeltaText');
  deltaElem.textContent = `${delta > 0 ? '+' : ''}${delta.toFixed(1)} pp`;
  deltaElem.style.color = delta < 0 ? '#34D399' : (delta > 0 ? '#F87171' : '#9CA3AF');
  
  // Recourse steps
  const recContainer = document.getElementById('recourseStepsContainer');
  recContainer.innerHTML = '';
  
  const recourse = data.recourse_recommendation;
  const feasBadge = document.getElementById('recourseFeasibilityBadge');
  feasBadge.textContent = recourse.feasibility || 'Evaluation Complete';
  feasBadge.className = recourse.feasibility === 'High' || recourse.feasibility === 'Realistic' 
    ? 'badge-ep badge-success' : 'badge-ep badge-warning';
    
  if (recourse.actionable_steps && recourse.actionable_steps.length > 0) {
    recourse.actionable_steps.forEach((step, idx) => {
      const item = document.createElement('div');
      item.style.background = 'var(--bg-input)';
      item.style.padding = '0.75rem 1rem';
      item.style.borderRadius = 'var(--radius-sm)';
      item.style.borderLeft = '3px solid var(--cyan)';
      item.innerHTML = `<strong style="color: #67E8F9; margin-right: 0.5rem;">Step ${idx + 1}:</strong> <span style="color: #fff; font-size: 0.85rem;">${step}</span>`;
      recContainer.appendChild(item);
    });
  }
}

function logCurrentScenario() {
  if (!currentSimulation) return;
  scenarioCounter++;
  const tbody = document.getElementById('scenarioHistoryBody');
  const tr = document.createElement('tr');
  
  const appr = document.getElementById('simApprovedSlider').value;
  const grade = document.getElementById('simGradeSlider').value;
  const tuition = document.getElementById('simTuitionSelect').value == '1' ? 'Paid' : 'Arrears';
  const risk = (currentSimulation.simulated.dropout_probability * 100).toFixed(1) + '%';
  const delta = `${currentSimulation.delta_risk_pp > 0 ? '+' : ''}${currentSimulation.delta_risk_pp.toFixed(1)} pp`;
  
  tr.innerHTML = `
    <td>#${scenarioCounter} (Simulated)</td>
    <td>${appr}</td>
    <td>${grade}</td>
    <td>${tuition}</td>
    <td><strong style="color: ${currentSimulation.simulated.is_screened ? '#F87171' : '#34D399'}">${risk}</strong></td>
    <td style="color: ${currentSimulation.delta_risk_pp < 0 ? '#34D399' : '#F87171'}">${delta}</td>
  `;
  tbody.prepend(tr);
}

async function downloadDossierPdf() {
  try {
    const res = await fetch('/api/reports/pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student: activeBaseline,
        case_ref: "DEMO-130",
        advisor_name: "Lead Academic Advisor"
      })
    });
    
    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "EduPulse_Student_Dossier_DEMO-130.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } else {
      alert('PDF generation error');
    }
  } catch (err) {
    alert('Failed to download PDF: ' + err);
  }
}

async function exportDossierMarkdown() {
  try {
    const res = await fetch('/api/reports/markdown', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student: activeBaseline,
        case_ref: "DEMO-130",
        advisor_name: "Lead Academic Advisor"
      })
    });
    const data = await res.json();
    if (data.status === 'success') {
      const blob = new Blob([data.markdown], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "EduPulse_Student_Dossier_DEMO-130.md";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    }
  } catch (err) {
    alert('Failed to export markdown: ' + err);
  }
}
