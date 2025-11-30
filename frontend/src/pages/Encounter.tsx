import * as React from 'react';
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { encountersAPI, creaturesAPI, getApiBaseUrl } from '../utils/api';
import type { Encounter, Creature, CreateCreature, CreatureType } from '../types';
import CreatureModal from '../components/CreatureModal';
import './Encounter.css';

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
  const [fade, setFade] = useState(false);

  const handleCreatureSubmit = async (data: CreateCreature) => {
    if (editCreature) {
      await handleEditCreature(data);
    } else {
      await handleAddCreature(data);
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
    } else if (imageUrl.startsWith('/database_images/')) {
      // Database image
      return `${getApiBaseUrl()}${imageUrl}`;
    } else if (imageUrl.startsWith('database_images/')) {
      // Database image without leading slash
      return `${getApiBaseUrl()}/${imageUrl}`;
    } else if (imageUrl.startsWith('/uploads/')) {
      // Backend upload URL - construct full URL
      return `${getApiBaseUrl()}${imageUrl}`;
    } else if (imageUrl.startsWith('/')) {
      // Frontend static asset
      return imageUrl;
    } else if (imageUrl.startsWith('user_uploads/')) {
      // Old format: user_uploads/filename.jpg (without /uploads/ prefix)
      return `${getApiBaseUrl()}/uploads/${imageUrl}`;
    } else {
      // Other relative backend path - assume it's an upload
      return `${getApiBaseUrl()}/uploads/${imageUrl}`;
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
              className={`initiative-item bg-black} 
                ${creature.id === currentInitiative?.id ? 'current' : ''}`}

                onClick={() => {
                  const originalCreature = encounter?.creatures.find(c => c.id === creature.id);
                    if (originalCreature) {
                      setEditCreature(originalCreature);
                      setShowCreatureModal(true);
                    }
                  }
                }
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

      {/* Creature Modal */}
      <CreatureModal
        isOpen={showCreatureModal}
        onClose={() => {
          setShowCreatureModal(false);
          setEditCreature(null);
        }}
        onSubmit={handleCreatureSubmit}
        initialData={editCreature ? {
          name: editCreature.name,
          initiative: editCreature.initiative,
          creature_type: editCreature.creature_type,
          image_url: editCreature.image_url
        } : null}
      />
    </div>
  );
};

export default Encounter;
