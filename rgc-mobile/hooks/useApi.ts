import { useState, useCallback } from 'react';
import * as SecureStore from 'expo-secure-store';

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE' | 'PUT';
  body?: object;
  token?: string | null;
}

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const call = useCallback(async <T = any>(url: string, options: ApiOptions = {}): Promise<T | null> => {
    setLoading(true);
    setError(null);
    try {
      const token = options.token || await SecureStore.getItemAsync('access_token');
      const headers: HeadersInit = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(url, {
        method: options.method || 'GET',
        headers,
        body: options.body ? JSON.stringify(options.body) : undefined,
      });

      const data = await response.json();

      if (!response.ok) {
        const msg = typeof data === 'string' ? data
          : data.detail || data.error || data.message
          || Object.values(data).flat().join(' ')
          || 'Request failed';
        throw new Error(msg);
      }

      return data as T;
    } catch (e: any) {
      const msg = e.message || 'Network error';
      setError(msg);
      throw new Error(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  return { call, loading, error, setError };
}
