import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { encountersAPI, creaturesAPI } from '../utils/api';
import type { Encounter, Creature, CreateCreature } from '../types';
import CreatureModal from '../components/CreatureModal';

const Encounter: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [encounter, setEncounter] = useState<Encounter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatures, setCreatures] = useState<Creature[]>([]);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [showCreatureModal, setShowCreatureModal] = useState(false);
  const [editCreature, setEditCreature] = useState<Creature | null>(null);

  useEffect(() => {
    const fetchEncounter = async () => {
      setLoading(true);
      setError(null);
      try {
        if (!id) return;
        const data = await encountersAPI.getById(id);
        setEncounter(data);
        setCreatures([...data.creatures].sort((a, b) => b.initiative - a.initiative));
        setCurrentTurn(0);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load encounter');
      } finally {
        setLoading(false);
      }
    };
    fetchEncounter();
  }, [id]);

  const nextTurn = () => {
    setCurrentTurn((prev) => (creatures.length ? (prev + 1) % creatures.length : 0));
  };
  const prevTurn = () => {
    setCurrentTurn((prev) => (creatures.length ? (prev - 1 + creatures.length) % creatures.length : 0));
  };

  const handleAddCreature = async (data: CreateCreature) => {
    if (!id) return;
    try {
      const newCreature = await encountersAPI.addCreature(id, data);
      setCreatures((prev) => [...prev, newCreature].sort((a, b) => b.initiative - a.initiative));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to add creature');
    }
  };

  const handleEditCreature = async (data: CreateCreature) => {
    if (!editCreature) return;
    try {
      const updated = await creaturesAPI.update(editCreature.id, data);
      setCreatures((prev) => prev.map(c => c.id === updated.id ? updated : c).sort((a, b) => b.initiative - a.initiative));
      setEditCreature(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update creature');
    }
  };

  const handleDeleteCreature = async (id: string) => {
    if (!window.confirm('Delete this creature?')) return;
    try {
      await creaturesAPI.delete(id);
      setCreatures((prev) => prev.filter(c => c.id !== id));
      if (currentTurn >= creatures.length - 1) setCurrentTurn(0);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete creature');
    }
  };

  return (
    <div className="min-h-screen p-4">
      <div className="container mx-auto max-w-4xl">
        <header className="glass p-6 mb-8">
          <div className="flex justify-between items-center">
            <div>
              <button 
                onClick={() => navigate('/home')} 
                className="btn btn-secondary btn-sm mb-2"
              >
                ← Back to Home
              </button>
              <h1 className="text-2xl font-bold">{encounter?.name || 'Encounter'}</h1>
              <p className="text-gray-300">ID: {id}</p>
            </div>
            <button className="btn btn-primary" onClick={() => setShowCreatureModal(true)}>
              Add Creature
            </button>
          </div>
        </header>

        <main>
          <div className="glass p-8">
            <h2 className="text-xl font-semibold mb-4">Initiative Tracker</h2>
            {loading ? (
              <div className="text-center py-8">Loading...</div>
            ) : error ? (
              <div className="text-center text-red-400 py-8">{error}</div>
            ) : creatures.length === 0 ? (
              <div className="text-center py-8 text-gray-300">No creatures yet. Add one!</div>
            ) : (
              <>
                <div className="flex flex-col md:flex-row gap-8 items-center justify-center mb-8">
                  <button className="btn btn-secondary" onClick={prevTurn}>
                    Previous Turn
                  </button>
                  <div className="flex flex-col items-center">
                    <div className="mb-2 text-lg font-bold">Current Turn</div>
                    <div className="glass-heavy p-6 rounded-xl w-64 flex flex-col items-center">
                      <img
                        src={creatures[currentTurn].image_url || '/assets/default_creature.png'}
                        alt={creatures[currentTurn].name}
                        className="w-24 h-24 object-cover rounded-full mb-2 border-2 border-blue-500"
                      />
                      <div className="text-xl font-bold mb-1">{creatures[currentTurn].name}</div>
                      <div className="text-gray-300 mb-1">Initiative: {creatures[currentTurn].initiative}</div>
                      <div className="text-gray-400 text-sm mb-2">Type: {creatures[currentTurn].creature_type}</div>
                      <div className="flex gap-2">
                        <button className="btn btn-secondary btn-sm" onClick={() => { setEditCreature(creatures[currentTurn]); setShowCreatureModal(true); }}>
                          Edit
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDeleteCreature(creatures[currentTurn].id)}>
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                  <button className="btn btn-secondary" onClick={nextTurn}>
                    Next Turn
                  </button>
                </div>

                <div className="mb-8">
                  <div className="text-lg font-semibold mb-2">Turn Order</div>
                  <ul className="flex flex-wrap gap-4 justify-center">
                    {creatures.map((c, idx) => (
                      <li key={c.id} className={`glass-light p-4 rounded-lg flex flex-col items-center w-40 ${idx === currentTurn ? 'border-2 border-blue-500' : ''}`}>
                        <img
                          src={c.image_url || '/assets/default_creature.png'}
                          alt={c.name}
                          className="w-12 h-12 object-cover rounded-full mb-2"
                        />
                        <div className="font-bold">{c.name}</div>
                        <div className="text-gray-300 text-sm">Init: {c.initiative}</div>
                        <div className="text-gray-400 text-xs">{c.creature_type}</div>
                        <div className="flex gap-1 mt-2">
                          <button className="btn btn-secondary btn-xs" onClick={() => { setEditCreature(c); setShowCreatureModal(true); }}>
                            Edit
                          </button>
                          <button className="btn btn-danger btn-xs" onClick={() => handleDeleteCreature(c.id)}>
                            Delete
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
        </main>
      </div>

      {/* Creature Modal */}
      <CreatureModal
        isOpen={showCreatureModal}
        onClose={() => { setShowCreatureModal(false); setEditCreature(null); }}
        onSubmit={editCreature ? handleEditCreature : handleAddCreature}
        initialData={editCreature ? {
          name: editCreature.name,
          initiative: editCreature.initiative,
          creature_type: editCreature.creature_type,
          image_url: editCreature.image_url,
        } : undefined}
      />
    </div>
  );
};

export default Encounter;