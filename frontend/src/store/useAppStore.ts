import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Learner } from '../types';

export const applyThemeToDom = (theme: 'light' | 'dark') => {
  if (typeof document !== 'undefined') {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.setAttribute('data-theme', 'dark');
      try {
        localStorage.setItem('neuronpath-theme', 'dark');
      } catch (e) {}
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.setAttribute('data-theme', 'light');
      try {
        localStorage.setItem('neuronpath-theme', 'light');
      } catch (e) {}
    }
  }
};

const getInitialTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined') {
    try {
      const direct = localStorage.getItem('neuronpath-theme');
      if (direct === 'dark' || direct === 'light') return direct;
      const stored = localStorage.getItem('neuronpath-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed?.state?.theme === 'dark') return 'dark';
      }
    } catch (e) {}
  }
  return 'light';
};

interface AppState {
  currentLearner: Learner | null;
  setCurrentLearner: (learner: Learner | null) => void;
  isOnboarded: boolean;
  setOnboarded: (status: boolean) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  logout: () => void;
}

const initialTheme = getInitialTheme();
applyThemeToDom(initialTheme);

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      currentLearner: null,
      setCurrentLearner: (learner) => set({ currentLearner: learner }),
      isOnboarded: false,
      setOnboarded: (status) => set({ isOnboarded: status }),
      sidebarOpen: false,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      theme: initialTheme,
      toggleTheme: () => {
        const current = get().theme;
        const nextTheme = current === 'dark' ? 'light' : 'dark';
        applyThemeToDom(nextTheme);
        set({ theme: nextTheme });
      },
      setTheme: (theme) => {
        applyThemeToDom(theme);
        set({ theme });
      },
      logout: () => set({ currentLearner: null, isOnboarded: false }),
    }),
    {
      name: 'neuronpath-storage',
      partialize: (state) => ({
        currentLearner: state.currentLearner,
        isOnboarded: state.isOnboarded,
        theme: state.theme,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          applyThemeToDom(state.theme || 'light');
        }
      },
    }
  )
);
