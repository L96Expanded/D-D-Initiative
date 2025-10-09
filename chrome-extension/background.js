// Background script for D&D Initiative Tracker Extension
// This handles background tasks and extension lifecycle

chrome.runtime.onInstalled.addListener(() => {
  console.log('D&D Initiative Tracker Extension installed');
});

// Handle clicks on the extension icon
chrome.action.onClicked.addListener((tab) => {
  // This won't fire when popup is set, but kept for completeness
  chrome.tabs.create({ url: 'http://localhost:3000' });
});

// Optional: Add context menu items (only if permission is granted)
chrome.runtime.onInstalled.addListener(() => {
  if (chrome.contextMenus) {
    chrome.contextMenus.create({
      id: 'openDnDApp',
      title: 'Open D&D Initiative Tracker',
      contexts: ['page']
    });
    
    chrome.contextMenus.create({
      id: 'createEncounter',
      title: 'Create New Encounter',
      contexts: ['page']
    });
  }
});

// Handle context menu clicks (only if available)
if (chrome.contextMenus) {
  chrome.contextMenus.onClicked.addListener((info, tab) => {
    switch (info.menuItemId) {
      case 'openDnDApp':
        chrome.tabs.create({ url: 'http://localhost:3000' });
        break;
      case 'createEncounter':
        chrome.tabs.create({ url: 'http://localhost:3000/encounters' });
        break;
    }
  });
}

// Optional: Handle extension updates
chrome.runtime.onStartup.addListener(() => {
  console.log('D&D Initiative Tracker Extension started');
});