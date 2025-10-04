import * as React from 'react';
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { encountersAPI, creaturesAPI, uploadAPI } from '../utils/api';
import type { Encounter, Creature, CreateCreature, CreatureType } from '../types';
import './Encounter.css';

interface InitiativeType {
  id: string;
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
}

const typeColors = {
  player: "bg-blue-500",
  enemy: "bg-red-700",
  ally: "bg-green-600",
  other: "bg-yellow-400",
} as const;

const typeLabels = {
  player: "Player",
  enemy: "Enemy",
  ally: "Ally",
  other: "Other",
} as const;

const Encounter: React.FC = () => {
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
// Clear file input when editing
      } else {
        setFormData({
          name: '',
          initiative: 0,
          creature_type: 'enemy'
        });
        setImageFile(null);
      }
    }
  }, [showCreatureModal, editCreature]);

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      alert('Creature name is required');
      return;
    }
    
    let imageUrl = undefined;
    
    
// If a file was uploaded, upload it first and get the URL
    if (imageFile) {
      try {
        const uploadResult = await uploadAPI.uploadImage(imageFile);
        imageUrl = uploadResult.url;
      } catch (error) {
        console.error('Failed to upload image:', error);
        alert('Failed to upload image. The creature will be created without an image.');
        imageUrl = undefined; 
// Use default image if upload fails
      }
    }
    
    const submitData: CreateCreature = {
      name: formData.name,
      initiative: formData.initiative,
      creature_type: formData.creature_type,
      image_url: imageUrl || undefined
    };

    if (editCreature) {
      await handleEditCreature(submitData);
    } else {
      await handleAddCreature(submitData);
    }
    
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
        
        
// Convert creatures to InitiativeType and sort by initiative
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

  const handleEditCreature = async (data: CreateCreature) => {
    if (!editCreature) return;
    try {
      const updated = await creaturesAPI.update(editCreature.id, data);
      const updatedInitiative: InitiativeType = {
        id: updated.id,
        name: updated.name,
        initiative: updated.initiative,
        creature_type: updated.creature_type,
        image_url: updated.image_url,
      };
      setCreatures((prev) => prev.map(c => c.id === updated.id ? updatedInitiative : c).sort((a, b) => b.initiative - a.initiative));
      setEditCreature(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to update creature');
    }
  };

  const handleDeleteCreature = async (creatureId: string) => {
    if (!window.confirm('Delete this creature?')) return;
    try {
      await creaturesAPI.delete(creatureId);
      setCreatures((prev) => prev.filter(c => c.id !== creatureId));
      if (currentTurn >= creatures.length - 1) setCurrentTurn(0);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to delete creature');
    }
  };

  const getImageUrl = (imageUrl?: string, creatureType?: CreatureType) => {
    // Only use default images if no image URL is provided or if it's empty/whitespace
    if (!imageUrl || imageUrl.trim() === '') {
      // Use type-specific default images
      switch (creatureType) {
        case 'player': return '/images/defaults/Player.png';
        case 'enemy': return '/images/defaults/Enemy.png';
        case 'ally': return '/images/defaults/Ally.png';
        case 'other': return '/images/defaults/Other.png';
        default: return '/images/defaults/Other.png';
      }
    }
    
    // Fix double user_uploads in URLs (legacy bug fix)
    if (imageUrl.includes('/user_uploads/user_uploads/')) {
      imageUrl = imageUrl.replace('/user_uploads/user_uploads/', '/user_uploads/');
    }
    
    // If image URL is provided, use it
    if (imageUrl.startsWith('http')) {
      // External URL
      return imageUrl;
    } else if (imageUrl.startsWith('/uploads/')) {
      // Backend upload URL - construct full URL
      return `http://localhost:8000${imageUrl}`;
    } else if (imageUrl.startsWith('/')) {
      // Frontend static asset
      return imageUrl;
    } else if (imageUrl.startsWith('user_uploads/')) {
      // Old format: user_uploads/filename.jpg (without /uploads/ prefix)
      return `http://localhost:8000/uploads/${imageUrl}`;
    } else {
      // Other relative backend path - assume it's an upload
      return `http://localhost:8000/uploads/${imageUrl}`;
    }
  };

  const prevTurn = () => {
    setFade(true);
    setTimeout(() => {
      const nextTurn = (currentTurn - 1 + creatures.length) % creatures.length;
      setCurrentTurn(nextTurn);
      
      // If we're going from turn 0 to the last turn, decrement the round (but not below 1)
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
      
      // If we're going back to turn 0, increment the round
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

  if (!encounter || creatures.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-black">
        <div className="text-white text-xl">No creatures in this encounter</div>
        <button 
          onClick={() => navigate('/home')} 
          className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded text-white"
        >
          ← Back to Home
        </button>
      </div>
    );
  }

  
// Sort creatures by initiative (descending)
  const sorted = [...creatures].sort((a, b) => b.initiative - a.initiative);
  const currentInitiative = sorted[currentTurn];
  const nextInitiative = sorted[(currentTurn + 1) % sorted.length];
  const tempInitiative = sorted[(currentTurn + 2) % sorted.length];

  return (
    <div className="combat-grid"
      style={{
      backgroundImage: encounter?.background_image ? `url(${getImageUrl(encounter.background_image)})` : undefined,
      backgroundSize: 'cover',
      backgroundPosition: 'center'
      }}>
      {/* Next Initiative, visually similar, shifted right and darker */}
      {nextInitiative && (
        <div className={`next-slanted-container${fade ? ' fade-out' : ' fade-in'}`}>
          <img
            src={getImageUrl(nextInitiative.image_url, nextInitiative.creature_type)}
            alt={nextInitiative.name + ' next'}
            onError={(e) => {
              e.currentTarget.src = '/images/defaults/Other.png';
            }}
          />
        </div>
      )}
      
      {/* Temp Initiative, visually similar, shifted right and darker */}
      {tempInitiative && (
        <div className={`temp-slanted-container${fade ? ' fade-out' : ' fade-in'}`}>
          <img
            src={getImageUrl(tempInitiative.image_url, tempInitiative.creature_type)}
            alt={tempInitiative.name + ' temp'}
            onError={(e) => {
              e.currentTarget.src = '/images/defaults/Other.png';
            }}
          />
        </div>
      )}
      
      {/* Left: Current Creature Display */}
      <section className="current-section">
        <div
          className={`current-container slanted-container ${fade ? 'fade-out' : 'fade-in'}`}

        >
          {currentInitiative && (
            <>
              <img
                alt={currentInitiative.name}
                src={getImageUrl(currentInitiative.image_url, currentInitiative.creature_type)}
                className="current-image"
                onError={(e) => {
                  e.currentTarget.src = '/images/defaults/Other.png';
                }}
              />
            </>
          )}
          <div className="image-overlay" />
        </div>

        {/* Controls */}
        <div className="turn-controls">
          <button onClick={prevTurn} className="control-button control-prev">
            Prev Turn
          </button>
          <button onClick={advanceTurn} className="control-button control-next">
            Next Turn
          </button>
          <button onClick={resetRound} className="control-button control-reset">
            Reset Round
          </button>
        </div>
      </section>

      {/* Right: Initiative List */}
      <div className="initiative-list">
        <div className="initiative-header">
          <h2 className="initiative-title">
            {encounter.name}
          </h2>
          <div className="round-tracker">
            <span className="round-label">Round {currentRound}</span>
          </div>
        </div>
        <div className="initiative-grid">
          {sorted.map((creature) => (
            <div
              key={creature.id}
              className={`initiative-item ${typeColors[creature.creature_type]} 
                ${creature.id === currentInitiative?.id ? 'current' : ''}`}
            >
              <span className="initiative-number">
                {creature.initiative}
              </span>
              <span className="character-name">
                {creature.name}
              </span>
              <span className="character-type">
                {typeLabels[creature.creature_type]}
              </span>
              {/* Action buttons */}
              <div className="flex gap-1 ml-auto">
                <button 
                  onClick={() => {
                    
// Find the original creature object for editing
                    const originalCreature = encounter?.creatures.find(c => c.id === creature.id);
                    if (originalCreature) {
                      setEditCreature(originalCreature);
                      setShowCreatureModal(true);
                    }
                  }}
                  className="bg-blue-600 hover:bg-blue-700 px-2 py-1 rounded text-white text-xs"
                >
                  Edit
                </button>
                <button 
                  onClick={() => handleDeleteCreature(creature.id)}
                  className="bg-red-600 hover:bg-red-700 px-2 py-1 rounded text-white text-xs"
                >
                  Del
                </button>
              </div>
            </div>
          ))}
        </div>
        
        {/* Action buttons */}
        <div className="flex gap-2 mt-4">
          <button 
            onClick={() => {
              setEditCreature(null);
              setShowCreatureModal(true);
            }}
            className="bg-green-600 hover:bg-green-700 px-4 py-2 rounded text-white text-sm flex-1"
          >
            Add Creature
          </button>
          <button 
            onClick={() => navigate('/home')}
            className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded text-white text-sm flex-1"
          >
            Back
          </button>
        </div>
      </div>

      {/* Simple Direct Modal Implementation */}
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
          zIndex: 10000
        }}>
          <div style={{
            backgroundColor: '#1f2937',
            padding: '2rem',
            borderRadius: '0.75rem',
            border: '1px solid #374151',
            maxWidth: '32rem',
            width: '90vw',
            color: 'white',
            position: 'relative'
          }}>
            <button
              onClick={() => {
                setShowCreatureModal(false);
                setEditCreature(null);
              }}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'none',
                border: 'none',
                color: '#9ca3af',
                fontSize: '1.5rem',
                cursor: 'pointer'
              }}
            >
              ×
            </button>
            
            <h3 style={{ marginBottom: '1.5rem', textAlign: 'center', fontSize: '1.25rem', fontWeight: 'bold' }}>
              {editCreature ? 'Edit Creature' : 'Add Creature'}
            </h3>
            
            <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    borderRadius: '0.375rem',
                    border: '1px solid #374151',
                    backgroundColor: '#374151',
                    color: 'white'
                  }}
                  required
                />
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Initiative</label>
                <input
                  type="number"
                  value={formData.initiative}
                  onChange={e => setFormData(prev => ({ ...prev, initiative: Number(e.target.value) }))}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    borderRadius: '0.375rem',
                    border: '1px solid #374151',
                    backgroundColor: '#374151',
                    color: 'white'
                  }}
                  min="0"
                  required
                />
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Type</label>
                <select
                  value={formData.creature_type}
                  onChange={e => setFormData(prev => ({ ...prev, creature_type: e.target.value as CreatureType }))}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    borderRadius: '0.375rem',
                    border: '1px solid #374151',
                    backgroundColor: '#374151',
                    color: 'white'
                  }}
                >
                  <option value="player">Player</option>
                  <option value="enemy">Enemy</option>
                  <option value="ally">Ally</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div>
                <label style={{ display: 'block', marginBottom: '0.5rem' }}>Image</label>
                <div style={{ marginBottom: '0.5rem' }}>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={e => {
                      const file = e.target.files?.[0];
                      if (file) {
                        setImageFile(file);
                      }
                    }}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #374151',
                      backgroundColor: '#374151',
                      color: 'white'
                    }}
                  />
                </div>
              </div>
              
              {/* Image Preview */}
              {imageFile && (
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Preview</label>
                  <img
                    src={URL.createObjectURL(imageFile)}
                    alt="Preview"
                    style={{
                      maxWidth: '100px',
                      maxHeight: '100px',
                      objectFit: 'cover',
                      borderRadius: '0.375rem',
                      border: '1px solid #374151'
                    }}
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                </div>
              )}
              
              <button
                type="submit"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '0.375rem',
                  border: 'none',
                  backgroundColor: '#059669',
                  color: 'white',
                  fontSize: '1rem',
                  fontWeight: 'bold',
                  cursor: 'pointer',
                  marginTop: '1rem'
                }}
              >
                {editCreature ? 'Save Changes' : 'Add Creature'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Encounter;