import React, { ReactNode } from 'react';

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
      <div
        className={`glass-heavy p-8 relative shadow-lg rounded-xl w-full max-w-lg ${width || ''}`}
        role="dialog"
        aria-modal="true"
      >
        {title && <h2 className="text-xl font-bold mb-4 text-center">{title}</h2>}
        <button
          className="absolute top-4 right-4 btn btn-secondary btn-sm"
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
