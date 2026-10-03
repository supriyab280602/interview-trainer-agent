'use client';

import { api } from './api';

export const resumeService = {
  async upload(file: File) {
    return api.upload<any>('/api/resume/upload', file);
  },

  async get() {
    return api.get<any>('/api/resume');
  },

  async delete() {
    return api.delete<any>('/api/resume');
  },
};

// Add missing delete method inside the api object in frontend/services/api.ts
// Wait, we can implement it here or inside api.ts. Let's make sure we update api.ts if we haven't added delete.
