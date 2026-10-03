'use client';

import { api } from './api';

export const authService = {
  async signup(payload: any) {
    return api.post('/api/signup', payload);
  },

  async login(payload: any) {
    const res = await api.post<{ session_id: string; user: any }>('/api/login', payload);
    if (res.session_id) {
      localStorage.setItem('inferexa_session_id', res.session_id);
    }
    return res;
  },

  async logout() {
    try {
      await api.post('/api/logout', {});
    } finally {
      localStorage.removeItem('inferexa_session_id');
    }
  },

  async getProfile() {
    return api.get<any>('/api/profile');
  },

  async updateProfile(payload: { profile_name: string; experience_level: string; target_role: string }) {
    return api.put<any>('/api/profile', payload);
  },
};
