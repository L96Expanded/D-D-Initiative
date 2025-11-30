
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { encountersAPI, presetsAPI } from '../utils/api';
import type { 
  EncounterSummary, 
  CreateEncounter, 
  Encounter, 
  UpdateEncounter, 
  CreateCreature,
  PresetSummary,
  CreatePreset,
  Preset,
  UpdatePreset
} from '../types';
import EncounterModal from '../components/EncounterModal';
import EditEncounterModal from '../components/EditEncounterModal';
import PresetModal from '../components/PresetModal';
import EditPresetModal from '../components/EditPresetModal';
import UsePresetModal from '../components/UsePresetModal';

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  
  // Encounters state
  const [encounters, setEncounters] = useState<EncounterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingEncounter, setEditingEncounter] = useState<Encounter | null>(null);

  // Presets state
  const [presets, setPresets] = useState<PresetSummary[]>([]);
  const [presetSearch, setPresetSearch] = useState('');
  const [showCreatePresetModal, setShowCreatePresetModal] = useState(false);
  const [showEditPresetModal, setShowEditPresetModal] = useState(false);
  const [showUsePresetModal, setShowUsePresetModal] = useState(false);
  const [editingPreset, setEditingPreset] = useState<Preset | null>(null);
  const [usingPreset, setUsingPreset] = useState<Preset | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [encountersData, presetsData] = await Promise.all([
          encountersAPI.getAll(),
          presetsAPI.getAll()
        ]);
        setEncounters(encountersData);
        setPresets(presetsData);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredEncounters = encounters.filter(e =>
    (e as EncounterSummary).name.toLowerCase().includes(search.toLowerCase())
  );

  const filteredPresets = presets.filter(p =>
    (p as PresetSummary).name.toLowerCase().includes(presetSearch.toLowerCase())
  );

  const handleCreate = () => {
    console.log('handleCreate called, setting showCreateModal to true');
    setShowCreateModal(true);
  };

  const handleCreateSubmit = async (data: CreateEncounter) => {
    setLoading(true);
    setError(null);
    try {
      const newEncounter = await encountersAPI.create(data);
      // Convert to EncounterSummary if needed
      const summary: EncounterSummary = {
        id: newEncounter.id,
        name: newEncounter.name,
        background_image: newEncounter.background_image,
        created_at: newEncounter.created_at,
        creature_count: newEncounter.creatures ? newEncounter.creatures.length : 0,
      };
      setEncounters(prev => [...prev, summary]);
      setShowCreateModal(false);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create encounter');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const encounter = await encountersAPI.getById(id);
      setEditingEncounter(encounter);
      setShowEditModal(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load encounter for editing');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSubmit = async (id: string, updateData: UpdateEncounter, creatures: CreateCreature[]) => {
    setLoading(true);
    setError(null);
    try {
      // For simplicity, we'll recreate the encounter with updated data and creatures
      // First, get the current encounter to preserve any data
      const currentEncounter = await encountersAPI.getById(id);
      
      // Delete existing encounter
      await encountersAPI.delete(id);
      
      // Create new encounter with updated data and creatures
      const newEncounterData = {
        name: updateData.name || currentEncounter.name,
        background_image: updateData.background_image || currentEncounter.background_image,
        creatures: creatures
      };
      
      const newEncounter = await encountersAPI.create(newEncounterData);
      
      // Update the encounters list with the new encounter
      setEncounters(prev => prev.map(enc => 
        enc.id === id 
          ? { 
              ...enc, 
              id: newEncounter.id, // Update with new ID
              name: newEncounter.name, 
              background_image: newEncounter.background_image,
              creature_count: newEncounter.creatures ? newEncounter.creatures.length : 0
            }
          : enc
      ));
      
      setShowEditModal(false);
      setEditingEncounter(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update encounter');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this encounter?')) return;
    try {
      await encountersAPI.delete(id);
      setEncounters((encounters: EncounterSummary[]) => encounters.filter((e: EncounterSummary) => e.id !== id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete encounter');
    }
  };

  // Preset handlers
  const handleCreatePreset = () => {
    setShowCreatePresetModal(true);
  };

  const handleCreatePresetSubmit = async (data: CreatePreset) => {
    setLoading(true);
    setError(null);
    try {
      const newPreset = await presetsAPI.create(data);
      const summary: PresetSummary = {
        id: newPreset.id,
        name: newPreset.name,
        description: newPreset.description,
        background_image: newPreset.background_image,
        created_at: newPreset.created_at,
        creature_count: newPreset.creatures ? newPreset.creatures.length : 0,
      };
      setPresets(prev => [...prev, summary]);
      setShowCreatePresetModal(false);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create preset');
    } finally {
      setLoading(false);
    }
  };

  const handleEditPreset = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const preset = await presetsAPI.getById(id);
      setEditingPreset(preset);
      setShowEditPresetModal(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load preset for editing');
    } finally {
      setLoading(false);
    }
  };

  const handleEditPresetSubmit = async (id: string, updateData: UpdatePreset) => {
    setLoading(true);
    setError(null);
    try {
      // Update preset with creatures included in updateData
      const updatedPreset = await presetsAPI.update(id, updateData);
      
      // Update the presets list with the updated data
      setPresets(prev => prev.map(preset => 
        preset.id === id 
          ? { 
              ...preset,
              name: updatedPreset.name,
              description: updatedPreset.description,
              background_image: updatedPreset.background_image,
              creature_count: updatedPreset.creatures ? updatedPreset.creatures.length : 0
            }
          : preset
      ));
      
      setShowEditPresetModal(false);
      setEditingPreset(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update preset');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePreset = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this preset?')) return;
    try {
      await presetsAPI.delete(id);
      setPresets(presets => presets.filter(p => p.id !== id));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete preset');
    }
  };

  const handleUsePreset = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const preset = await presetsAPI.getById(id);
      setUsingPreset(preset);
      setShowUsePresetModal(true);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to load preset');
    } finally {
      setLoading(false);
    }
  };

  const handleUsePresetSubmit = async (data: CreateEncounter) => {
    setLoading(true);
    setError(null);
    try {
      const newEncounter = await encountersAPI.create(data);
      const summary: EncounterSummary = {
        id: newEncounter.id,
        name: newEncounter.name,
        background_image: newEncounter.background_image,
        created_at: newEncounter.created_at,
        creature_count: newEncounter.creatures ? newEncounter.creatures.length : 0,
      };
      setEncounters(prev => [...prev, summary]);
      setShowUsePresetModal(false);
      setUsingPreset(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to create encounter from preset');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-4">
      <div className="container mx-auto max-w-3xl">
        <header className="glass p-6 mb-8">
          <div className="flex justify-between items-center p-8">
            <div>
              <h1 className="text-2xl font-bold">D&D Initiative Tracker</h1>
              <p className="text-gray-300">Welcome back, {user?.email}</p>
            </div>
            <button onClick={logout} className="btn btn-secondary btn-sm">
              Logout
            </button>
          </div>
        </header>

        <main>
          <div className="glass p-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
              <h2 className="text-xl font-semibold">Your Encounters</h2>
              <div className="flex gap-2 items-center">
                <input
                  type="text"
                  className="px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring focus:ring-blue-500"
                  placeholder="Search encounters..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                />
                <button className="btn btn-primary" style={{ marginLeft: '30px' }} onClick={handleCreate}>
                  Create New Encounter
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8">Loading encounters...</div>
            ) : error ? (
              <div className="text-center text-red-400 py-8">{error}</div>
            ) : filteredEncounters.length === 0 ? (
              <div className="text-center py-8 text-gray-300">No encounters found. Create your first one!</div>
            ) : (
              <ul className="space-y-4">
                {filteredEncounters.map(encounter => (
                  <li key={encounter.id} className="glass-heavy p-2 flex items-center justify-between mt-4 gap-4">
                    <div className="flex items-center gap-4 flex-1 ">
                      <h3 className="text-lg font-bold">{encounter.name}</h3>
                      <p className="text-gray-400 text-sm">Created: {new Date(encounter.created_at).toLocaleDateString()}</p>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn btn-secondary" style={{ marginRight: '15px' }} onClick={() => handleEdit(encounter.id)}>
                        Edit
                      </button>
                      <button className="btn btn-danger" style={{ marginRight: '15px' }} onClick={() => handleDelete(encounter.id)}>
                        Delete
                      </button>
                      <a href={`/encounter/${encounter.id}`} className="btn btn-success">
                        Open
                      </a>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Presets Section */}
          <div className="glass p-8 mt-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
              <h2 className="text-xl font-semibold">Your Presets</h2>
              <div className="flex gap-2 items-center">
                <input
                  type="text"
                  className="px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring focus:ring-blue-500"
                  placeholder="Search presets..."
                  value={presetSearch}
                  onChange={e => setPresetSearch(e.target.value)}
                />
                <button className="btn btn-primary" style={{ marginLeft: '30px' }} onClick={handleCreatePreset}>
                  Create New Preset
                </button>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-8">Loading presets...</div>
            ) : error ? (
              <div className="text-center text-red-400 py-8">{error}</div>
            ) : filteredPresets.length === 0 ? (
              <div className="text-center py-8 text-gray-300">No presets found. Create your first preset!</div>
            ) : (
              <ul className="space-y-4">
                {filteredPresets.map(preset => (
                  <li key={preset.id} className="glass-heavy p-2 flex items-center justify-between mt-4 gap-4">
                    <div className="flex items-center gap-4 flex-1">
                      <div>
                        <h3 className="text-lg font-bold">{preset.name}</h3>
                        {preset.description && (
                          <p className="text-gray-400 text-sm">{preset.description}</p>
                        )}
                        <p className="text-gray-400 text-xs">
                          Created: {new Date(preset.created_at).toLocaleDateString()} • {preset.creature_count} creature{preset.creature_count !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn btn-success" style={{ marginRight: '15px' }} onClick={() => handleUsePreset(preset.id)}>
                        Use
                      </button>
                      <button className="btn btn-secondary" style={{ marginRight: '15px' }} onClick={() => handleEditPreset(preset.id)}>
                        Edit
                      </button>
                      <button className="btn btn-danger" onClick={() => handleDeletePreset(preset.id)}>
                        Delete
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </main>

        {/* Create Encounter Modal */}
        {(() => {
          console.log('showCreateModal state:', showCreateModal);
          return null;
        })()}
        {showCreateModal && (
          <EncounterModal
            isOpen={showCreateModal}
            onClose={() => setShowCreateModal(false)}
            onSubmit={handleCreateSubmit}
          />
        )}

        {/* Edit Encounter Modal */}
        {showEditModal && editingEncounter && (
          <EditEncounterModal
            isOpen={showEditModal}
            onClose={() => {
              setShowEditModal(false);
              setEditingEncounter(null);
            }}
            onSubmit={handleEditSubmit}
            encounterId={editingEncounter.id}
            initialData={editingEncounter}
          />
        )}

        {/* Create Preset Modal */}
        {showCreatePresetModal && (
          <PresetModal
            isOpen={showCreatePresetModal}
            onClose={() => setShowCreatePresetModal(false)}
            onSubmit={handleCreatePresetSubmit}
          />
        )}

        {/* Edit Preset Modal */}
        {showEditPresetModal && editingPreset && (
          <EditPresetModal
            isOpen={showEditPresetModal}
            preset={editingPreset}
            onClose={() => {
              setShowEditPresetModal(false);
              setEditingPreset(null);
            }}
            onSubmit={handleEditPresetSubmit}
          />
        )}

        {/* Use Preset Modal */}
        {showUsePresetModal && usingPreset && (
          <UsePresetModal
            isOpen={showUsePresetModal}
            preset={usingPreset}
            onClose={() => {
              setShowUsePresetModal(false);
              setUsingPreset(null);
            }}
            onSubmit={handleUsePresetSubmit}
          />
        )}
      </div>
    </div>
  );
};

export default Home;