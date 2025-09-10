// Text Replacer Web UI JavaScript

class TextReplacerUI {
  constructor() {
    this.currentJobId = null;
    this.statusInterval = null;
    this.init();
  }

  init() {
    this.bindEvents();
    this.loadSavedSettings();
    this.initDarkMode();
  }

  bindEvents() {
    // Form submission
    document.getElementById('replacementForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.startReplacement();
    });

    // Directory validation
    document.getElementById('validateDir').addEventListener('click', () => {
      this.validateDirectory();
    });

    // Reset form
    document.getElementById('resetBtn').addEventListener('click', () => {
      this.resetForm();
    });

    // Auto-validate directory on input
    document.getElementById('directory').addEventListener('blur', () => {
      if (document.getElementById('directory').value.trim()) {
        this.validateDirectory();
      }
    });
  }

  async validateDirectory() {
    const directory = document.getElementById('directory').value.trim();
    const statusDiv = document.getElementById('directoryStatus');
    
    if (!directory) {
      statusDiv.innerHTML = '<span class="status-warning">Enter a directory path</span>';
      return;
    }

    statusDiv.innerHTML = '<span class="loading"></span> Validating...';

    try {
      const response = await fetch('/api/validate-directory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ directory })
      });

      const result = await response.json();

      if (result.valid) {
        statusDiv.innerHTML = `<span class="status-valid">✓ ${result.repo_info || 'Valid directory'}</span>`;
        this.saveSettings();
      } else {
        statusDiv.innerHTML = `<span class="status-invalid">✗ ${result.error}</span>`;
      }
    } catch (error) {
      statusDiv.innerHTML = `<span class="status-invalid">✗ Error: ${error.message}</span>`;
    }
  }

  async startReplacement() {
    const formData = new FormData(document.getElementById('replacementForm'));
    const data = {};

    // Convert form data to object
    for (let [key, value] of formData.entries()) {
      if (key === 'extensions' || key === 'excludeDirs') {
        data[key] = value ? value.split(' ').filter(s => s.trim()) : [];
      } else if (key === 'useRegex' || key === 'dryRun') {
        data[key] = true;
      } else if (key === 'maxFiles') {
        data[key] = parseInt(value) || 10000;
      } else {
        data[key] = value;
      }
    }

    // Validate required fields
    if (!data.directory || !data.search || !data.replace) {
      this.showToast('Please fill in all required fields', 'error');
      return;
    }

    try {
      // Start the job
      const response = await fetch('/api/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      const result = await response.json();
      this.currentJobId = result.job_id;

      // Show progress section
      document.getElementById('progressSection').style.display = 'block';
      document.getElementById('resultsSection').style.display = 'none';
      document.getElementById('instructionsSection').style.display = 'none';

      // Start polling for status
      this.startStatusPolling();

      this.showToast('Replacement job started!', 'success');
      this.saveSettings();

    } catch (error) {
      this.showToast(`Error starting job: ${error.message}`, 'error');
    }
  }

  startStatusPolling() {
    if (this.statusInterval) {
      clearInterval(this.statusInterval);
    }

    this.statusInterval = setInterval(async () => {
      if (!this.currentJobId) return;

      try {
        const response = await fetch(`/api/status/${this.currentJobId}`);
        const status = await response.json();

        this.updateProgress(status);

        if (status.status === 'completed' || status.status === 'failed' || status.status === 'error') {
          clearInterval(this.statusInterval);
          this.showResults(status);
        }
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 1000);
  }

  updateProgress(status) {
    const progressBar = document.getElementById('progressBar');
    const progressPercent = document.getElementById('progressPercent');
    const progressDetails = document.getElementById('progressDetails');

    const progress = status.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressPercent.textContent = `${progress}%`;
    progressDetails.textContent = status.details || status.status;

    // Update progress bar color based on status
    progressBar.className = 'progress-bar progress-bar-striped';
    if (status.status === 'completed') {
      progressBar.classList.add('bg-success');
    } else if (status.status === 'failed' || status.status === 'error') {
      progressBar.classList.add('bg-danger');
    } else {
      progressBar.classList.add('progress-bar-animated', 'bg-primary');
    }
  }

  showResults(status) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsContent = document.getElementById('resultsContent');

    resultsSection.style.display = 'block';

    if (status.status === 'completed') {
      const result = status.result;
      
      if (result.success !== undefined) {
        // Full workflow result
        resultsContent.innerHTML = `
          <div class="alert alert-success">
            <h6><i class="fas fa-check-circle"></i> Workflow Completed Successfully!</h6>
            <p class="mb-0">Text replacement, Git operations, and PR creation completed.</p>
          </div>
        `;
      } else {
        // Dry run result
        resultsContent.innerHTML = `
          <div class="alert alert-info">
            <h6><i class="fas fa-eye"></i> Dry Run Results</h6>
            <p class="mb-3">Preview of changes that would be made:</p>
            <div class="row">
              <div class="col-md-4">
                <div class="card">
                  <div class="card-body text-center">
                    <h3 class="text-primary">${result.files_processed || 0}</h3>
                    <p class="mb-0">Files Processed</p>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card">
                  <div class="card-body text-center">
                    <h3 class="text-success">${result.files_changed || 0}</h3>
                    <p class="mb-0">Files Changed</p>
                  </div>
                </div>
              </div>
              <div class="col-md-4">
                <div class="card">
                  <div class="card-body text-center">
                    <h3 class="text-warning">${result.total_replacements || 0}</h3>
                    <p class="mb-0">Total Replacements</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
      }
    } else if (status.status === 'failed') {
      resultsContent.innerHTML = `
        <div class="alert alert-danger">
          <h6><i class="fas fa-exclamation-triangle"></i> Job Failed</h6>
          <p class="mb-0">The text replacement job failed. Please check the directory and try again.</p>
        </div>
      `;
    } else if (status.status === 'error') {
      resultsContent.innerHTML = `
        <div class="alert alert-danger">
          <h6><i class="fas fa-exclamation-triangle"></i> Error</h6>
          <p class="mb-0">${status.error || 'An error occurred during processing.'}</p>
        </div>
      `;
    }
  }

  showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastBody = document.getElementById('toastBody');
    
    toastBody.textContent = message;
    
    // Update toast styling based on type
    const toastHeader = toast.querySelector('.toast-header');
    const icon = toastHeader.querySelector('i');
    
    icon.className = `fas me-2`;
    if (type === 'success') {
      icon.classList.add('fa-check-circle', 'text-success');
    } else if (type === 'error') {
      icon.classList.add('fa-exclamation-triangle', 'text-danger');
    } else {
      icon.classList.add('fa-bell', 'text-primary');
    }

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
  }

  resetForm() {
    document.getElementById('replacementForm').reset();
    document.getElementById('directoryStatus').innerHTML = '';
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('instructionsSection').style.display = 'block';
    
    if (this.statusInterval) {
      clearInterval(this.statusInterval);
    }
    
    this.currentJobId = null;
    this.showToast('Form reset successfully', 'info');
  }

  saveSettings() {
    const formData = new FormData(document.getElementById('replacementForm'));
    const settings = {};
    
    for (let [key, value] of formData.entries()) {
      if (key !== 'githubToken') { // Don't save sensitive data
        settings[key] = value;
      }
    }
    
    localStorage.setItem('textReplacerSettings', JSON.stringify(settings));
  }

  loadSavedSettings() {
    const saved = localStorage.getItem('textReplacerSettings');
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        
        Object.keys(settings).forEach(key => {
          const element = document.getElementById(key);
          if (element) {
            if (element.type === 'checkbox') {
              element.checked = settings[key] === 'on';
            } else {
              element.value = settings[key];
            }
          }
        });
      } catch (error) {
        console.error('Error loading saved settings:', error);
      }
    }
  }

  initDarkMode() {
    // Add dark mode toggle to sidebar header
    const sidebarHeader = document.querySelector('.sidebar-header');
    const darkModeToggle = document.createElement('div');
    darkModeToggle.className = 'dark-mode-toggle mt-3';
    darkModeToggle.innerHTML = `
      <button class="btn btn-outline-secondary btn-sm" id="darkModeToggle">
        <i class="fas fa-moon"></i> Dark Mode
      </button>
    `;
    sidebarHeader.appendChild(darkModeToggle);

    // Bind dark mode toggle event
    document.getElementById('darkModeToggle').addEventListener('click', () => {
      this.toggleDarkMode();
    });

    // Load saved dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
      this.enableDarkMode();
    }
  }

  toggleDarkMode() {
    const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
    if (isDarkMode) {
      this.disableDarkMode();
    } else {
      this.enableDarkMode();
    }
  }

  enableDarkMode() {
    document.documentElement.setAttribute('data-bs-theme', 'dark');
    localStorage.setItem('darkMode', 'true');
    const toggleBtn = document.getElementById('darkModeToggle');
    toggleBtn.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    toggleBtn.classList.remove('btn-outline-secondary');
    toggleBtn.classList.add('btn-outline-warning');
  }

  disableDarkMode() {
    document.documentElement.setAttribute('data-bs-theme', 'light');
    localStorage.setItem('darkMode', 'false');
    const toggleBtn = document.getElementById('darkModeToggle');
    toggleBtn.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
    toggleBtn.classList.remove('btn-outline-warning');
    toggleBtn.classList.add('btn-outline-secondary');
  }
}

// Initialize the UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
  new TextReplacerUI();
});
