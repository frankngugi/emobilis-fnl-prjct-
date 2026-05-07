import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import * as SecureStore from 'expo-secure-store';
import { ENDPOINTS } from '../constants/Api';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone: string;
  role: string;
  is_staff: boolean;
  is_superuser: boolean;
  profile_picture: string | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAdmin: boolean;
  isManager: boolean;
}

interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  password: string;
  confirm_password: string;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  async function loadStoredAuth() {
    try {
      const storedToken = await SecureStore.getItemAsync('access_token');
      const storedUser = await SecureStore.getItemAsync('user_data');
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        // Verify token is still valid by fetching profile
        await fetchProfile(storedToken);
      }
    } catch (e) {
      console.log('Auth load error:', e);
    } finally {
      setLoading(false);
    }
  }

  async function fetchProfile(accessToken: string) {
    try {
      const resp = await fetch(ENDPOINTS.PROFILE, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (resp.ok) {
        const userData = await resp.json();
        setUser(userData);
        await SecureStore.setItemAsync('user_data', JSON.stringify(userData));
      } else {
        // Token expired
        await clearAuth();
      }
    } catch (e) {
      console.log('Profile fetch error:', e);
    }
  }

  async function login(username: string, password: string) {
    const resp = await fetch(ENDPOINTS.LOGIN, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Login failed');
    await SecureStore.setItemAsync('access_token', data.access);
    await SecureStore.setItemAsync('refresh_token', data.refresh);
    await SecureStore.setItemAsync('user_data', JSON.stringify(data.user));
    setToken(data.access);
    setUser(data.user);
  }

  async function register(formData: RegisterData) {
    const resp = await fetch(ENDPOINTS.REGISTER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });
    const data = await resp.json();
    if (!resp.ok) {
      const msg = Object.values(data).flat().join(' ');
      throw new Error(msg || 'Registration failed');
    }
    await SecureStore.setItemAsync('access_token', data.access);
    await SecureStore.setItemAsync('refresh_token', data.refresh);
    await SecureStore.setItemAsync('user_data', JSON.stringify(data.user));
    setToken(data.access);
    setUser(data.user);
  }

  async function logout() {
    await clearAuth();
  }

  async function clearAuth() {
    await SecureStore.deleteItemAsync('access_token');
    await SecureStore.deleteItemAsync('refresh_token');
    await SecureStore.deleteItemAsync('user_data');
    setToken(null);
    setUser(null);
  }

  async function refreshUser() {
    if (token) await fetchProfile(token);
  }

  const isAdmin = !!(user?.is_superuser || user?.role === 'admin');
  const isManager = !!(user?.is_staff || user?.role === 'manager' || isAdmin);

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, refreshUser, isAdmin, isManager }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
