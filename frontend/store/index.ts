'use client';

import { create } from 'zustand';
import { authService } from '../services/auth';

interface AuthState {
  user: any | null;
  sessionId: string | null;
  isAuthenticated: boolean;
  activeProfile: string | null;
  streakCount: number;
  setAuth: (user: any, sessionId: string) => void;
  clearAuth: () => void;
  fetchProfile: () => Promise<void>;
}

interface InterviewState {
  currentInterview: any | null;
  activeQuestion: string | null;
  questionIndex: number;
  totalQuestions: number;
  answers: Record<number, string>;
  setInterview: (interview: any) => void;
  setAnswer: (index: number, text: string) => void;
  clearInterview: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  sessionId: typeof window !== 'undefined' ? localStorage.getItem('inferexa_session_id') : null,
  isAuthenticated: typeof window !== 'undefined' ? !!localStorage.getItem('inferexa_session_id') : false,
  activeProfile: null,
  streakCount: 5, // Simulated default streak

  setAuth: (user, sessionId) => {
    localStorage.setItem('inferexa_session_id', sessionId);
    set({ user, sessionId, isAuthenticated: true, activeProfile: user?.active_profile_name });
  },

  clearAuth: () => {
    localStorage.removeItem('inferexa_session_id');
    set({ user: null, sessionId: null, isAuthenticated: false, activeProfile: null });
  },

  fetchProfile: async () => {
    try {
      const user = await authService.getProfile();
      set({ user, isAuthenticated: true, activeProfile: user?.active_profile_name });
    } catch (_) {
      // Clear session if profile call fails
      localStorage.removeItem('inferexa_session_id');
      set({ user: null, sessionId: null, isAuthenticated: false, activeProfile: null });
    }
  },
}));

export const useInterviewStore = create<InterviewState>((set) => ({
  currentInterview: null,
  activeQuestion: null,
  questionIndex: 0,
  totalQuestions: 5,
  answers: {},

  setInterview: (interview) => {
    const questions = interview?.questions || [];
    set({
      currentInterview: interview,
      activeQuestion: questions[0] || null,
      questionIndex: 0,
      totalQuestions: questions.length || 5,
      answers: {},
    });
  },

  setAnswer: (index, text) => {
    set((state) => ({
      answers: { ...state.answers, [index]: text },
    }));
  },

  clearInterview: () => {
    set({
      currentInterview: null,
      activeQuestion: null,
      questionIndex: 0,
      totalQuestions: 5,
      answers: {},
    });
  },
}));
