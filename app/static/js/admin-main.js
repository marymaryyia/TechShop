// Admin Panel Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('adminSidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.add('open');
      overlay.classList.add('show');
    });
  }
  
  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('show');
    });
  }
  
  // Theme toggle
  const themeToggle = document.getElementById('adminThemeToggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      document.documentElement.setAttribute('data-bs-theme', next);
      localStorage.setItem('theme', next);
    });
  }
  
  // Auto-hide toasts
  document.querySelectorAll('.toast').forEach(toast => {
    setTimeout(() => toast.remove(), 5000);
  });
});

// Toast notification
function showToast(title, message, type) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const iconMap = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill'
  };
  
  toast.innerHTML = `
    <i class="bi ${iconMap[type] || 'bi-info-circle'}"></i>
    <div>
      <div style="font-weight:600;font-size:0.85rem;">${title}</div>
      <div style="font-size:0.8rem;color:var(--text-muted);">${message}</div>
    </div>
  `;
  
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);
}