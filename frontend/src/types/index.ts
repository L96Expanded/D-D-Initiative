import { ReactNode } from 'react';

export type CreatureType = 'player' | 'enemy' | 'ally' | 'other';

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Creature {
  id: string;
  encounter_id: string;
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
  created_at: string;
}

export interface CreateCreature {
  name: string;
  initiative: number;
  creature_type: CreatureType;
  image_url?: string;
}

export interface UpdateCreature {
  name?: string;
  initiative?: number;
  creature_type?: CreatureType;
  image_url?: string;
}

export interface Encounter {
  id: string;
  user_id: string;
  name: string;
  background_image?: string;
  created_at: string;
  updated_at: string;
  creatures: Creature[];
}

export interface EncounterSummary {
  id: string;
  name: string;
  background_image?: string;
  created_at: string;
  creature_count: number;
}

export interface CreateEncounter {
  name: string;
  background_image?: string;
  creatures: CreateCreature[];
}

export interface UpdateEncounter {
  name?: string;
  background_image?: string;
}

// Preset types - for reusable encounter templates
export interface Preset {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  background_image?: string;
  created_at: string;
  updated_at: string;
  creatures: CreateCreature[];
}

export interface PresetSummary {
  id: string;
  name: string;
  description?: string;
  background_image?: string;
  created_at: string;
  creature_count: number;
}

export interface CreatePreset {
  name: string;
  description?: string;
  background_image?: string;
  creatures: CreateCreature[];
}

export interface UpdatePreset {
  name?: string;
  description?: string;
  background_image?: string;
}

export interface FileUpload {
  filename: string;
  url: string;
}

export interface ApiError {
  detail: string;
  error_code?: string;
}

// Context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export interface EncounterContextType {
  encounters: EncounterSummary[];
  currentEncounter: Encounter | null;
  loading: boolean;
  error: string | null;
  fetchEncounters: () => Promise<void>;
  fetchEncounter: (id: string) => Promise<void>;
  createEncounter: (data: CreateEncounter) => Promise<void>;
  updateEncounter: (id: string, data: UpdateEncounter) => Promise<void>;
  deleteEncounter: (id: string) => Promise<void>;
  addCreature: (encounterId: string, creature: CreateCreature) => Promise<void>;
  updateCreature: (id: string, data: UpdateCreature) => Promise<void>;
  deleteCreature: (id: string) => Promise<void>;
}

// Component props
export interface CreatureCardProps {
  creature: Creature;
  isCurrent?: boolean;
  isNext?: boolean;
  onClick?: () => void;
}

export interface EncounterCardProps {
  encounter: EncounterSummary;
  onEdit: (encounter: EncounterSummary) => void;
  onDelete: (encounter: EncounterSummary) => void;
  onOpen: (encounter: EncounterSummary) => void;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}

export interface EncounterModalProps extends ModalProps {
  encounter?: Encounter | null;
  onSave: (data: CreateEncounter | UpdateEncounter) => Promise<void>;
}

export interface DeleteConfirmModalProps extends ModalProps {
  title: string;
  message: string;
  onConfirm: () => void;
}