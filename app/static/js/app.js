/**
 * EduPulse Global Client Application JavaScript
 * Handles global session management, modal dialogs, and common utility functions.
 */

document.addEventListener('DOMContentLoaded', () => {
  checkSessionStatus();
});

async function checkSessionStatus() {
  try {
    const res = await fetch('/api/cases/session');
    const data = await res.json();
    const authUsername = document.getElementById('authUsername');
    const authPill = document.getElementById('authPill');
    
    if (data.logged_in) {
      if (authUsername) authUsername.textContent = `${data.username} (${data.role})`;
      if (authPill) authPill.classList.add('border-primary');
      
      const form = document.getElementById('advisorLoginForm');
      const sessionView = document.getElementById('advisorSessionView');
      const userDisplay = document.getElementById('sessionUserDisplay');
      const roleDisplay = document.getElementById('sessionRoleDisplay');
      
      if (form) form.style.display = 'none';
      if (sessionView) sessionView.style.display = 'block';
      if (userDisplay) userDisplay.textContent = data.username;
      if (roleDisplay) roleDisplay.textContent = data.role.toUpperCase();
    } else {
      if (authUsername) authUsername.textContent = 'Advisor Sign In';
      const form = document.getElementById('advisorLoginForm');
      const sessionView = document.getElementById('advisorSessionView');
      if (form) form.style.display = 'block';
      if (sessionView) sessionView.style.display = 'none';
    }
  } catch (err) {
    console.warn('Session check failed:', err);
  }
}

function openLoginModal() {
  const modal = document.getElementById('loginModal');
  if (modal) modal.classList.add('active');
}

function closeLoginModal() {
  const modal = document.getElementById('loginModal');
  if (modal) modal.classList.remove('active');
}

async function handleAdvisorLogin(e) {
  e.preventDefault();
  const usernameInput = document.getElementById('modalUsername');
  const passwordInput = document.getElementById('modalPassword');
  const statusArea = document.getElementById('loginStatusArea');
  
  try {
    const res = await fetch('/api/cases/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: usernameInput.value,
        password: passwordInput.value
      })
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      statusArea.className = 'alert-ep alert-ep-info';
      statusArea.textContent = data.message;
      statusArea.style.display = 'block';
      setTimeout(() => {
        closeLoginModal();
        checkSessionStatus();
        if (window.onAdvisorLoginSuccess) window.onAdvisorLoginSuccess();
      }, 800);
    } else {
      statusArea.className = 'alert-ep alert-ep-warning';
      statusArea.textContent = data.message || 'Login failed';
      statusArea.style.display = 'block';
    }
  } catch (err) {
    statusArea.className = 'alert-ep alert-ep-warning';
    statusArea.textContent = 'Network or server error during sign in';
    statusArea.style.display = 'block';
  }
}

async function handleAdvisorLogout() {
  try {
    await fetch('/api/cases/logout', { method: 'POST' });
    closeLoginModal();
    checkSessionStatus();
    if (window.onAdvisorLogoutSuccess) window.onAdvisorLogoutSuccess();
  } catch (err) {
    console.error('Logout error:', err);
  }
}

// Global Plotly dark theme template helper
const darkPlotlyLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, sans-serif', color: '#9CA3AF' },
  margin: { l: 40, r: 20, t: 40, b: 40 },
  xaxis: {
    gridcolor: '#1F293D',
    zerolinecolor: '#374151',
    tickfont: { color: '#9CA3AF' }
  },
  yaxis: {
    gridcolor: '#1F293D',
    zerolinecolor: '#374151',
    tickfont: { color: '#9CA3AF' }
  }
};
