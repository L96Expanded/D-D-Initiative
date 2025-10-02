import React, { createContext, useContext, useReducer, useEffect } from 'react';
import type { AuthContextType, User, LoginData, RegisterData } from '../types';
import { authAPI } from '../utils/api';
import { storage } from '../utils/helpers';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'SET_LOADING'; payload: boolean };

const initialState: AuthState = {
  user: null,
  token: null,
  loading: true,
};

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        loading: false,
      };
    case 'LOGIN_FAILURE':
      return { ...state, user: null, token: null, loading: false };
    case 'LOGOUT':
      return { ...state, user: null, token: null, loading: false };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Initialize auth state from localStorage
  useEffect(() => {
    const token = storage.get('token');
    const userString = storage.get('user');
    
    if (token && userString) {
      try {
        const user = JSON.parse(userString);
        dispatch({ type: 'LOGIN_SUCCESS', payload: { user, token } });
      } catch {
        storage.remove('token');
        storage.remove('user');
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    } else {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authAPI.login({ email, password });
      
      // Store in localStorage
      storage.set('token', response.access_token);
      storage.set('user', JSON.stringify(response.user));
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: response.user, token: response.access_token },
      });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  const register = async (
    email: string,
    password: string,
    confirmPassword: string
  ): Promise<void> => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const response = await authAPI.register({
        email,
        password,
        confirm_password: confirmPassword,
      });
      
      // Store in localStorage
      storage.set('token', response.access_token);
      storage.set('user', JSON.stringify(response.user));
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user: response.user, token: response.access_token },
      });
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' });
      throw error;
    }
  };

  const logout = (): void => {
    storage.remove('token');
    storage.remove('user');
    dispatch({ type: 'LOGOUT' });
    
    // Call logout API endpoint (optional, for token invalidation)
    authAPI.logout().catch(() => {
      // Silently fail if logout API call fails
    });
  };

  const value: AuthContextType = {
    user: state.user,
    token: state.token,
    login,
    register,
    logout,
    loading: state.loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};