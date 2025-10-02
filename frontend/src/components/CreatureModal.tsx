import React, { useState } from 'react';
import Modal from './Modal';
import type { CreateCreature, CreatureType } from '../types';

interface CreatureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateCreature) => void;
  initialData?: CreateCreature | null;
}

const CreatureModal: React.FC<CreatureModalProps> = ({ isOpen, onClose, onSubmit, initialData }) => {
  const [name, setName] = useState(initialData?.name || '');
  const [initiative, setInitiative] = useState(initialData?.initiative || 0);
  const [creatureType, setCreatureType] = useState<CreatureType>(initialData?.creature_type || 'enemy');
  const [imageUrl, setImageUrl] = useState(initialData?.image_url || '');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Creature name is required');
      return;
    }
    if (initiative < 0) {
      setError('Initiative must be 0 or greater');
      return;
    }
    onSubmit({ name, initiative, creature_type: creatureType, image_url: imageUrl });
    setName('');
    setInitiative(0);
    setCreatureType('enemy');
    setImageUrl('');
    setError(null);
    onClose();
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
          <input
            type="text"
            className="w-full px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
            value={imageUrl}
            onChange={e => setImageUrl(e.target.value)}
            placeholder="Optional"
          />
        </label>
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <button type="submit" className="btn btn-primary w-full">
          {initialData ? 'Save Changes' : 'Add Creature'}
        </button>
      </form>
    </Modal>
  );
};

export default CreatureModal;
