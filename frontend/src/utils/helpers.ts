import type { CreatureType } from '../types';

// Color mappings for creature types
export const getCreatureTypeColor = (type: CreatureType): string => {
  switch (type) {
    case 'player':
      return '#3b82f6'; // Blue
    case 'enemy':
      return '#dc2626'; // Red
    case 'ally':
      return '#16a34a'; // Green
    case 'other':
      return '#ffffff'; // White
    default:
      return '#ffffff';
  }
};

// Format date for display
export const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

// Validate email format
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

// Generate default image URL for creature type
export const getDefaultCreatureImage = (type: CreatureType): string => {
  return `/images/defaults/${type}.png`;
};

// Generate default background image
export const getDefaultBackgroundImage = (): string => {
  return '/images/backgrounds/default.jpg';
};

// Sort creatures by initiative (highest first)
export const sortCreaturesByInitiative = <T extends { initiative: number }>(creatures: T[]): T[] => {
  return [...creatures].sort((a, b) => b.initiative - a.initiative);
};

// Get next creature in initiative order
export const getNextCreatureIndex = (currentIndex: number, totalCreatures: number): number => {
  return (currentIndex + 1) % totalCreatures;
};

// Get previous creature in initiative order
export const getPreviousCreatureIndex = (currentIndex: number, totalCreatures: number): number => {
  return currentIndex === 0 ? totalCreatures - 1 : currentIndex - 1;
};

// Debounce function for search
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

// File size formatter
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Check if file is a valid image
export const isValidImageFile = (file: File): boolean => {
  const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
  return validTypes.includes(file.type);
};

// Generate unique ID (fallback for client-side)
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

// Local storage helpers
export const storage = {
  get: (key: string): string | null => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  
  set: (key: string, value: string): void => {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Silently fail if localStorage is not available
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch {
      // Silently fail if localStorage is not available
    }
  },
  
  clear: (): void => {
    try {
      localStorage.clear();
    } catch {
      // Silently fail if localStorage is not available
    }
  },
};