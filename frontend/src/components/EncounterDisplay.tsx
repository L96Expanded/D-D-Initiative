import * as React from 'react';
import { useEffect, useState } from 'react';
import type { Encounter, CreatureType } from '../types';
import '../pages/Encounter.css';

interface InitiativeType {
  id?: number;
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
}

interface EncounterDisplayProps {
  encounter: Encounter;
  creatures: InitiativeType[];
  currentTurn: number;
  currentRound: number;
  fade: boolean;
}

// Component for handling creature images with API fallback
const CreatureImage: React.FC<{ creature: InitiativeType }> = ({ creature }) => {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const getDefaultImage = (name: string): string => {
    // Simple fallback that's guaranteed to work
    const cleanName = name.replace(/[^a-zA-Z0-9]/g, '').toLowerCase() || 'creature';
    return `https://api.dicebear.com/7.x/shapes/svg?seed=${cleanName}&backgroundColor=e0e7ff&size=128`;
  };

  useEffect(() => {
    const loadImage = async () => {
      setLoading(true);
      setError(false);
      console.log('CreatureImage useEffect called for:', creature.name, 'with image_url:', creature.image_url);
      
      try {
        // Priority 1: User-provided image
        if (creature.image_url && creature.image_url.trim()) {
          console.log('Using user-provided image:', creature.image_url);
          
          // Test if the user image actually loads
          const testImage = new Image();
          testImage.onload = () => {
            console.log('User image loaded successfully');
            setImageUrl(creature.image_url!);
            setLoading(false);
          };
          testImage.onerror = () => {
            console.log('User image failed to load, trying API');
            // Fall through to API call
            tryApiImage();
          };

          // Construct the correct URL based on the image path
          let imageUrl: string;
          if (creature.image_url.startsWith('http://') || creature.image_url.startsWith('https://')) {
            // Full URL
            imageUrl = creature.image_url;
          } else if (creature.image_url.startsWith('/database_images/')) {
            // Database image
            imageUrl = `http://localhost:8000${creature.image_url}`;
          } else if (creature.image_url.startsWith('database_images/')) {
            // Database image without leading slash
            imageUrl = `http://localhost:8000/${creature.image_url}`;
          } else {
            // Uploaded file
            imageUrl = `http://localhost:8000/uploads/${creature.image_url}`;
          }
          
          console.log(`Constructing URL for image: "${creature.image_url}" -> "${imageUrl}"`);
          testImage.src = imageUrl;
          return;
        }

        // Priority 2: Try API
        await tryApiImage();

      } catch (error) {
        console.error('Error in loadImage:', error);
        handleFallback();
      }
    };

    const tryApiImage = async () => {
      try {
        console.log('Fetching image for creature:', creature.name);
        const response = await fetch(`http://127.0.0.1:8000/api/creature-images/get_creature_image?name=${encodeURIComponent(creature.name)}&creature_type=${encodeURIComponent(creature.creature_type)}`);
        console.log('API response status:', response.status);

        if (response.ok) {
          const data = await response.json();
          console.log('API response data:', data);
          
          if (data.image_url) {
            // Handle relative paths from API
            let imageUrl = data.image_url;
            if (data.image_url.startsWith('/database_images/')) {
              imageUrl = `http://localhost:8000${data.image_url}`;
            }
            
            // Test if the API image actually loads
            const testImage = new Image();
            testImage.onload = () => {
              console.log('API image loaded successfully:', imageUrl);
              setImageUrl(imageUrl);
              setLoading(false);
            };
            testImage.onerror = () => {
              console.log('API image failed to load, using fallback');
              handleFallback();
            };
            testImage.src = imageUrl;
          } else {
            throw new Error('No image_url in API response');
          }
        } else {
          console.error('API request failed with status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
          handleFallback();
        }
      } catch (error) {
        console.error('Could not fetch creature image from API:', error);
        handleFallback();
      }
    };

    const handleFallback = () => {
      console.log('Using fallback image');
      setError(true);
      const fallbackUrl = getDefaultImage(creature.name);
      setImageUrl(fallbackUrl);
      setLoading(false);
    };

    loadImage();
  }, [creature.name, creature.image_url]);

  const handleImageError = () => {
    console.log('Image failed to load, using final fallback');
    setError(true);
    setImageUrl(getDefaultImage(creature.name));
  };

  if (loading) {
    return <div className="creature-image-loading">Loading...</div>;
  }

  return (
    <div className="creature-image-container">
      <img 
        src={imageUrl}
        alt={creature.name}
        className="creature-image"
        onError={handleImageError}
        onLoad={() => console.log('Image displayed successfully:', imageUrl)}
      />
      {error && (
        <div className="image-error-indicator" title="Using fallback image">
          ⚠️
        </div>
      )}
    </div>
  );
};

const typeLabels = {
  player: "Player",
  enemy: "Enemy",
  ally: "Ally",
  other: "Other",
} as const;

const EncounterDisplay: React.FC<EncounterDisplayProps> = ({
  encounter,
  creatures,
  currentTurn,
  currentRound,
  fade
}) => {
  const [displayData, setDisplayData] = useState<EncounterDisplayProps>({
    encounter,
    creatures,
    currentTurn,
    currentRound,
    fade
  });

  // Listen for updates from the control window
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'ENCOUNTER_UPDATE') {
        setDisplayData(event.data.payload);
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  // Use local display data that gets updated via messages
  const currentData = displayData;
  const sorted = [...currentData.creatures].sort((a, b) => b.initiative - a.initiative);
  const currentInitiative = sorted[currentData.currentTurn];
  const nextCreature = sorted[(currentData.currentTurn + 1) % sorted.length];
  const tempCreature = sorted[(currentData.currentTurn + 2) % sorted.length];

  const getImageUrl = (imageUrl?: string): string => {
    if (!imageUrl) return '';
    
    if (imageUrl.startsWith('http://') || imageUrl.startsWith('https://')) {
      return imageUrl;
    } else if (imageUrl.startsWith('/database_images/')) {
      // Database image
      return `http://localhost:8000${imageUrl}`;
    } else if (imageUrl.startsWith('database_images/')) {
      // Database image without leading slash
      return `http://localhost:8000/${imageUrl}`;
    } else if (imageUrl.startsWith('/uploads/')) {
      return `http://localhost:8000${imageUrl}`;
    } else if (imageUrl.startsWith('user_uploads/')) {
      return `http://localhost:8000/uploads/${imageUrl}`;
    } else {
      return `http://localhost:8000/uploads/${imageUrl}`;
    }
  };

  return (
    <div 
      className="encounter-page"
      style={{
        backgroundImage: currentData.encounter.background_image 
          ? `url(${getImageUrl(currentData.encounter.background_image)})` 
          : 'none'
      }}
    >
      {/* Main Combat Display */}
      <section className="main-display">
        {/* Current Creature */}
        <div className={`current-creature ${currentData.fade ? 'fade-out' : 'fade-in'}`}>
          {currentInitiative ? (
            <>
              <h1 className="creature-name">
                {currentInitiative.name}
              </h1>
              <div className="creature-info">
                <span className="creature-initiative">
                  Initiative: {currentInitiative.initiative}
                </span>
                <span className="creature-type">
                  {typeLabels[currentInitiative.creature_type]}
                </span>
              </div>
              <CreatureImage creature={currentInitiative} />
            </>
          ) : (
            <div className="no-creatures">
              <h1>No creatures in this encounter</h1>
            </div>
          )}
        </div>

        {/* Next Up Preview */}
        {nextCreature && sorted.length > 1 && (
          <div className="next-up">
            <h3>Next Up</h3>
            <div className="next-creature">
              <span className="next-name">{nextCreature.name}</span>
              <span className="next-initiative">Initiative: {nextCreature.initiative}</span>
            </div>
            {tempCreature && sorted.length > 2 && (
              <div className="temp-creature">
                <span className="temp-name">Then: {tempCreature.name}</span>
              </div>
            )}
          </div>
        )}

        {/* Round Tracker */}
        <div className="round-display">
          <h2>Round {currentData.currentRound}</h2>
        </div>
      </section>

      {/* Initiative Order Display */}
      <div className="initiative-display">
        <h3 className="initiative-display-title">{currentData.encounter.name}</h3>
        <div className="initiative-order">
          {sorted.map((creature, index) => (
            <div
              key={creature.id}
              className={`initiative-display-item ${
                index === currentData.currentTurn ? 'current' : ''
              }`}
            >
              <span className="display-initiative">{creature.initiative}</span>
              <span className="display-name">{creature.name}</span>
              <span className="display-type">{typeLabels[creature.creature_type]}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EncounterDisplay;