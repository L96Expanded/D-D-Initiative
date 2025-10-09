import * as React from 'react';
import { useState } from 'react';
import { uploadAPI } from '../utils/api';
import type { CreatePreset, CreateCreature, CreatureType } from '../types';

interface PresetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreatePreset) => void;
}

const PresetModal: React.FC<PresetModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [backgroundImageFile, setBackgroundImageFile] = useState<File | null>(null);
  const [creatures, setCreatures] = useState<CreateCreature[]>([]);
  const [error, setError] = useState('');

  const [newCreature, setNewCreature] = useState({
    name: '',
    initiative: 10,
    creature_type: 'enemy' as CreatureType,
    image_file: null as File | null
  });

  if (!isOpen) return null;

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Preset name is required');
      return;
    }

    // Upload background image if provided
    let backgroundImageUrl = undefined;
    if (backgroundImageFile) {
      try {
        const uploadResult = await uploadAPI.uploadImage(backgroundImageFile);
        backgroundImageUrl = uploadResult.url;
      } catch (error) {
        console.warn('Failed to upload background image:', error);
      }
    }

    const presetData: CreatePreset = {
      name: name.trim(),
      description: description.trim() || undefined,
      background_image: backgroundImageUrl,
      creatures
    };

    onSubmit(presetData);
    
    // Reset form
    setName('');
    setDescription('');
    setBackgroundImageFile(null);
    setCreatures([]);
    setNewCreature({
      name: '',
      initiative: 10,
      creature_type: 'enemy' as CreatureType,
      image_file: null
    });
  };

  const handleClose = () => {
    setName('');
    setDescription('');
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
          <h2 className="text-2xl font-bold">Create New Preset</h2>
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
            <label htmlFor="presetName" className="form-label">
              Preset Name *
            </label>
            <input
              type="text"
              id="presetName"
              className="form-input"
              placeholder="Enter preset name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="presetDescription" className="form-label">
              Description
            </label>
            <textarea
              id="presetDescription"
              className="form-input"
              placeholder="Enter preset description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className="form-group">
            <label htmlFor="presetBackground" className="form-label">
              Background Image
            </label>
            <input
              type="file"
              id="presetBackground"
              className="form-input"
              accept="image/*"
              onChange={(e) => setBackgroundImageFile(e.target.files?.[0] || null)}
            />
          </div>

          {/* Creatures Section */}
          <div className="border-t border-gray-600 pt-6">
            <h3 className="text-lg font-semibold mb-4">Creatures</h3>
            
            {/* Add Creature Form */}
            <div className="glass-light p-4 mb-4">
              <h4 className="font-medium mb-3">Add Creature</h4>
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

            {/* Creatures List */}
            {creatures.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-medium">Preset Creatures ({creatures.length})</h4>
                {creatures.map((creature, index) => (
                  <div key={index} className={`glass-light p-3 flex items-center justify-between creature-${creature.creature_type}`}>
                    <div className="flex items-center gap-4">
                      <span className="font-medium">{creature.name}</span>
                      <span className="text-sm text-gray-400">Initiative: {creature.initiative}</span>
                      <span className="text-sm text-gray-400 capitalize">{creature.creature_type}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveCreature(index)}
                      className="text-red-400 hover:text-red-300"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex gap-3 pt-4">
            <button type="submit" className="btn btn-primary flex-1">
              Create Preset
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

export default PresetModal;