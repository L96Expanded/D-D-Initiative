
import * as React from 'react';
import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { encountersAPI } from '../utils/api';
import type { EncounterSummary, CreateEncounter, Encounter, UpdateEncounter, CreateCreature } from '../types';
import EncounterModal from '../components/EncounterModal';
import EditEncounterModal from '../components/EditEncounterModal';

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  const [encounters, setEncounters] = useState<EncounterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingEncounter, setEditingEncounter] = useState<Encounter | null>(null);

  useEffect(() => {
    const fetchEncounters = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await encountersAPI.getAll();
        setEncounters(data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load encounters');
      } finally {
        setLoading(false);
      }
    };
    fetchEncounters();
  }, []);

  const filteredEncounters = encounters.filter(e =>
  (e as EncounterSummary).name.toLowerCase().includes(search.toLowerCase())
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
                  <li key={encounter.id} className="glass-heavy p-4 flex items-center justify-between gap-4">
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
      </div>
    </div>
  );
};

export default Home;