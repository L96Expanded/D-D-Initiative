import * as React from 'react';
import { useEffect, useState } from 'react';
import { getApiBaseUrl } from '../utils/api';
import type { Encounter, CreatureType } from '../types';
import '../pages/Encounter.css';

interface InitiativeType {
  id: string;
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
}

interface DisplayData {
  encounter: Encounter | null;
  creatures: InitiativeType[];
  currentTurn: number;
  currentRound: number;
  fade: boolean;
}

const typeLabels = {
  player: "Player",
  enemy: "Enemy",
  ally: "Ally",
  other: "Other",
} as const;

const typeColors = {
  player: "bg-blue-500",
  enemy: "bg-red-700",
  ally: "bg-green-600",
  other: "bg-yellow-400",
} as const;

const EncounterDisplayPage: React.FC = () => {
  const [displayData, setDisplayData] = useState<DisplayData>({
    encounter: null,
    creatures: [],
    currentTurn: 0,
    currentRound: 1,
    fade: false
  });

  // Listen for updates from the control window
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'ENCOUNTER_UPDATE') {
        setDisplayData(event.data.payload);
      } else if (event.data.type === 'ENCOUNTER_LOADING') {
        // Control window is still loading, retry in a moment
        setTimeout(() => {
          if (window.opener) {
            window.opener.postMessage({ type: 'REQUEST_INITIAL_DATA' }, '*');
          }
        }, 500);
      }
    };

    window.addEventListener('message', handleMessage);
    
    // Request initial data from opener
    const requestData = () => {
      if (window.opener) {
        window.opener.postMessage({ type: 'REQUEST_INITIAL_DATA' }, '*');
      }
    };
    
    // Try immediately
    requestData();
    
    // Also retry after a short delay in case the control window wasn't ready
    const retryTimer = setTimeout(requestData, 500);

    return () => {
      window.removeEventListener('message', handleMessage);
      clearTimeout(retryTimer);
    };
  }, []);

  // Update window title when encounter data changes
  useEffect(() => {
    if (displayData.encounter?.name) {
      document.title = `${displayData.encounter.name} - D&D Initiative Tracker`;
    } else {
      document.title = 'D&D Initiative Tracker - Display';
    }
  }, [displayData.encounter?.name]);

  const getImageUrl = (imageUrl?: string, creatureType?: CreatureType): string => {
    if (!imageUrl) {
      return `/images/defaults/${creatureType ? creatureType.charAt(0).toUpperCase() + creatureType.slice(1) : 'Other'}.png`;
    }
    
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
      return imageUrl;
    } else if (imageUrl.startsWith('/database_images/')) {
      // Database image
      return `${getApiBaseUrl()}${imageUrl}`;
    } else if (imageUrl.startsWith('database_images/')) {
      // Database image without leading slash
      return `${getApiBaseUrl()}/${imageUrl}`;
    } else if (imageUrl.startsWith('/uploads/')) {
      return `${getApiBaseUrl()}${imageUrl}`;
    } else if (imageUrl.startsWith('user_uploads/')) {
      return `${getApiBaseUrl()}/uploads/${imageUrl}`;
    } else {
      return `${getApiBaseUrl()}/uploads/${imageUrl}`;
    }
  };

  if (!displayData.encounter) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-black">
        <div className="text-white text-xl">Waiting for encounter data...</div>
      </div>
    );
  }

  const sorted = [...displayData.creatures].sort((a, b) => b.initiative - a.initiative);
  const currentInitiative = sorted[displayData.currentTurn];
  const nextInitiative = sorted[(displayData.currentTurn + 1) % sorted.length];
  const tempInitiative = sorted[(displayData.currentTurn + 2) % sorted.length];

  return (
    <div className="combat-grid"
      style={{
        backgroundImage: displayData.encounter?.background_image ? `url(${getImageUrl(displayData.encounter.background_image)})` : undefined,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}>
      {/* Next Initiative, visually similar, shifted right and darker */}
      {nextInitiative && (
        <div className={`next-slanted-container${displayData.fade ? ' fade-out' : ' fade-in'}`}>
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
        <div className={`temp-slanted-container${displayData.fade ? ' fade-out' : ' fade-in'}`}>
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
          className={`current-container slanted-container ${displayData.fade ? 'fade-out' : 'fade-in'}`}
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
      </section>

      {/* Right: Initiative List */}
      <div className="initiative-list">
        <div className="initiative-header">
          <h2 className="initiative-title">
            {displayData.encounter.name}
          </h2>
          <div className="round-tracker">
            <span className="round-label">Round {displayData.currentRound}</span>
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
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EncounterDisplayPage;
