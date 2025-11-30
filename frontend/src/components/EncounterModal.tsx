import * as React from 'react';
import { useState } from 'react';
import { uploadAPI, getApiBaseUrl } from '../utils/api';
import type { CreateEncounter, EncounterSummary, CreateCreature, CreatureType } from '../types';

interface EncounterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateEncounter) => void;
  initialData?: EncounterSummary | null;
}

interface Initiative {
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_file?: File;
}

const EncounterModal: React.FC<EncounterModalProps> = ({ isOpen, onClose, onSubmit, initialData }) => {
  const [encounterName, setEncounterName] = useState(initialData?.name || '');
  const [backgroundImageFile, setBackgroundImageFile] = useState<File | null>(null);
  const [initiatives, setInitiatives] = useState<Initiative[]>([
    { name: '', initiative: 0, creature_type: 'enemy' }
  ]);
  const [formError, setFormError] = useState<string | null>(null);

  const handleInitiativeChange = (idx: number, field: keyof Initiative, value: string | number | File) => {
    const updated = [...initiatives];
    if (field === 'initiative') {
      updated[idx][field] = Number(value);
    } else if (field === 'image_file') {
      updated[idx][field] = value as File;
    } else if (field === 'creature_type') {
      updated[idx][field] = value as CreatureType;
    } else {
      updated[idx][field] = value as string;
    }
    setInitiatives(updated);
  };

  const handleAddInitiative = () => {
    setInitiatives([...initiatives, { name: '', initiative: 0, creature_type: 'enemy' }]);
  };

  const handleRemoveInitiative = (idx: number) => {
    if (initiatives.length > 1) {
      setInitiatives(initiatives.filter((_, i) => i !== idx));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!encounterName.trim()) {
      setFormError('Encounter name is required');
      return;
    }
    
    // Validate initiatives
    for (const init of initiatives) {
      if (!init.name.trim()) {
        setFormError('All creature names are required');
        return;
      }
    }

    setFormError(null);

    try {
      // Upload background image if provided
      let backgroundImageUrl = undefined;
      if (backgroundImageFile) {
        try {
          const uploadResult = await uploadAPI.uploadImage(backgroundImageFile);
          backgroundImageUrl = uploadResult.url;
        } catch (error) {
          console.warn('Failed to upload background image:', error);
          // Continue without background image rather than failing entirely
        }
      }

      // Upload image files and get URLs
      const creatures: CreateCreature[] = await Promise.all(
        initiatives.map(async (init) => {
          let imageUrl = undefined;
          
          if (init.image_file) {
            try {
              const uploadResult = await uploadAPI.uploadImage(init.image_file);
              imageUrl = uploadResult.url;
            } catch (error) {
              console.warn(`Failed to upload image for ${init.name}:`, error);
              // Continue without image rather than failing entirely
            }
          } else if (init.name && init.name.trim() !== '') {
            // Auto-fetch image from creature database if no file uploaded
            try {
              console.log('Fetching image for creature:', init.name);
              const response = await fetch(`${getApiBaseUrl()}/api/creature-images/get_creature_image?name=${encodeURIComponent(init.name)}&creature_type=${init.creature_type}`, {
                credentials: 'include'
              });
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

          return {
            name: init.name,
            initiative: init.initiative,
            creature_type: init.creature_type,
            image_url: imageUrl
          };
        })
      );

      const encounterData = { name: encounterName, background_image: backgroundImageUrl, creatures };
      console.log('EncounterModal submitting data:', JSON.stringify(encounterData, null, 2));
      onSubmit(encounterData);
      
      // Reset form
      setEncounterName('');
      setBackgroundImageFile(null);
      setInitiatives([{ name: '', initiative: 0, creature_type: 'enemy' }]);
      setFormError(null);
      onClose();
    } catch (error) {
      console.error('EncounterModal error:', error);
      setFormError('Failed to create encounter. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-4xl">
        <h3 className="text-xl font-bold mb-4 text-center">
          {initialData ? 'Edit Encounter' : 'Create New Encounter'}
        </h3>
        <button
          className="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl"
          onClick={onClose}
          aria-label="Close modal"
        >
          &times;
        </button>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="form-label">Encounter Name</label>
            <input
              type="text"
              className="form-input"
              value={encounterName}
              onChange={e => setEncounterName(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="form-label">Background Image</label>
            <input
              type="file"
              className="form-input"
              accept="image/*"
              onChange={e => setBackgroundImageFile(e.target.files?.[0] || null)}
            />
            {backgroundImageFile && (
              <div className="mt-2">
                <img 
                  src={URL.createObjectURL(backgroundImageFile)} 
                  alt="Background preview" 
                  className="w-full h-32 object-cover rounded border border-gray-600"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>

          <div>
            <h4 className="text-lg font-semibold mb-3">Creatures</h4>
            {initiatives.map((init, idx) => (
              <div key={idx} className="mb-3">
                <div className="initiative-row mb-2">
                  <input
                    type="text"
                    className="form-input"
                    placeholder="Name"
                    value={init.name}
                    onChange={e => handleInitiativeChange(idx, "name", e.target.value)}
                    required
                  />
                  <input
                    type="number"
                    className="form-input"
                    placeholder="0"
                    value={init.initiative}
                    onChange={e => handleInitiativeChange(idx, "initiative", e.target.value)}
                    required
                  />
                  <select
                    className="form-input"
                    value={init.creature_type}
                    onChange={e => handleInitiativeChange(idx, "creature_type", e.target.value)}
                  >
                    <option value="player">Player</option>
                    <option value="enemy">Enemy</option>
                    <option value="ally">Ally</option>
                    <option value="other">Other</option>
                  </select>
                  <button
                    type="button"
                    className="btn btn-danger btn-sm"
                    onClick={() => handleRemoveInitiative(idx)}
                    disabled={initiatives.length === 1}
                    title="Remove creature"
                  >
                    -
                  </button>
                  {idx === initiatives.length - 1 && (
                    <button
                      type="button"
                      className="btn btn-primary btn-sm"
                      onClick={handleAddInitiative}
                      title="Add creature"
                    >
                      +
                    </button>
                  )}
                </div>
                
                {/* Compact image upload row */}
                <div className="flex gap-2 items-center pl-2">
                  <input
                    type="file"
                    className="form-input text-sm"
                    accept="image/*"
                    onChange={e => e.target.files && handleInitiativeChange(idx, "image_file", e.target.files[0])}
                  />
                  {init.image_file && (
                    <img 
                      src={URL.createObjectURL(init.image_file)} 
                      alt={`${init.name} preview`}
                      className="w-12 h-12 object-cover rounded border border-gray-500"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {formError && (
            <div className="form-error bg-red-900 border border-red-500 rounded p-3">
              {formError}
            </div>
          )}

          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn btn-success flex-1">
              {initialData ? 'Save Changes' : 'Create Encounter'}
            </button>
            <button type="button" className="btn btn-secondary flex-1" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EncounterModal;
