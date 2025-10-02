import React, { useState } from 'react';
import Modal from './Modal';
import type { CreateEncounter, EncounterSummary } from '../types';

interface EncounterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateEncounter) => void;
  initialData?: EncounterSummary | null;
}

const EncounterModal: React.FC<EncounterModalProps> = ({ isOpen, onClose, onSubmit, initialData }) => {
  const [name, setName] = useState(initialData?.name || '');
  const [backgroundImage, setBackgroundImage] = useState(initialData?.background_image || '');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Encounter name is required');
      return;
    }
    onSubmit({ name, background_image: backgroundImage, creatures: [] });
    setName('');
    setBackgroundImage('');
    setError(null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={initialData ? 'Edit Encounter' : 'Create Encounter'}>
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
          Background Image URL
          <input
            type="text"
            className="w-full px-4 py-2 rounded-lg bg-gray-900 text-white border border-gray-700 mt-1"
            value={backgroundImage}
            onChange={e => setBackgroundImage(e.target.value)}
            placeholder="Optional"
          />
        </label>
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <button type="submit" className="btn btn-primary w-full">
          {initialData ? 'Save Changes' : 'Create Encounter'}
        </button>
      </form>
    </Modal>
  );
};

export default EncounterModal;
