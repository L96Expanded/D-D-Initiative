import * as React from 'react';
import { ReactNode } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  title?: string;
  width?: string;
}

const Modal: React.FC<ModalProps> = ({ isOpen, onClose, children, title, width }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50" style={{ zIndex: 9999 }}>
      <div
        className={`bg-gray-800 text-white p-8 relative shadow-lg rounded-xl w-full max-w-lg border border-gray-600 ${width || ''}`}
        role="dialog"
        aria-modal="true"
      >
        {title && <h2 className="text-xl font-bold mb-4 text-center">{title}</h2>}
        <button
          className="absolute top-4 right-4 text-gray-400 hover:text-white text-2xl"
          onClick={onClose}
          aria-label="Close modal"
        >
          &times;
        </button>
        {children}
      </div>
    </div>
  );
};

export default Modal;
