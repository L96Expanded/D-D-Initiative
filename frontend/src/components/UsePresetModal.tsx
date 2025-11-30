import * as React from 'react';
import { useState, useEffect } from 'react';
import { uploadAPI, getApiBaseUrl } from '../utils/api';
import type { Preset, CreateEncounter, CreateCreature, CreatureType } from '../types';

interface UsePresetModalProps {
  isOpen: boolean;
  preset: Preset;
  onClose: () => void;
  onSubmit: (data: CreateEncounter) => void;
}

const UsePresetModal: React.FC<UsePresetModalProps> = ({ isOpen, preset, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [backgroundImageFile, setBackgroundImageFile] = useState<File | null>(null);
  const [creatures, setCreatures] = useState<CreateCreature[]>([]);
  const [error, setError] = useState('');

  const [newCreature, setNewCreature] = useState<{
    name: string;
    initiative: number;
    creature_type: CreatureType;
    image_file: File | null;
  }>({
    name: '',
    initiative: 10,
    creature_type: 'enemy' as CreatureType,
    image_file: null
  });

  useEffect(() => {
    if (preset) {
      setName(preset.name + ' - Copy');
      // For using a preset, we don't set the background image file since it's an existing URL
      // Users can upload a new file to replace it
      setBackgroundImageFile(null);
      setCreatures([...preset.creatures]);
    }
  }, [preset]);

  if (!isOpen || !preset) return null;

  const handleAddCreature = async () => {
    if (!newCreature.name.trim()) {
      setError('Creature name is required');
      return;
    }

    // Upload creature image if provided
    let imageUrl = undefined;
    if (newCreature.image_file) {
      try {
        const uploadResult = await uploadAPI.uploadImage(newCreature.image_file);
        imageUrl = uploadResult.url;
      } catch (error) {
        console.warn(`Failed to upload image for ${newCreature.name}:`, error);
      }
    } else if (newCreature.name && newCreature.name.trim() !== '') {
      // Auto-fetch image from creature database if no file uploaded
      try {
        console.log('Fetching image for creature:', newCreature.name);
        const response = await fetch(`${getApiBaseUrl()}/api/creature-images/get_creature_image?name=${encodeURIComponent(newCreature.name)}&creature_type=${newCreature.creature_type}`);
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

    const creature: CreateCreature = {
      name: newCreature.name,
      initiative: newCreature.initiative,
      creature_type: newCreature.creature_type,
      image_url: imageUrl
    };

    setCreatures([...creatures, creature]);
    setNewCreature({
      name: '',
      initiative: 10,
      creature_type: 'enemy' as CreatureType,
      image_file: null
    });
    setError('');
  };

  const handleRemoveCreature = (index: number) => {
    setCreatures(creatures.filter((_, i) => i !== index));
  };

  const handleUpdateCreature = (index: number, field: keyof CreateCreature, value: any) => {
    const updatedCreatures = [...creatures];
    updatedCreatures[index] = { ...updatedCreatures[index], [field]: value };
    setCreatures(updatedCreatures);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Encounter name is required');
      return;
    }

    if (creatures.length === 0) {
      setError('At least one creature is required');
      return;
    }

    // Upload background image if a new file was provided
    let backgroundImageUrl = preset.background_image; // Use the original preset's image by default
    if (backgroundImageFile) {
      try {
        const uploadResult = await uploadAPI.uploadImage(backgroundImageFile);
        backgroundImageUrl = uploadResult.url;
      } catch (error) {
        console.warn('Failed to upload background image:', error);
      }
    }

    const encounterData: CreateEncounter = {
      name: name.trim(),
      background_image: backgroundImageUrl,
      creatures
    };

    onSubmit(encounterData);
    handleClose();
  };

  const handleClose = () => {
    setName('');
    setBackgroundImageFile(null);
    setCreatures([]);
    setNewCreature({
      name: '',
      initiative: 10,
      creature_type: 'enemy' as CreatureType,
      image_file: null
    });
    setError('');
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold">Use Preset: {preset.name}</h2>
            {preset.description && (
              <p className="text-gray-400 text-sm mt-1">{preset.description}</p>
            )}
          </div>
          <button onClick={handleClose} className="text-gray-400 hover:text-white">
            ✕
          </button>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 mb-4">
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="form-group">
            <label htmlFor="encounterName" className="form-label">
              Encounter Name *
            </label>
            <input
              type="text"
              id="encounterName"
              className="form-input"
              placeholder="Enter encounter name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="encounterBackground" className="form-label">
              Background Image {preset.background_image && '(Replace original)'}
            </label>
            <input
              type="file"
              id="encounterBackground"
              className="form-input"
              accept="image/*"
              onChange={(e) => setBackgroundImageFile(e.target.files?.[0] || null)}
            />
            {preset.background_image && !backgroundImageFile && (
              <div className="mt-2">
                <p className="text-sm text-gray-400 mb-2">
                  Current background: {preset.background_image.split('/').pop()}
                </p>
                <img 
                  src={preset.background_image} 
                  alt="Current background"
                  className="w-full h-24 object-cover rounded border border-gray-600"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}
            {backgroundImageFile && (
              <div className="mt-2">
                <p className="text-sm text-gray-400 mb-2">New background preview:</p>
                <img 
                  src={URL.createObjectURL(backgroundImageFile)} 
                  alt="New background preview"
                  className="w-full h-24 object-cover rounded border border-gray-600"
                  onError={(e) => { e.currentTarget.style.display = 'none'; }}
                />
              </div>
            )}
          </div>

          {/* Creatures Section */}
          <div className="border-t border-gray-600 pt-6">
            <h3 className="text-lg font-semibold mb-4">Creatures (From Preset)</h3>
            
            {/* Existing Creatures */}
            {creatures.length > 0 && (
              <div className="space-y-2 mb-6">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Creatures from Preset:</h4>
                {creatures.map((creature, index) => (
                  <div key={index} className={`initiative-row creature-${creature.creature_type}`}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Creature name"
                      value={creature.name}
                      onChange={(e) => handleUpdateCreature(index, 'name', e.target.value)}
                    />
                    <input
                      type="number"
                      className="form-input"
                      placeholder="Initiative"
                      min="0"
                      max="100"
                      value={creature.initiative}
                      onChange={(e) => handleUpdateCreature(index, 'initiative', parseInt(e.target.value) || 0)}
                    />
                    <select
                      className="form-input"
                      value={creature.creature_type}
                      onChange={(e) => handleUpdateCreature(index, 'creature_type', e.target.value as CreatureType)}
                    >
                      <option value="enemy">Enemy</option>
                      <option value="player">Player</option>
                      <option value="ally">Ally</option>
                      <option value="other">Other</option>
                    </select>
                    <div className="flex items-center gap-2 flex-1">
                      {creature.image_url && (
                        <img 
                          src={creature.image_url} 
                          alt={creature.name}
                          className="w-12 h-12 rounded object-cover border border-gray-600"
                          onError={(e) => { e.currentTarget.style.display = 'none'; }}
                        />
                      )}
                      <span className="text-xs text-gray-400 flex-1">
                        {creature.image_url ? 'Has image' : 'No image'}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveCreature(index)}
                      className="btn btn-danger btn-sm"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Add Additional Creature Form */}
            <div className="glass-light p-4">
              <h4 className="font-medium mb-3">Add Additional Creature</h4>
              <div className="initiative-row mb-3">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Creature name"
                  value={newCreature.name}
                  onChange={(e) => setNewCreature({ ...newCreature, name: e.target.value })}
                />
                <input
                  type="number"
                  className="form-input"
                  placeholder="Initiative"
                  min="0"
                  max="100"
                  value={newCreature.initiative}
                  onChange={(e) => setNewCreature({ ...newCreature, initiative: parseInt(e.target.value) || 0 })}
                />
                <select
                  className="form-input"
                  value={newCreature.creature_type}
                  onChange={(e) => setNewCreature({ ...newCreature, creature_type: e.target.value as CreatureType })}
                >
                  <option value="enemy">Enemy</option>
                  <option value="player">Player</option>
                  <option value="ally">Ally</option>
                  <option value="other">Other</option>
                </select>
                <input
                  type="file"
                  className="form-input"
                  accept="image/*"
                  title="Upload creature image"
                  onChange={(e) => setNewCreature({ ...newCreature, image_file: e.target.files?.[0] || null })}
                />
                <button
                  type="button"
                  onClick={handleAddCreature}
                  className="btn btn-secondary btn-sm"
                >
                  Add
                </button>
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn btn-primary flex-1">
              Create Encounter from Preset
            </button>
            <button type="button" onClick={handleClose} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UsePresetModal;