'use client';

import { api } from './api';

export interface InterviewStartPayload {
  profile_name: string;
  interview_type: string;
  difficulty: string;
  length: number;
}

export interface AnswerSubmitPayload {
  interview_id: string;
  question_index: number;
  answer: string;
}

export const interviewService = {
  async start(payload: InterviewStartPayload) {
    return api.post<any>('/api/interview/start', payload);
  },

  async submitAnswer(payload: AnswerSubmitPayload) {
    return api.post<any>('/api/interview/answer', payload);
  },

  async end(interviewId: string) {
    return api.post<any>(`/api/interview/end?interview_id=${interviewId}`, {});
  },

  async getHistory() {
    return api.get<any[]>('/api/interview/history');
  },

  async getDownloadUrl(interviewId: string): Promise<string> {
    return `http://localhost:8000/api/interview/${interviewId}/report`;
  },
};
