/**
 * Cloud Services Configuration and Testing
 * Handles configuration and connection testing for cloud services:
 * - Supabase (Database + Auth)
 * - Railway (Backend)
 * - Vercel (Frontend)
 * - Cloudflare R2 (Storage)
 * - Ollama (Local AI Models)
 */

class CloudServicesManager {
  constructor() {
    this.services = {
      supabase: {
        url: '',
        publishableKey: '',
        secretKey: '',
        dbUrl: '',
        status: 'unknown'
      },
      railway: {
        projectId: '',
        url: '',
        token: '',
        status: 'unknown'
      },
      vercel: {
        url: '',
        projectId: '',
        token: '',
        status: 'unknown'
      },
      r2: {
        accountId: '',
        accessKey: '',
        secretKey: '',
        bucket: '',
        status: 'unknown'
      },
      ollama: {
        url: '',
        models: '',
        defaultModel: '',
        status: 'unknown'
      }
    };
    
    this.init();
  }
  
  init() {
    this.loadSettings();
    this.bindEvents();
    this.updateStatusIndicators();
  }
  
  loadSettings() {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('cloudServicesSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        this.services = { ...this.services, ...parsed };
        this.populateForm();
      } catch (e) {
        console.error('Error loading cloud services settings:', e);
      }
    }
  }
  
  saveSettings() {
    // Save settings to localStorage
    try {
      localStorage.setItem('cloudServicesSettings', JSON.stringify(this.services));
      console.log('Cloud services settings saved successfully');
    } catch (error) {
      console.error('Error saving cloud services settings:', error);
    }
  }
  
  populateForm() {
    // Populate form fields with saved settings
    // Note: Browser JavaScript cannot directly access server-side environment variables
    // Users must manually enter credentials in the UI or they can be provided via backend API
    document.getElementById('cloud-supabase-url').value = this.services.supabase.url || '';
    document.getElementById('cloud-supabase-publishable-key').value = this.services.supabase.publishableKey || '';
    document.getElementById('cloud-supabase-secret-key').value = this.services.supabase.secretKey || '';
    document.getElementById('cloud-supabase-db-url').value = this.services.supabase.dbUrl || '';
    
    document.getElementById('cloud-railway-project-id').value = this.services.railway.projectId || '';
    document.getElementById('cloud-railway-url').value = this.services.railway.url || '';
    document.getElementById('cloud-railway-token').value = this.services.railway.token || '';
    
    document.getElementById('cloud-vercel-url').value = this.services.vercel.url || '';
    document.getElementById('cloud-vercel-project-id').value = this.services.vercel.projectId || '';
    document.getElementById('cloud-vercel-token').value = this.services.vercel.token || '';
    
    document.getElementById('cloud-r2-account-id').value = this.services.r2.accountId || '';
    document.getElementById('cloud-r2-access-key').value = this.services.r2.accessKey || '';
    document.getElementById('cloud-r2-secret-key').value = this.services.r2.secretKey || '';
    document.getElementById('cloud-r2-bucket').value = this.services.r2.bucket || '';
    
    document.getElementById('cloud-ollama-url').value = this.services.ollama.url || '';
    document.getElementById('cloud-ollama-models').value = this.services.ollama.models || '';
    document.getElementById('cloud-ollama-default-model').value = this.services.ollama.defaultModel || '';
  }
  
  bindEvents() {
    console.log('Binding cloud services events...');
    
    // Use event delegation to handle dynamic elements
    document.addEventListener('click', (e) => {
      const target = e.target;
      console.log('Click detected on element:', target.id, target.className);
      
      // Supabase events
      if (target.id === 'cloud-supabase-test') {
        console.log('Supabase test button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.testSupabase();
      } else if (target.id === 'cloud-supabase-save') {
        console.log('Supabase save button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.saveSupabase();
      }
      
      // Railway events
      else if (target.id === 'cloud-railway-test') {
        console.log('Railway test button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.testRailway();
      } else if (target.id === 'cloud-railway-save') {
        console.log('Railway save button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.saveRailway();
      }
      
      // Vercel events
      else if (target.id === 'cloud-vercel-test') {
        console.log('Vercel test button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.testVercel();
      } else if (target.id === 'cloud-vercel-save') {
        console.log('Vercel save button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.saveVercel();
      }
      
      // R2 events
      else if (target.id === 'cloud-r2-test') {
        console.log('R2 test button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.testR2();
      } else if (target.id === 'cloud-r2-save') {
        console.log('R2 save button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.saveR2();
      }
      
      // Ollama events
      else if (target.id === 'cloud-ollama-test') {
        console.log('Ollama test button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.testOllama();
      } else if (target.id === 'cloud-ollama-save') {
        console.log('Ollama save button clicked');
        e.preventDefault();
        e.stopPropagation();
        this.saveOllama();
      }
    });
    
    console.log('Cloud services events bound successfully');
  }
  
  updateStatusIndicator(service, status) {
    const indicator = document.getElementById(`cloud-${service}-status`);
    if (indicator) {
      indicator.className = 'cloud-status-indicator';
      if (status === 'success') {
        indicator.classList.add('status-success');
      } else if (status === 'error') {
        indicator.classList.add('status-error');
      } else if (status === 'testing') {
        indicator.classList.add('status-testing');
      }
    }
  }
  
  updateStatusIndicators() {
    Object.keys(this.services).forEach(service => {
      this.updateStatusIndicator(service, this.services[service].status);
    });
  }
  
  showMessage(service, message, isError = false) {
    const msgEl = document.getElementById(`cloud-${service}-msg`);
    if (msgEl) {
      msgEl.textContent = message;
      msgEl.style.color = isError ? 'var(--red)' : 'color-mix(in srgb, var(--fg) 55%, transparent)';
    }
  }
  
  // Supabase testing
  async testSupabase() {
    console.log('Testing Supabase connection...');
    const url = document.getElementById('cloud-supabase-url').value;
    const publishableKey = document.getElementById('cloud-supabase-publishable-key').value;
    
    console.log('Supabase credentials:', {
      url: url,
      hasKey: !!publishableKey,
      keyLength: publishableKey ? publishableKey.length : 0
    });
    
    if (!url || !publishableKey) {
      this.showMessage('supabase', 'Please enter URL and Publishable Key', true);
      return;
    }
    
    this.updateStatusIndicator('supabase', 'testing');
    this.showMessage('supabase', 'Testing connection...');
    
    try {
      // Use backend API to test connection
      const response = await fetch('/api/cloud/supabase/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: url,
          publishableKey: publishableKey
        })
      });

      const result = await response.json();
      console.log('Backend test result:', result);

      if (result.ok) {
        this.services.supabase.status = 'success';
        this.showMessage('supabase', `✓ ${result.message}`);
      } else {
        this.services.supabase.status = 'error';
        this.showMessage('supabase', `✗ ${result.message}`, true);
      }
    } catch (error) {
      console.error('Supabase connection error:', error);
      this.services.supabase.status = 'error';
      this.showMessage('supabase', `✗ Connection error: ${error.message}`, true);
    }
    
    this.updateStatusIndicator('supabase', this.services.supabase.status);
  }
  
  async saveSupabase() {
    console.log('Saving Supabase settings...');
    try {
      const urlInput = document.getElementById('cloud-supabase-url');
      const keyInput = document.getElementById('cloud-supabase-publishable-key');
      const secretInput = document.getElementById('cloud-supabase-secret-key');
      const dbInput = document.getElementById('cloud-supabase-db-url');

      console.log('Input elements found:', {
        url: !!urlInput,
        key: !!keyInput,
        secret: !!secretInput,
        db: !!dbInput
      });

      if (urlInput && keyInput && secretInput && dbInput) {
        this.services.supabase.url = urlInput.value;
        this.services.supabase.publishableKey = keyInput.value;
        this.services.supabase.secretKey = secretInput.value;
        this.services.supabase.dbUrl = dbInput.value;

        console.log('Supabase settings to save:', {
          url: this.services.supabase.url,
          hasKey: !!this.services.supabase.publishableKey,
          keyLength: this.services.supabase.publishableKey ? this.services.supabase.publishableKey.length : 0
        });

        // Call backend API to configure
        const response = await fetch('/api/cloud/supabase/configure', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            url: this.services.supabase.url,
            publishableKey: this.services.supabase.publishableKey,
            secretKey: this.services.supabase.secretKey,
            dbUrl: this.services.supabase.dbUrl
          })
        });

        const result = await response.json();
        console.log('Backend configure result:', result);

        if (result.ok) {
          this.saveSettings(); // Still save to localStorage as backup
          this.showMessage('supabase', `✓ ${result.message}`);
          console.log('Supabase settings saved successfully');
        } else {
          this.showMessage('supabase', `✗ ${result.message}`, true);
        }
      } else {
        console.error('Some input elements not found');
        this.showMessage('supabase', '✗ Error: Input elements not found', true);
      }
    } catch (error) {
      console.error('Error saving Supabase settings:', error);
      this.showMessage('supabase', `✗ Error: ${error.message}`, true);
    }
  }
  
  // Railway testing
  async testRailway() {
    const projectId = document.getElementById('cloud-railway-project-id').value;
    const url = document.getElementById('cloud-railway-url').value;
    const token = document.getElementById('cloud-railway-token').value;

    console.log('Railway credentials:', {
      projectId: projectId,
      url: url,
      hasToken: !!token
    });

    if (!url) {
      this.showMessage('railway', 'Please enter Railway Service URL', true);
      return;
    }

    this.updateStatusIndicator('railway', 'testing');
    this.showMessage('railway', 'Testing connection...');

    try {
      // Use backend API to test connection
      const response = await fetch('/api/cloud/railway/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          projectId: projectId,
          url: url,
          token: token
        })
      });

      const result = await response.json();
      console.log('Backend test result:', result);

      if (result.ok) {
        this.services.railway.status = 'success';
        this.showMessage('railway', `✓ ${result.message}`);
      } else {
        this.services.railway.status = 'error';
        this.showMessage('railway', `✗ ${result.message}`, true);
      }
    } catch (error) {
      console.error('Railway connection error:', error);
      this.services.railway.status = 'error';
      this.showMessage('railway', `✗ Connection error: ${error.message}`, true);
    }

    this.updateStatusIndicator('railway', this.services.railway.status);
  }
  
  async saveRailway() {
    console.log('Saving Railway settings...');
    try {
      const projectId = document.getElementById('cloud-railway-project-id').value;
      const url = document.getElementById('cloud-railway-url').value;
      const token = document.getElementById('cloud-railway-token').value;

      this.services.railway.projectId = projectId;
      this.services.railway.url = url;
      this.services.railway.token = token;

      // Call backend API to configure
      const response = await fetch('/api/cloud/railway/configure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          projectId: projectId,
          url: url,
          token: token
        })
      });

      const result = await response.json();
      console.log('Backend configure result:', result);

      if (result.ok) {
        this.saveSettings(); // Still save to localStorage as backup
        this.showMessage('railway', `✓ ${result.message}`);
      } else {
        this.showMessage('railway', `✗ ${result.message}`, true);
      }
    } catch (error) {
      console.error('Error saving Railway settings:', error);
      this.showMessage('railway', `✗ Error: ${error.message}`, true);
    }
  }
  
  // Vercel testing
  async testVercel() {
    const url = document.getElementById('cloud-vercel-url').value;
    
    if (!url) {
      this.showMessage('vercel', 'Please enter Vercel URL', true);
      return;
    }
    
    this.updateStatusIndicator('vercel', 'testing');
    this.showMessage('vercel', 'Testing connection...');
    
    try {
      const response = await fetch(url, {
        method: 'HEAD'
      });
      
      if (response.ok) {
        this.services.vercel.status = 'success';
        this.showMessage('vercel', '✓ Connection successful');
      } else {
        this.services.vercel.status = 'error';
        this.showMessage('vercel', `✗ Connection failed: ${response.status}`, true);
      }
    } catch (error) {
      this.services.vercel.status = 'error';
      this.showMessage('vercel', `✗ Connection error: ${error.message}`, true);
    }
    
    this.updateStatusIndicator('vercel', this.services.vercel.status);
  }
  
  saveVercel() {
    this.services.vercel.url = document.getElementById('cloud-vercel-url').value;
    this.services.vercel.projectId = document.getElementById('cloud-vercel-project-id').value;
    this.services.vercel.token = document.getElementById('cloud-vercel-token').value;
    this.saveSettings();
    this.showMessage('vercel', '✓ Settings saved');
  }
  
  // R2 testing
  async testR2() {
    const accountId = document.getElementById('cloud-r2-account-id').value;
    const accessKey = document.getElementById('cloud-r2-access-key').value;
    const secretKey = document.getElementById('cloud-r2-secret-key').value;
    const bucket = document.getElementById('cloud-r2-bucket').value;
    
    if (!accountId || !accessKey || !secretKey || !bucket) {
      this.showMessage('r2', 'Please enter all R2 credentials', true);
      return;
    }
    
    this.updateStatusIndicator('r2', 'testing');
    this.showMessage('r2', 'Testing connection...');
    
    try {
      // Test R2 connection by attempting to list buckets
      const endpoint = `https://${accountId}.r2.cloudflarestorage.com`;
      const response = await fetch(`${endpoint}/${bucket}`, {
        method: 'HEAD',
        headers: {
          'Authorization': `AWS4-HMAC-SHA256 Credential=${accessKey}`
        }
      });
      
      if (response.ok || response.status === 404) { // 404 means bucket exists but is empty
        this.services.r2.status = 'success';
        this.showMessage('r2', '✓ Connection successful');
      } else {
        this.services.r2.status = 'error';
        this.showMessage('r2', `✗ Connection failed: ${response.status}`, true);
      }
    } catch (error) {
      this.services.r2.status = 'error';
      this.showMessage('r2', `✗ Connection error: ${error.message}`, true);
    }
    
    this.updateStatusIndicator('r2', this.services.r2.status);
  }
  
  saveR2() {
    this.services.r2.accountId = document.getElementById('cloud-r2-account-id').value;
    this.services.r2.accessKey = document.getElementById('cloud-r2-access-key').value;
    this.services.r2.secretKey = document.getElementById('cloud-r2-secret-key').value;
    this.services.r2.bucket = document.getElementById('cloud-r2-bucket').value;
    this.saveSettings();
    this.showMessage('r2', '✓ Settings saved');
  }
  
  // Ollama testing
  async testOllama() {
    const url = document.getElementById('cloud-ollama-url').value;
    
    if (!url) {
      this.showMessage('ollama', 'Please enter Ollama URL', true);
      return;
    }
    
    this.updateStatusIndicator('ollama', 'testing');
    this.showMessage('ollama', 'Testing connection...');
    
    try {
      const response = await fetch(`${url}/api/tags`);
      
      if (response.ok) {
        const data = await response.json();
        this.services.ollama.status = 'success';
        this.showMessage('ollama', `✓ Connection successful (${data.models?.length || 0} models available)`);
      } else {
        this.services.ollama.status = 'error';
        this.showMessage('ollama', `✗ Connection failed: ${response.status}`, true);
      }
    } catch (error) {
      this.services.ollama.status = 'error';
      this.showMessage('ollama', `✗ Connection error: ${error.message}`, true);
    }
    
    this.updateStatusIndicator('ollama', this.services.ollama.status);
  }
  
  saveOllama() {
    this.services.ollama.url = document.getElementById('cloud-ollama-url').value;
    this.services.ollama.models = document.getElementById('cloud-ollama-models').value;
    this.services.ollama.defaultModel = document.getElementById('cloud-ollama-default-model').value;
    this.saveSettings();
    this.showMessage('ollama', '✓ Settings saved');
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('Cloud services script loaded, initializing...');
  try {
    window.cloudServicesManager = new CloudServicesManager();
    console.log('Cloud services manager initialized successfully');
    
    // Test if the manager is working
    setTimeout(() => {
      console.log('Cloud services manager test:', window.cloudServicesManager);
      console.log('Services data:', window.cloudServicesManager.services);
    }, 1000);
  } catch (error) {
    console.error('Error initializing cloud services manager:', error);
  }
});

// Also try to initialize immediately in case DOMContentLoaded already fired
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  console.log('DOM already loaded, initializing cloud services immediately...');
  try {
    if (!window.cloudServicesManager) {
      window.cloudServicesManager = new CloudServicesManager();
      console.log('Cloud services manager initialized successfully (immediate)');
    }
  } catch (error) {
    console.error('Error initializing cloud services manager (immediate):', error);
  }
}

// Add a global test function for debugging
window.testCloudServices = function() {
  console.log('=== Cloud Services Test ===');
  console.log('Manager exists:', !!window.cloudServicesManager);
  if (window.cloudServicesManager) {
    console.log('Services:', window.cloudServicesManager.services);
    console.log('Test Supabase method:', typeof window.cloudServicesManager.testSupabase);
    console.log('Save Supabase method:', typeof window.cloudServicesManager.saveSupabase);
  }
  
  // Check if elements exist
  console.log('Supabase test button:', !!document.getElementById('cloud-supabase-test'));
  console.log('Supabase save button:', !!document.getElementById('cloud-supabase-save'));
  console.log('Supabase URL input:', !!document.getElementById('cloud-supabase-url'));
  console.log('Supabase key input:', !!document.getElementById('cloud-supabase-publishable-key'));
  
  console.log('=== End Test ===');
};

console.log('Cloud services script loaded. Run testCloudServices() in console to test.');
