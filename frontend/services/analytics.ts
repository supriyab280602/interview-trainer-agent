'use client';

import { api } from './api';

export const analyticsService = {
  async getFullMetrics() {
    return api.get<any>('/api/analytics');
  },

  async getDashboardSummary() {
    return api.get<any>('/api/dashboard');
  },
};
