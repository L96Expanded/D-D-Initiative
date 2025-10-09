class DnDExtension {
  constructor() {
    this.baseURL = 'http://localhost:8000';
    this.frontendURL = 'http://localhost:3000';
    this.token = null;
    this.user = null;
    this.selectedPreset = null;
    this.currentCreatures = [];
    this.editingCreatureIndex = null;
    this.init();
  }

  async init() {
    // Load saved token and user info
    const result = await chrome.storage.local.get(['authToken', 'userInfo']);
    if (result.authToken) {
      this.token = result.authToken;
      this.user = result.userInfo;
      await this.validateToken();
    } else {
      this.showLogin();
    }

    this.setupEventListeners();
    this.checkServerStatus();
  }

  async checkServerStatus() {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    try {
      const response = await fetch(`${this.baseURL}/docs`, { 
        method: 'HEAD',
        signal: AbortSignal.timeout(3000)
      });
      
      if (response.ok) {
        statusDot.classList.add('online');
        statusText.textContent = 'Server online';
      } else {
        statusText.textContent = 'Server error';
      }
    } catch (error) {
      statusText.textContent = 'Server offline';
    }
  }

  setupEventListeners() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleLogin();
    });

    // Navigation buttons
    document.getElementById('openApp').addEventListener('click', () => {
      this.openTab(this.frontendURL);
    });

    document.getElementById('openFullApp').addEventListener('click', () => {
      this.openTab(this.frontendURL);
    });

    document.getElementById('createEncounter').addEventListener('click', () => {
      this.showCreateEncounter();
    });

    document.getElementById('logout').addEventListener('click', () => {
      this.handleLogout();
    });

    document.getElementById('refreshData').addEventListener('click', () => {
      this.loadDashboardData();
    });

    // Create encounter form and creature management
    document.getElementById('createEncounterForm').addEventListener('submit', (e) => {
      e.preventDefault();
      this.handleCreateEncounter();
    });

    document.getElementById('cancelCreate').addEventListener('click', () => {
      this.showDashboard();
    });

    document.getElementById('addCreatureBtn').addEventListener('click', () => {
      this.showAddCreatureForm();
    });

    document.getElementById('saveCreatureBtn').addEventListener('click', () => {
      this.handleSaveCreature();
    });

    document.getElementById('cancelCreatureBtn').addEventListener('click', () => {
      this.hideAddCreatureForm();
    });

    // Event delegation for dynamically created buttons
    document.addEventListener('click', (e) => {
      const action = e.target.getAttribute('data-action');
      const id = e.target.getAttribute('data-id');
      const index = e.target.getAttribute('data-index');
      
      if (action === 'open-encounter' && id) {
        this.openEncounter(id);
      } else if (action === 'use-preset' && id) {
        this.usePreset(id);
      } else if (action === 'edit-creature' && index !== null) {
        this.editCreature(parseInt(index));
      } else if (action === 'delete-creature' && index !== null) {
        this.deleteCreature(parseInt(index));
      }
    });
  }

  openTab(url) {
    chrome.tabs.create({ url });
    window.close(); // Close the popup
  }

  async handleLogin() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');
    const loginBtn = document.getElementById('loginBtn');

    // Reset error state
    errorDiv.classList.add('hidden');
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';

    try {
      // Send JSON data (not form data) to match the backend API
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password
        }),
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.access_token;
        
        // Get user info
        await this.fetchUserInfo();
        
        // Save token and user info
        await chrome.storage.local.set({ 
          authToken: this.token,
          userInfo: this.user
        });
        
        this.showDashboard();
      } else {
        let errorMessage = 'Invalid email or password';
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (typeof errorData === 'string') {
            errorMessage = errorData;
          }
        } catch (parseError) {
          console.error('Error parsing response:', parseError);
          errorMessage = `Login failed (Status: ${response.status})`;
        }
        errorDiv.textContent = errorMessage;
        errorDiv.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Login error:', error);
      errorDiv.textContent = 'Could not connect to server. Is the D&D app running?';
      errorDiv.classList.remove('hidden');
    } finally {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Login';
    }
  }

  async fetchUserInfo() {
    try {
      const response = await fetch(`${this.baseURL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        this.user = await response.json();
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  }

  async validateToken() {
    try {
      const response = await fetch(`${this.baseURL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        this.user = await response.json();
        this.showDashboard();
      } else {
        this.showLogin();
      }
    } catch (error) {
      this.showLogin();
    }
  }

  async handleLogout() {
    this.token = null;
    this.user = null;
    await chrome.storage.local.remove(['authToken', 'userInfo']);
    this.showLogin();
  }

  showLogin() {
    document.getElementById('loginSection').classList.add('active');
    document.getElementById('dashboardSection').classList.remove('active');
    document.getElementById('createEncounterSection').classList.remove('active');
  }

  showDashboard() {
    document.getElementById('loginSection').classList.remove('active');
    document.getElementById('dashboardSection').classList.add('active');
    document.getElementById('createEncounterSection').classList.remove('active');
    
    // Update user info
    if (this.user) {
      document.getElementById('userEmail').textContent = this.user.email;
    }
    
    this.loadDashboardData();
  }

  async loadDashboardData() {
    await Promise.all([
      this.loadEncounters(),
      this.loadPresets()
    ]);
  }

  async loadEncounters() {
    const container = document.getElementById('encountersList');
    
    try {
      const response = await fetch(`${this.baseURL}/encounters/`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        const encounters = await response.json();
        
        if (encounters.length === 0) {
          container.innerHTML = '<div class="empty">No encounters yet. Create one to get started!</div>';
          return;
        }

        container.innerHTML = encounters.slice(0, 4).map(encounter => `
          <div class="item">
            <div class="item-content">
              <div class="item-name">${this.escapeHtml(encounter.name)}</div>
              <div class="item-meta">${encounter.creatures?.length || 0} creatures</div>
            </div>
            <div class="item-actions">
              <button class="btn btn-small btn-success" data-action="open-encounter" data-id="${encounter.id}">
                Open
              </button>
            </div>
          </div>
        `).join('');
      } else {
        container.innerHTML = '<div class="empty">Failed to load encounters</div>';
      }
    } catch (error) {
      container.innerHTML = '<div class="empty">Could not connect to server</div>';
    }
  }

  async loadPresets() {
    const container = document.getElementById('presetsList');
    
    // Note: This assumes you have a presets endpoint. If not, we'll show a placeholder
    try {
      // First try to fetch presets - if the endpoint doesn't exist, show placeholder
      const response = await fetch(`${this.baseURL}/presets/`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.status === 404) {
        // Presets endpoint doesn't exist yet
        container.innerHTML = '<div class="empty">Presets feature coming soon!</div>';
        return;
      }

      if (response.ok) {
        const presets = await response.json();
        
        if (presets.length === 0) {
          container.innerHTML = '<div class="empty">No presets yet. Create some for quick encounters!</div>';
          return;
        }

        container.innerHTML = presets.slice(0, 4).map(preset => `
          <div class="item">
            <div class="item-content">
              <div class="item-name">${this.escapeHtml(preset.name)}</div>
              <div class="item-meta">${preset.creatures?.length || 0} creatures</div>
            </div>
            <div class="item-actions">
              <button class="btn btn-small" data-action="use-preset" data-id="${preset.id}">
                Use
              </button>
            </div>
          </div>
        `).join('');
      } else {
        container.innerHTML = '<div class="empty">Failed to load presets</div>';
      }
    } catch (error) {
      // Assume presets aren't implemented yet
      container.innerHTML = '<div class="empty">Presets feature coming soon!</div>';
    }
  }

  openEncounter(encounterId) {
    this.openTab(`${this.frontendURL}/encounter/${encounterId}`);
  }

  async usePreset(presetId) {
    try {
      // Fetch the preset details
      const response = await fetch(`${this.baseURL}/presets/${presetId}`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        alert('Failed to load preset details');
        return;
      }

      const preset = await response.json();
      this.selectedPreset = preset;
      
      // Show the create encounter form with preset data
      this.showCreateEncounter(preset);
      
    } catch (error) {
      console.error('Error loading preset:', error);
      alert('Could not connect to server. Is the D&D app running?');
    }
  }

  showCreateEncounter(preset = null) {
    // Hide dashboard, show create form
    document.getElementById('dashboardSection').classList.remove('active');
    document.getElementById('createEncounterSection').classList.add('active');
    
    if (preset) {
      // Creating from preset
      document.getElementById('createEncounterTitle').textContent = 'Create Encounter from Preset';
      document.getElementById('basePresetInfo').style.display = 'block';
      document.getElementById('selectedPresetName').textContent = preset.name;
      document.getElementById('selectedPresetMeta').textContent = 
        `${preset.creatures?.length || 0} creatures${preset.description ? ' • ' + preset.description : ''}`;
      
      // Set default encounter name and load preset creatures
      document.getElementById('encounterName').value = `${preset.name} - Encounter`;
      this.currentCreatures = [...(preset.creatures || [])];
    } else {
      // Creating new encounter
      document.getElementById('createEncounterTitle').textContent = 'Create New Encounter';
      document.getElementById('basePresetInfo').style.display = 'none';
      document.getElementById('encounterName').value = '';
      this.currentCreatures = [];
    }
    
    // Clear any previous errors and reset forms
    document.getElementById('createError').classList.add('hidden');
    this.hideAddCreatureForm();
    this.renderCreaturesList();
  }

  renderCreaturesList() {
    const container = document.getElementById('creaturesList');
    
    if (this.currentCreatures.length === 0) {
      container.innerHTML = '<div class="empty">No creatures added yet. Click ➕ to add some!</div>';
      return;
    }

    container.innerHTML = this.currentCreatures.map((creature, index) => `
      <div class="creature-item">
        ${creature.image_url ? `<div class="creature-image"><img src="${creature.image_url}" alt="${this.escapeHtml(creature.name)}" onerror="this.style.display='none'"></div>` : ''}
        <div class="creature-info">
          <div class="creature-name">${this.escapeHtml(creature.name)}</div>
          <div class="creature-details">
            Initiative: ${creature.initiative} • 
            <span class="type-badge type-${creature.creature_type}">${creature.creature_type}</span>
          </div>
        </div>
        <div class="creature-actions">
          <button class="btn btn-small" data-action="edit-creature" data-index="${index}">✏️</button>
          <button class="btn btn-small" data-action="delete-creature" data-index="${index}">🗑️</button>
        </div>
      </div>
    `).join('');
  }

  showAddCreatureForm(creature = null, index = null) {
    document.getElementById('addCreatureForm').style.display = 'block';
    
    if (creature) {
      // Editing existing creature
      document.querySelector('#addCreatureForm h4').textContent = 'Edit Creature';
      document.getElementById('creatureName').value = creature.name;
      document.getElementById('creatureInitiative').value = creature.initiative;
      document.getElementById('creatureType').value = creature.creature_type;
      document.getElementById('creatureImageUrl').value = creature.image_url || '';
      document.getElementById('saveCreatureBtn').textContent = 'Update Creature';
      this.editingCreatureIndex = index;
    } else {
      // Adding new creature
      document.querySelector('#addCreatureForm h4').textContent = 'Add Creature';
      document.getElementById('creatureName').value = '';
      document.getElementById('creatureInitiative').value = 10;
      document.getElementById('creatureType').value = 'enemy';
      document.getElementById('creatureImageUrl').value = '';
      document.getElementById('saveCreatureBtn').textContent = 'Add Creature';
      this.editingCreatureIndex = null;
    }
  }

  hideAddCreatureForm() {
    document.getElementById('addCreatureForm').style.display = 'none';
    this.editingCreatureIndex = null;
  }

  async handleSaveCreature() {
    const name = document.getElementById('creatureName').value.trim();
    const initiative = parseInt(document.getElementById('creatureInitiative').value);
    const creature_type = document.getElementById('creatureType').value;
    const userImageUrl = document.getElementById('creatureImageUrl')?.value?.trim() || null;

    if (!name) {
      alert('Please enter a creature name');
      return;
    }

    // Create base creature object
    const creature = {
      name,
      initiative,
      creature_type,
      image_url: userImageUrl || null
    };

    // If no user image provided, try to fetch from API
    if (!userImageUrl) {
      try {
        console.log('Fetching image for creature:', name, 'type:', creature_type);
        const response = await fetch(`${this.baseURL}/api/creature-images/get_creature_image?name=${encodeURIComponent(name)}&creature_type=${encodeURIComponent(creature_type)}`);
        console.log('API response status:', response.status);

        if (response.ok) {
          const data = await response.json();
          console.log('API response data:', data);
          if (data.image_url) {
            // Convert relative URL to absolute URL for Chrome extension
            if (data.image_url.startsWith('/')) {
              creature.image_url = `${this.baseURL}${data.image_url}`;
            } else {
              creature.image_url = data.image_url;
            }
            console.log('Set creature image URL to:', creature.image_url);
          }
        } else {
          console.error('API request failed with status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
        }
      } catch (error) {
        console.error('Could not fetch creature image:', error);
        // Continue without image - not a critical error
      }
    }

    console.log('Final creature object:', creature);

    if (this.editingCreatureIndex !== null) {
      // Update existing creature
      this.currentCreatures[this.editingCreatureIndex] = creature;
      console.log('Updated creature at index', this.editingCreatureIndex);
    } else {
      // Add new creature
      this.currentCreatures.push(creature);
      console.log('Added new creature, total creatures:', this.currentCreatures.length);
    }

    console.log('All creatures:', this.currentCreatures);
    this.renderCreaturesList();
    this.hideAddCreatureForm();
  }

  editCreature(index) {
    const creature = this.currentCreatures[index];
    this.showAddCreatureForm(creature, index);
  }

  deleteCreature(index) {
    if (confirm('Remove this creature?')) {
      this.currentCreatures.splice(index, 1);
      this.renderCreaturesList();
    }
  }

  async handleCreateEncounter() {
    const encounterNameInput = document.getElementById('encounterName');
    const createBtn = document.getElementById('createEncounterBtn');
    const errorDiv = document.getElementById('createError');
    
    const encounterName = encounterNameInput.value.trim();
    
    if (!encounterName) {
      errorDiv.textContent = 'Please enter an encounter name';
      errorDiv.classList.remove('hidden');
      return;
    }

    // Reset error state
    errorDiv.classList.add('hidden');
    createBtn.disabled = true;
    createBtn.textContent = 'Creating...';

    try {
      // Create encounter
      const encounterData = {
        name: encounterName,
        background_image: this.selectedPreset?.background_image || null,
        creatures: this.currentCreatures
      };

      const createResponse = await fetch(`${this.baseURL}/encounters`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.token}`,
        },
        body: JSON.stringify(encounterData),
      });

      if (createResponse.ok) {
        const newEncounter = await createResponse.json();
        // Open the new encounter immediately and close the popup
        this.openTab(`${this.frontendURL}/encounter/${newEncounter.id}`);
      } else {
        const errorData = await createResponse.json().catch(() => ({}));
        errorDiv.textContent = errorData.detail || 'Failed to create encounter';
        errorDiv.classList.remove('hidden');
      }
    } catch (error) {
      console.error('Error creating encounter:', error);
      errorDiv.textContent = 'Could not connect to server. Is the D&D app running?';
      errorDiv.classList.remove('hidden');
    } finally {
      createBtn.disabled = false;
      createBtn.textContent = 'Create & Open';
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Initialize extension when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.dndExt = new DnDExtension();
});