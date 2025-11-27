import axios from 'axios';
import type { 
  AuthResponse, 
  LoginData, 
  RegisterData, 
  User,
  Encounter,
  EncounterSummary,
  CreateEncounter,
  UpdateEncounter,
  Creature,
  CreateCreature,
  UpdateCreature,
  Preset,
  PresetSummary,
  CreatePreset,
  UpdatePreset,
  FileUpload
} from '../types';

interface ImportMetaEnv {
  VITE_API_URL?: string;
}
declare global {
  interface ImportMeta {
    env: ImportMetaEnv;
  }
}
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Log API URL for debugging - IMPORTANT: Check this in browser console!
console.log('='.repeat(60));
console.log('🔧 API CONFIGURATION');
console.log('='.repeat(60));
console.log('API Base URL:', API_BASE_URL);
console.log('Environment:', import.meta.env.MODE);
console.log('All Env Vars:', import.meta.env);
console.log('='.repeat(60));

// Helper function to get the API base URL for use in components
export const getApiBaseUrl = () => API_BASE_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Encounters API
export const encountersAPI = {
  getAll: async (): Promise<EncounterSummary[]> => {
    const response = await api.get<EncounterSummary[]>('/encounters');
    return response.data;
  },

  getById: async (id: string): Promise<Encounter> => {
    const response = await api.get<Encounter>(`/encounters/${id}`);
    return response.data;
  },

  create: async (data: CreateEncounter): Promise<Encounter> => {
    const response = await api.post<Encounter>('/encounters', data);
    return response.data;
  },

  update: async (id: string, data: UpdateEncounter): Promise<Encounter> => {
    const response = await api.put<Encounter>(`/encounters/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/encounters/${id}`);
  },

  addCreature: async (encounterId: string, data: CreateCreature): Promise<Creature> => {
    const response = await api.post<Creature>(`/encounters/${encounterId}/creatures`, data);
    return response.data;
  },
};

// Presets API
export const presetsAPI = {
  getAll: async (): Promise<PresetSummary[]> => {
    const response = await api.get<PresetSummary[]>('/presets');
    return response.data;
  },

  getById: async (id: string): Promise<Preset> => {
    const response = await api.get<Preset>(`/presets/${id}`);
    return response.data;
  },

  create: async (data: CreatePreset): Promise<Preset> => {
    const response = await api.post<Preset>('/presets', data);
    return response.data;
  },

  update: async (id: string, data: UpdatePreset): Promise<Preset> => {
    const response = await api.put<Preset>(`/presets/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/presets/${id}`);
  },
};

// Creatures API
export const creaturesAPI = {
  update: async (id: string, data: UpdateCreature): Promise<Creature> => {
    const response = await api.put<Creature>(`/creatures/${id}`, data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/creatures/${id}`);
  },
};

// File Upload API
export const uploadAPI = {
  uploadImage: async (file: File): Promise<FileUpload> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<FileUpload>('/upload/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  deleteImage: async (filename: string): Promise<void> => {
    await api.delete(`/upload/images/${filename}`);
  },
};

export default api;