import * as React from 'react';
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { encountersAPI, creaturesAPI, uploadAPI, getApiBaseUrl } from '../utils/api';
import type { Encounter, Creature, CreateCreature, CreatureType } from '../types';

interface InitiativeType {
  id: string;
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
}

const typeLabels = {
  player: "Player",
  enemy: "Enemy",
  ally: "Ally",
  other: "Other",
} as const;

const EncounterControl: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [encounter, setEncounter] = useState<Encounter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creatures, setCreatures] = useState<InitiativeType[]>([]);
  const [currentTurn, setCurrentTurn] = useState(0);
  const [currentRound, setCurrentRound] = useState(1);
  const [showCreatureModal, setShowCreatureModal] = useState(false);
  const [editCreature, setEditCreature] = useState<Creature | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    initiative: 0,
    creature_type: 'enemy' as CreatureType
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [fade, setFade] = useState(false);
  const [displayWindow, setDisplayWindow] = useState<Window | null>(null);

  // Helper function to get full image URL
  const getFullImageUrl = (imageUrl: string | undefined): string | undefined => {
    if (!imageUrl) return undefined;
    if (imageUrl.startsWith('/database_images/')) {
      return `${getApiBaseUrl()}${imageUrl}`;
    }
    return imageUrl;
  };

  // Send updates to display window
  const updateDisplayWindow = () => {
    if (displayWindow && !displayWindow.closed && encounter) {
      displayWindow.postMessage({
        type: 'ENCOUNTER_UPDATE',
        payload: {
          encounter,
          creatures,
          currentTurn,
          currentRound,
          fade
        }
      }, '*');
    }
  };

  // Handle messages from display window
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'REQUEST_INITIAL_DATA') {
        // Send data directly to the requesting window (event.source)
        if (event.source && event.source !== window) {
          if (encounter) {
            // Send data immediately if encounter is loaded
            (event.source as Window).postMessage({
              type: 'ENCOUNTER_UPDATE',
              payload: {
                encounter,
                creatures,
                currentTurn,
                currentRound,
                fade
              }
            }, '*');
          } else {
            // If encounter isn't loaded yet, send a loading message
            (event.source as Window).postMessage({
              type: 'ENCOUNTER_LOADING'
            }, '*');
          }
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [encounter, creatures, currentTurn, currentRound, fade]);

  // Update display window whenever data changes
  useEffect(() => {
    updateDisplayWindow();
  }, [encounter, creatures, currentTurn, currentRound, fade]);

  // Open display window
  const openDisplayWindow = () => {
    const newWindow = window.open(
      `/encounter-display/${id}`,
      'EncounterDisplay',
      'width=1200,height=800,resizable=yes,scrollbars=no,menubar=no,toolbar=no'
    );
    
    if (newWindow) {
      setDisplayWindow(newWindow);
      
      // Send initial data when window loads
      newWindow.addEventListener('load', () => {
        updateDisplayWindow();
      });
      
      // Clean up when window closes
      const checkClosed = setInterval(() => {
        if (newWindow.closed) {
          setDisplayWindow(null);
          clearInterval(checkClosed);
        }
      }, 1000);
    }
  };

  // Reset form when modal opens/closes
  useEffect(() => {
    if (showCreatureModal) {
      if (editCreature) {
        setFormData({
          name: editCreature.name,
          initiative: editCreature.initiative,
          creature_type: editCreature.creature_type
        });
        setImageFile(null);
      } else {
        setFormData({
          name: '',
          initiative: 0,
          creature_type: 'enemy' as CreatureType
        });
        setImageFile(null);
      }
    }
  }, [showCreatureModal, editCreature]);

  const closeModal = () => {
    setShowCreatureModal(false);
    setEditCreature(null);
  };

  useEffect(() => {
    const fetchEncounter = async () => {
      setLoading(true);
      setError(null);
      try {
        if (!id) return;
        const data = await encountersAPI.getById(id);
        setEncounter(data);
        
        const initiativeData: InitiativeType[] = data.creatures.map(creature => ({
          id: creature.id,
          name: creature.name,
          initiative: creature.initiative,
          creature_type: creature.creature_type,
          image_url: creature.image_url,
        }));
        
        setCreatures(initiativeData.sort((a, b) => b.initiative - a.initiative));
        setCurrentTurn(0);
        setCurrentRound(1);
      } catch (err: any) {
        setError(err?.response?.data?.detail || 'Failed to load encounter');
      } finally {
        setLoading(false);
      }
    };
    fetchEncounter();
  }, [id]);

  const handleAddCreature = async (data: CreateCreature) => {
    if (!id) return;
    try {
      const newCreature = await encountersAPI.addCreature(id, data);
      const newInitiative: InitiativeType = {
        id: newCreature.id,
        name: newCreature.name,
        initiative: newCreature.initiative,
        creature_type: newCreature.creature_type,
        image_url: newCreature.image_url,
      };
      setCreatures((prev) => [...prev, newInitiative].sort((a, b) => b.initiative - a.initiative));
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to add creature');
    }
  };

  const handleUpdateCreature = async (creature: Creature, data: CreateCreature) => {
    if (!id) return;
    try {
      const updatedCreature = await creaturesAPI.update(creature.id, data);
      setCreatures((prev) => 
        prev.map(c => c.id === creature.id ? {
          id: updatedCreature.id,
          name: updatedCreature.name,
          initiative: updatedCreature.initiative,
          creature_type: updatedCreature.creature_type,
          image_url: updatedCreature.image_url,
        } : c).sort((a, b) => b.initiative - a.initiative)
      );
      
      // Update encounter data
      if (encounter) {
        setEncounter({
          ...encounter,
          creatures: encounter.creatures.map(c => c.id === creature.id ? updatedCreature : c)
        });
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update creature');
    }
  };

  const handleDeleteCreature = async (creatureId: string) => {
    if (!id) return;
    try {
      await creaturesAPI.delete(creatureId);
      setCreatures((prev) => prev.filter(c => c.id !== creatureId));
      
      // Update encounter data
      if (encounter) {
        setEncounter({
          ...encounter,
          creatures: encounter.creatures.filter(c => c.id !== creatureId)
        });
      }
      
      // Adjust current turn if necessary
      const newCreatures = creatures.filter(c => c.id !== creatureId);
      if (currentTurn >= newCreatures.length && newCreatures.length > 0) {
        setCurrentTurn(0);
      }
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete creature');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('=== ENCOUNTER CONTROL SUBMIT DEBUG ===');
    console.log('formData.name:', formData.name);
    console.log('editCreature:', editCreature);
    console.log('=======================================');
    
    let imageUrl = editCreature?.image_url;
    
    if (imageFile) {
      try {
        const uploadResult = await uploadAPI.uploadImage(imageFile);
        imageUrl = uploadResult.url;
      } catch (error) {
        console.error('Failed to upload image:', error);
      }
    } else if (formData.name && formData.name.trim() !== '') {
      // Auto-fetch image from creature database if no file uploaded
      try {
        console.log('Fetching image for creature:', formData.name);
        const response = await fetch(`${getApiBaseUrl()}/api/creature-images/get_creature_image?name=${encodeURIComponent(formData.name)}&creature_type=${formData.creature_type}`);
        console.log('API response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('API response data:', data);
          if (data.image_url) {
            // Store the relative path as returned by the API
            imageUrl = data.image_url;
          }
        } else {
          console.log('API response not ok:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Failed to fetch creature image:', error);
      }
    }
    
    const creatureData: CreateCreature = {
      name: formData.name,
      initiative: formData.initiative,
      creature_type: formData.creature_type,
      image_url: imageUrl
    };

    if (editCreature) {
      await handleUpdateCreature(editCreature, creatureData);
    } else {
      await handleAddCreature(creatureData);
    }
    
    closeModal();
  };

  const prevTurn = () => {
    setFade(true);
    setTimeout(() => {
      const nextTurn = (currentTurn - 1 + creatures.length) % creatures.length;
      setCurrentTurn(nextTurn);
      
      if (currentTurn === 0 && nextTurn === creatures.length - 1) {
        setCurrentRound(prev => Math.max(1, prev - 1));
      }
      
      setFade(false);
    }, 350);
  };

  const resetRound = () => {
    setFade(true);
    setTimeout(() => {
      setCurrentTurn(0);
      setCurrentRound(1);
      setFade(false);
    }, 350);
  };

  const advanceTurn = () => {
    setFade(true);
    setTimeout(() => {
      const nextTurn = (currentTurn + 1) % creatures.length;
      setCurrentTurn(nextTurn);
      
      if (nextTurn === 0) {
        setCurrentRound(prev => prev + 1);
      }
      
      setFade(false);
    }, 350);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white text-xl">Loading encounter...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    );
  }

  if (!encounter) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white text-xl">Encounter not found</div>
      </div>
    );
  }

  const sorted = [...creatures].sort((a, b) => b.initiative - a.initiative);

  return (
    <div className="encounter-control-container" style={{ padding: '20px', backgroundColor: '#1a1a1a', color: 'white', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '10px' }}>{encounter.name} - Control Panel</h1>
          <p style={{ color: '#888' }}>Round {currentRound} - {sorted[currentTurn]?.name || 'No creatures'}'s turn</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={openDisplayWindow}
            style={{
              padding: '10px 20px',
              backgroundColor: '#4f46e5',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Open Display Window
          </button>
          <button 
            onClick={() => navigate('/encounters')}
            style={{
              padding: '10px 20px',
              backgroundColor: '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Back to Encounters
          </button>
        </div>
      </div>

      {/* Turn Controls */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <button 
          onClick={prevTurn}
          style={{
            padding: '10px 20px',
            backgroundColor: '#dc2626',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Previous Turn
        </button>
        <button 
          onClick={advanceTurn}
          style={{
            padding: '10px 20px',
            backgroundColor: '#059669',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Next Turn
        </button>
        <button 
          onClick={resetRound}
          style={{
            padding: '10px 20px',
            backgroundColor: '#7c2d12',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Reset Round
        </button>
      </div>

      {/* Add Creature Button */}
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={() => setShowCreatureModal(true)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#16a34a',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
        >
          Add Creature
        </button>
      </div>

      {/* Creatures List */}
      <div style={{ backgroundColor: '#2a2a2a', padding: '20px', borderRadius: '12px' }}>
        <h2 style={{ marginBottom: '15px' }}>Creatures</h2>
        {sorted.length === 0 ? (
          <p style={{ color: '#888' }}>No creatures in this encounter</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {sorted.map((creature, index) => (
              <div 
                key={creature.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '15px',
                  backgroundColor: index === currentTurn ? '#4f46e5' : '#3a3a3a',
                  borderRadius: '8px',
                  gap: '15px'
                }}
              >
                <span style={{ fontWeight: 'bold', minWidth: '40px' }}>
                  {creature.initiative}
                </span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
                  {creature.image_url && (
                    <img 
                      src={getFullImageUrl(creature.image_url)}
                      alt={creature.name}
                      style={{
                        width: '32px',
                        height: '32px',
                        objectFit: 'cover',
                        borderRadius: '4px',
                        border: '1px solid #666'
                      }}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                      }}
                    />
                  )}
                  <span style={{ fontSize: '1.1rem' }}>
                    {creature.name}
                  </span>
                </div>
                <span style={{ color: '#888', minWidth: '80px' }}>
                  {typeLabels[creature.creature_type]}
                </span>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <button
                    onClick={() => {
                      // Find the full creature object from encounter.creatures
                      const originalCreature = encounter?.creatures.find(c => c.id === creature.id);
                      if (originalCreature) {
                        setEditCreature(originalCreature);
                        setShowCreatureModal(true);
                      } else {
                        // Fallback: convert InitiativeType to Creature format
                        const fallbackCreature: Creature = {
                          id: creature.id,
                          name: creature.name,
                          initiative: creature.initiative,
                          creature_type: creature.creature_type,
                          image_url: creature.image_url,
                          encounter_id: id || '',
                          created_at: new Date().toISOString()
                        };
                        setEditCreature(fallbackCreature);
                        setShowCreatureModal(true);
                      }
                    }}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDeleteCreature(creature.id)}
                    style={{
                      padding: '5px 10px',
                      backgroundColor: '#dc2626',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Creature Modal */}
      {showCreatureModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#2a2a2a',
            padding: '30px',
            borderRadius: '12px',
            width: '400px',
            maxWidth: '90vw'
          }}>
            <h3 style={{ marginBottom: '20px' }}>
              {editCreature ? 'Edit Creature' : 'Add Creature'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#3a3a3a',
                    border: '1px solid #555',
                    borderRadius: '4px',
                    color: 'white'
                  }}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Initiative</label>
                <input
                  type="number"
                  value={formData.initiative}
                  onChange={(e) => setFormData({ ...formData, initiative: parseInt(e.target.value) || 0 })}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#3a3a3a',
                    border: '1px solid #555',
                    borderRadius: '4px',
                    color: 'white'
                  }}
                />
              </div>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Type</label>
                <select
                  value={formData.creature_type}
                  onChange={(e) => setFormData({ ...formData, creature_type: e.target.value as CreatureType })}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#3a3a3a',
                    border: '1px solid #555',
                    borderRadius: '4px',
                    color: 'white'
                  }}
                >
                  <option value="enemy">Enemy</option>
                  <option value="player">Player</option>
                  <option value="ally">Ally</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px' }}>Image</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    backgroundColor: '#3a3a3a',
                    border: '1px solid #555',
                    borderRadius: '4px',
                    color: 'white'
                  }}
                />
              </div>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="submit"
                  style={{
                    flex: 1,
                    padding: '10px',
                    backgroundColor: '#16a34a',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {editCreature ? 'Update' : 'Add'}
                </button>
                <button
                  type="button"
                  onClick={closeModal}
                  style={{
                    flex: 1,
                    padding: '10px',
                    backgroundColor: '#6b7280',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EncounterControl;