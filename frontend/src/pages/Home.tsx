
import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { encountersAPI } from '../utils/api';
import type { EncounterSummary } from '../types';

const Home: React.FC = () => {
  const { user, logout } = useAuth();
  const [encounters, setEncounters] = useState<EncounterSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

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
    // TODO: Open create encounter modal
    alert('Create Encounter modal coming soon!');
  };

  const handleEdit = (id: string) => {
    // TODO: Open edit encounter modal
    alert(`Edit Encounter ${id} modal coming soon!`);
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
          <div className="flex justify-between items-center">
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
                <button className="btn btn-primary" onClick={handleCreate}>
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
                  <li key={encounter.id} className="glass-heavy p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div>
                      <h3 className="text-lg font-bold mb-1">{encounter.name}</h3>
                      <p className="text-gray-400 text-sm mb-2">Created: {new Date(encounter.created_at).toLocaleDateString()}</p>
                      <p className="text-gray-300 text-sm">Creatures: {encounter.creature_count}</p>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn btn-secondary" onClick={() => handleEdit(encounter.id)}>
                        Edit
                      </button>
                      <button className="btn btn-danger" onClick={() => handleDelete(encounter.id)}>
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
      </div>
    </div>
  );
};

export default Home;