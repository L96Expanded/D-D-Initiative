import * as React from 'react';
import { useState, useEffect } from 'react';
import Modal from './Modal';
import { getApiBaseUrl } from '../utils/api';
import type { CreateCreature, CreatureType } from '../types';

interface CreatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCreature) => void;
  initialData?: CreateCreature | null;
}

const CreatureModal: React.FC<CreatureModalProps> = ({ isOpen, onClose, onSubmit, initialData }) => {
  const [name, setName] = useState('');
  const [initiative, setInitiative] = useState(0);
  const [creatureType, setCreatureType] = useState<CreatureType>('enemy');
  const [imageUrl, setImageUrl] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isFetchingImage, setIsFetchingImage] = useState(false);

  console.log('CreatureModal rendered - isOpen:', isOpen, 'initialData:', initialData);

  // Update form fields when initialData changes or modal opens
  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setName(initialData.name || '');
        setInitiative(initialData.initiative || 0);
        setCreatureType(initialData.creature_type || 'enemy');
        setImageUrl(initialData.image_url || '');
      } else {
        // Reset form for new creature
        setName('');
        setInitiative(0);
        setCreatureType('enemy');
        setImageUrl('');
      }
      setError(null);
    }
  }, [isOpen, initialData]);

  // Auto-fetch image when name changes - DISABLED, now fetching on submit
  // useEffect(() => {
  //   // Image fetching moved to handleSubmit for more reliable behavior
  // }, [name, isOpen, initialData, creatureType]);

  const handleSubmit = async (e: React.FormEvent) => {
    console.log('handleSubmit called!', e);
    e.preventDefault();
    if (!name.trim()) {
      setError('Creature name is required');
      return;
    }
    if (initiative < 0) {
      setError('Initiative must be 0 or greater');
      return;
    }
    
    setError(null);
    
    // Fetch image before submitting if we don't have one or if this is a new creature
    let finalImageUrl = imageUrl;
    const shouldFetchImage = !imageUrl || imageUrl.trim() === '' || !initialData;
    
    console.log('=== SUBMIT DEBUG ===');
    console.log('name:', name);
    console.log('imageUrl:', imageUrl);
    console.log('initialData:', initialData);
    console.log('shouldFetchImage:', shouldFetchImage);
    console.log('===================');
    
    if (shouldFetchImage && name.trim() !== '') {
      try {
        setIsFetchingImage(true);
        console.log('Fetching image for creature before submit:', name);
        const response = await fetch(`${getApiBaseUrl()}/api/creature-images/get_creature_image?name=${encodeURIComponent(name)}&creature_type=${creatureType}`);
        console.log('API response status:', response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log('API response data:', data);
          if (data.image_url) {
            finalImageUrl = data.image_url;
            setImageUrl(data.image_url); // Update the UI as well
          }
        } else {
          console.log('API response not ok:', response.status, response.statusText);
        }
      } catch (error) {
        console.error('Failed to fetch creature image during submit:', error);
      } finally {
        setIsFetchingImage(false);
      }
    }
    
    onSubmit({ name, initiative, creature_type: creatureType, image_url: finalImageUrl });
    onClose(); // Let the parent handle form reset via useEffect
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={initialData ? 'Edit Creature' : 'Add Creature'}>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="text-left">
          Name
          <input
            type="text"
            className="w-full px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
            value={name}
            onChange={e => setName(e.target.value)}
            required
          />
        </label>
        <label className="text-left">
          Initiative
          <input
            type="number"
            className="w-full px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
            value={initiative}
            onChange={e => setInitiative(Number(e.target.value))}
            min={0}
            required
          />
        </label>
        <label className="text-left">
          Type
          <select
            className="w-full px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
            value={creatureType}
            onChange={e => setCreatureType(e.target.value as CreatureType)}
          >
            <option value="player">Player</option>
            <option value="enemy">Enemy</option>
            <option value="ally">Ally</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label className="text-left">
          Image URL
          <div className="flex items-center gap-2">
            <input
              type="text"
              className="flex-1 px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
              value={imageUrl}
              onChange={e => setImageUrl(e.target.value)}
              placeholder="Auto-filled or enter custom URL"
            />
            {isFetchingImage && (
              <span className="text-blue-400 text-sm mt-1">Fetching...</span>
            )}
          </div>
          {imageUrl && (
            <div className="mt-2">
              <img 
                src={imageUrl} 
                alt={name} 
                className="w-16 h-16 object-cover rounded border border-gray-600"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                }}
              />
            </div>
          )}
        </label>
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <button 
          type="submit" 
          className="btn btn-primary w-full"
          onClick={() => console.log('Button clicked!')}
        >
          {initialData ? 'Save Changes' : 'Add Creature'}
        </button>
      </form>
    </Modal>
  );
};

export default CreatureModal;
