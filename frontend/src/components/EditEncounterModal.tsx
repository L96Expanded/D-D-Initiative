import * as React from 'react';
import { useState, useEffect } from 'react';
import { uploadAPI } from '../utils/api';
import type { Encounter, UpdateEncounter, CreateCreature, CreatureType } from '../types';

interface EditEncounterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (id: string, data: UpdateEncounter, creatures: CreateCreature[]) => void;
  encounterId: string;
  initialData: Encounter;
}

interface Initiative {
  id?: string; // for existing creatures
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
  image_file?: File;
  isNew?: boolean; // to track new vs existing creatures
}

const EditEncounterModal: React.FC<EditEncounterModalProps> = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  encounterId,
  initialData 
}) => {
  const [encounterName, setEncounterName] = useState(initialData?.name || '');
  const [backgroundImageFile, setBackgroundImageFile] = useState<File | null>(null);
  const [initiatives, setInitiatives] = useState<Initiative[]>([]);
  const [formError, setFormError] = useState<string | null>(null);

  // Initialize form when modal opens or data changes
  useEffect(() => {
    if (initialData && isOpen) {
      setEncounterName(initialData.name);
      setBackgroundImageFile(null); // Reset file input for new editing session
      
      // Convert existing creatures to initiative format
      const existingInitiatives: Initiative[] = initialData.creatures.map(creature => ({
        id: creature.id,
        name: creature.name,
        initiative: creature.initiative,
        creature_type: creature.creature_type,
        image_url: creature.image_url,
        isNew: false
      }));
      
      // If no creatures exist, add one empty row
      if (existingInitiatives.length === 0) {
        existingInitiatives.push({
          name: '',
          initiative: 0,
          creature_type: 'enemy',
          isNew: true
        });
      }
      
      setInitiatives(existingInitiatives);
    }
  }, [initialData, isOpen]);

  const handleInitiativeChange = (idx: number, field: keyof Initiative, value: string | number | File) => {
    const updated = [...initiatives];
    if (field === 'initiative') {
      updated[idx][field] = Number(value);
    } else if (field === 'image_file') {
      updated[idx][field] = value as File;
      // Clear the image_url when a new file is selected
      updated[idx].image_url = undefined;
    } else if (field === 'creature_type') {
      updated[idx][field] = value as CreatureType;
    } else if (field === 'name') {
      updated[idx][field] = value as string;
    } else if (field === 'image_url') {
      updated[idx][field] = value as string;
    }
    setInitiatives(updated);
  };

  const handleAddInitiative = () => {
    setInitiatives([...initiatives, { 
      name: '', 
      initiative: 0, 
      creature_type: 'enemy',
      isNew: true 
    }]);
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

    try {
      // Upload background image if provided
      let backgroundImageUrl = initialData?.background_image; // Keep existing background if no new file
      if (backgroundImageFile) {
        try {
          const uploadResult = await uploadAPI.uploadImage(backgroundImageFile);
          backgroundImageUrl = uploadResult.url;
        } catch (error) {
          console.error('Failed to upload background image:', error);
          setFormError('Failed to upload background image. Please try again.');
          return;
        }
      }

      // Process creatures and handle file uploads
      const creatures: CreateCreature[] = [];
      
      for (const init of initiatives) {
        let imageUrl = init.image_url;
        
        // If a file was uploaded, upload it first and get the URL
        if (init.image_file) {
          try {
            const uploadResult = await uploadAPI.uploadImage(init.image_file);
            imageUrl = uploadResult.url;
          } catch (error) {
            console.error('Failed to upload image for creature:', init.name, error);
            setFormError(`Failed to upload image for ${init.name}. Please try again.`);
            return;
          }
        } else if (init.name && init.name.trim() !== '' && !init.image_url) {
          // Auto-fetch image from creature database if no file uploaded and no existing image
          try {
            console.log('Fetching image for creature:', init.name);
            const response = await fetch(`http://localhost:8000/api/creature-images/get_creature_image?name=${encodeURIComponent(init.name)}&creature_type=${init.creature_type}`);
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
        
        creatures.push({
          name: init.name,
          initiative: init.initiative,
          creature_type: init.creature_type,
          image_url: imageUrl
        });
      }

      const updateData: UpdateEncounter = {
        name: encounterName,
        background_image: backgroundImageUrl || undefined
      };

      onSubmit(encounterId, updateData, creatures);
      setFormError(null);
      onClose();
    } catch (error) {
      console.error('Error submitting form:', error);
      setFormError('Failed to save encounter. Please try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-3xl">
        <h3 className="text-xl font-bold mb-4 text-center">
          Edit Encounter
        </h3>
        <button
          className="absolute top-4 right-4 btn btn-secondary btn-sm"
          onClick={onClose}
          aria-label="Close modal"
        >
          &times;
        </button>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-left mb-2">Encounter Name</label>
            <input
              type="text"
              className="w-full px-4 py-2 rounded-sm bg-gray-900 text-white border border-gray-700"
              value={encounterName}
              onChange={e => setEncounterName(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-left mb-2">Background Image</label>
            <input
              type="file"
              className="w-full px-4 py-2 rounded-sm bg-gray-900 text-white border border-gray-700"
              accept="image/*"
              onChange={e => setBackgroundImageFile(e.target.files?.[0] || null)}
            />
            <div className="mt-2 text-sm text-gray-400">
              {initialData?.background_image ? 'Current background will be kept if no new file is selected' : 'No background image currently set'}
            </div>
            {backgroundImageFile && (
              <div className="mt-2">
                <img 
                  src={URL.createObjectURL(backgroundImageFile)} 
                  alt="Background preview" 
                  className="w-full h-32 object-cover rounded border border-gray-700"
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
                  {(init.image_url || init.image_file) && (
                    <img 
                      src={init.image_file ? URL.createObjectURL(init.image_file) : init.image_url} 
                      alt={`${init.name} preview`}
                      className="w-8 h-8 object-cover rounded border border-gray-500"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  )}
                  {init.image_url && !init.image_file && (
                    <span className="text-xs text-gray-400">Current image kept</span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {formError && (
            <div className="modal-error text-red-400 text-sm bg-red-500/20 border border-red-500 rounded p-3">
              {formError}
            </div>
          )}

          <div className="modal-buttons flex gap-3 pt-4">
            <button type="submit" className="btn btn-primary flex-1">
              Save Changes
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

export default EditEncounterModal;