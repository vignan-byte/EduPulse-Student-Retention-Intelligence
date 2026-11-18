/**
 * EduPulse Prediction & Student Risk Script
 */

let currentArchetypes = {};

document.addEventListener('DOMContentLoaded', async () => {
  await fetchArchetypes();
  // Trigger initial evaluation with default values (student index 130 values)
  evaluateStudentRisk();
});

async function fetchArchetypes() {
  try {
    const res = await fetch('/api/predict/archetypes');
    const data = await res.json();
    if (data.status === 'success') {
      currentArchetypes = data.archetypes;
    }
  } catch (err) {
    console.error('Failed to load archetypes:', err);
  }
}

function loadArchetype(name) {
  if (!name || !currentArchetypes[name]) return;
  const p = currentArchetypes[name];
  
  if (p['Curricular units 1st sem (enrolled)'] !== undefined)
    document.getElementById('sem1_enrolled').value = p['Curricular units 1st sem (enrolled)'];
  if (p['Curricular units 1st sem (approved)'] !== undefined)
    document.getElementById('sem1_approved').value = p['Curricular units 1st sem (approved)'];
  if (p['Curricular units 1st sem (grade)'] !== undefined)
    document.getElementById('sem1_grade').value = p['Curricular units 1st sem (grade)'];
  if (p['Admission grade'] !== undefined)
    document.getElementById('admission_grade').value = p['Admission grade'];
  if (p['Age at enrollment'] !== undefined)
    document.getElementById('age').value = p['Age at enrollment'];
  if (p['Scholarship holder'] !== undefined)
    document.getElementById('scholarship').value = p['Scholarship holder'];
  if (p['Tuition fees up to date'] !== undefined)
    document.getElementById('fees_current').value = p['Tuition fees up to date'];
  if (p['Debtor'] !== undefined)
    document.getElementById('debtor').value = p['Debtor'];
    
  evaluateStudentRisk();
}

async function loadByIndex() {
  const idx = document.getElementById('studentIndexInput').value;
  try {
    const res = await fetch(`/api/predict/student/${idx}`);
    const data = await res.json();
    if (data.status === 'success') {
      const s = data.student;
      if (s['Curricular units 1st sem (enrolled)'] !== undefined)
        document.getElementById('sem1_enrolled').value = s['Curricular units 1st sem (enrolled)'];
      if (s['Curricular units 1st sem (approved)'] !== undefined)
        document.getElementById('sem1_approved').value = s['Curricular units 1st sem (approved)'];
      if (s['Curricular units 1st sem (grade)'] !== undefined)
        document.getElementById('sem1_grade').value = s['Curricular units 1st sem (grade)'];
      if (s['Admission grade'] !== undefined)
        document.getElementById('admission_grade').value = s['Admission grade'];
      if (s['Age at enrollment'] !== undefined)
        document.getElementById('age').value = s['Age at enrollment'];
      if (s['Scholarship holder'] !== undefined)
        document.getElementById('scholarship').value = s['Scholarship holder'];
      if (s['Tuition fees up to date'] !== undefined)
        document.getElementById('fees_current').value = s['Tuition fees up to date'];
      if (s['Debtor'] !== undefined)
        document.getElementById('debtor').value = s['Debtor'];
        
      evaluateStudentRisk();
    } else {
      alert(data.message || 'Error loading student');
    }
  } catch (err) {
    alert('Failed to fetch student record: ' + err);
  }
}

function getFormData() {
  return {
    "Curricular units 1st sem (enrolled)": parseFloat(document.getElementById('sem1_enrolled').value),
    "Curricular units 1st sem (approved)": parseFloat(document.getElementById('sem1_approved').value),
    "Curricular units 1st sem (grade)": parseFloat(document.getElementById('sem1_grade').value),
    "Admission grade": parseFloat(document.getElementById('admission_grade').value),
    "Age at enrollment": parseInt(document.getElementById('age').value, 10),
    "Scholarship holder": parseInt(document.getElementById('scholarship').value, 10),
    "Tuition fees up to date": parseInt(document.getElementById('fees_current').value, 10),
    "Debtor": parseInt(document.getElementById('debtor').value, 10)
  };
}

async function evaluateStudentRisk(e) {
  if (e) e.preventDefault();
  const student = getFormData();
  
  try {
    const res = await fetch('/api/predict/single', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student: student })
    });
    const data = await res.json();
    
    if (data.status === 'success') {
      updateAssessmentUI(data);
    } else {
      alert('Error during prediction: ' + data.message);
    }
  } catch (err) {
    console.error('Prediction API error:', err);
  }
}

function updateAssessmentUI(data) {
  const pDrop = (data.probabilities.Dropout * 100).toFixed(1);
  const pEnr = (data.probabilities.Enrolled * 100).toFixed(1);
  const pGrad = (data.probabilities.Graduate * 100).toFixed(1);
  
  // Update progress bars
  document.getElementById('probDropoutText').textContent = `${pDrop}%`;
  document.getElementById('probDropoutBar').style.width = `${pDrop}%`;
  
  document.getElementById('probEnrolledText').textContent = `${pEnr}%`;
  document.getElementById('probEnrolledBar').style.width = `${pEnr}%`;
  
  document.getElementById('probGradText').textContent = `${pGrad}%`;
  document.getElementById('probGradBar').style.width = `${pGrad}%`;
  
  // Update Badge and Banner
  const riskBadge = document.getElementById('riskBadge');
  const riskBanner = document.getElementById('riskBanner');
  const bannerTitle = document.getElementById('bannerTitle');
  const bannerText = document.getElementById('bannerText');
  
  if (data.is_screened) {
    riskBadge.className = 'badge-ep badge-danger';
    riskBadge.textContent = 'CRITICAL / ADVISOR REVIEW';
    riskBanner.className = 'alert-ep alert-ep-warning';
    bannerTitle.textContent = `Dropout Risk (${pDrop}%) Exceeds Screening Threshold (${(data.screening_threshold * 100).toFixed(0)}%)`;
    bannerText.textContent = 'Student prioritized for active academic & financial advising review.';
  } else if (data.dropout_probability >= 0.30) {
    riskBadge.className = 'badge-ep badge-warning';
    riskBadge.textContent = 'MODERATE WATCH';
    riskBanner.className = 'alert-ep alert-ep-info';
    bannerTitle.textContent = `Moderate Risk Level (${pDrop}%) Below Immediate Review Threshold`;
    bannerText.textContent = 'Continue routine term-to-term monitoring; offer optional tutoring check-in.';
  } else {
    riskBadge.className = 'badge-ep badge-success';
    riskBadge.textContent = 'ROUTINE SUPPORT / ON TRACK';
    riskBanner.className = 'alert-ep alert-ep-info';
    bannerTitle.textContent = `Low Risk Profile (${pDrop}%) — Student On Track`;
    bannerText.textContent = 'Academic indicators meet retention targets. Standard advising schedule.';
  }
  
  // Render Recommendations
  const recContainer = document.getElementById('recommendationsList');
  recContainer.innerHTML = '';
  
  if (data.recommendations && data.recommendations.length > 0) {
    data.recommendations.forEach(r => {
      const card = document.createElement('div');
      card.style.background = 'var(--bg-input)';
      card.style.padding = '0.75rem';
      card.style.borderRadius = 'var(--radius-sm)';
      card.style.borderLeft = r.priority.includes('Critical') ? '3px solid var(--danger)' : '3px solid var(--info)';
      
      card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem;">
          <strong style="color: #fff; font-size: 0.8rem;">${r.category}</strong>
          <span style="font-size: 0.72rem; color: ${r.priority.includes('Critical') ? '#F87171' : '#34D399'}; font-weight: 600;">${r.priority}</span>
        </div>
        <p style="font-size: 0.76rem; color: var(--text-secondary); margin: 0 0 0.2rem 0;">${r.action}</p>
        <span style="font-size: 0.7rem; color: var(--text-muted);"><i class="bi bi-geo-alt"></i> ${r.referral_channel}</span>
      `;
      recContainer.appendChild(card);
    });
  }
}

async function handleCohortUpload(e) {
  e.preventDefault();
  const fileInput = document.getElementById('cohortFileInput');
  const threshold = document.getElementById('cohortThreshold').value;
  
  if (!fileInput.files.length) return;
  
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  formData.append('threshold', threshold);
  
  try {
    const res = await fetch('/api/predict/cohort', {
      method: 'POST',
      body: formData
    });
    const result = await res.json();
    if (res.ok && result.status === 'success') {
      const d = result.data;
      document.getElementById('cohortPlaceholder').style.display = 'none';
      document.getElementById('cohortSummaryArea').style.display = 'block';
      
      document.getElementById('cohortTotalScreened').textContent = d.total_records.toLocaleString();
      document.getElementById('cohortFlaggedCount').textContent = `${d.flagged_count} (${d.flagged_percentage}%)`;
      document.getElementById('cohortAvgRisk').textContent = `${(d.average_risk * 100).toFixed(1)}%`;
      
      const tbody = document.getElementById('cohortTableBody');
      tbody.innerHTML = '';
      
      d.results_sample.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>#${r.row}</td>
          <td><strong style="color: ${r.dropout_probability >= d.screening_threshold ? '#F87171' : '#34D399'}">${(r.dropout_probability * 100).toFixed(1)}%</strong></td>
          <td>${r.top_predicted_outcome}</td>
          <td>${(r.top_class_confidence * 100).toFixed(1)}%</td>
          <td><span class="badge-ep ${r.review_priority === 'Advisor review' ? 'badge-danger' : 'badge-success'}">${r.review_priority}</span></td>
        `;
        tbody.appendChild(tr);
      });
    } else {
      alert(result.message || 'Cohort screening failed');
    }
  } catch (err) {
    alert('Upload failed: ' + err);
  }
}
