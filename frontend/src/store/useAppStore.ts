import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Learner, LearnerGoal } from '../types';

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
  token: string | null;
  currentLearner: Learner | null;
  isAuthenticated: boolean;
  setAuth: (token: string, learner: Learner) => void;
  setCurrentLearner: (learner: Learner | null) => void;
  goals: LearnerGoal[];
  activeGoal: LearnerGoal | null;
  activeGoalVersion: number;
  setGoals: (goals: LearnerGoal[]) => void;
  setActiveGoal: (goal: LearnerGoal | null) => void;
  triggerGoalUpdate: () => void;
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
      token: null,
      currentLearner: null,
      isAuthenticated: false,
      goals: [],
      activeGoal: null,
      activeGoalVersion: 0,
      setGoals: (goals) => {
        if (!goals || goals.length === 0) {
          const currentActive = get().activeGoal;
          if (currentActive) {
            set({ goals: [{ ...currentActive, status: 'active' }] });
          } else {
            set({ goals: [], activeGoal: null });
          }
          return;
        }

        const currentActive = get().activeGoal;
        let matchedActive = currentActive ? goals.find(g => g.id === currentActive.id) : null;
        if (!matchedActive) {
          matchedActive = goals.find(g => g.status === 'active') || goals[0];
        }

        const normalizedGoals = goals.map(g => ({
          ...g,
          status: (matchedActive && g.id === matchedActive.id) ? 'active' : 'inactive'
        }));

        set({
          goals: normalizedGoals,
          activeGoal: matchedActive ? { ...matchedActive, status: 'active' } : null
        });
      },
      setActiveGoal: (goal) => {
        if (!goal) {
          set((state) => ({ activeGoal: null, goals: [], activeGoalVersion: state.activeGoalVersion + 1 }));
          return;
        }

        set((state) => {
          let updatedGoals = state.goals;
          const exists = state.goals.some(g => g.id === goal.id);
          if (!exists) {
            updatedGoals = [{ ...goal, status: 'active' }, ...state.goals];
          }

          const normalized = updatedGoals.map(g => ({
            ...g,
            status: g.id === goal.id ? 'active' : 'inactive'
          }));

          return {
            activeGoal: { ...goal, status: 'active' },
            goals: normalized,
            activeGoalVersion: state.activeGoalVersion + 1
          };
        });
      },
      triggerGoalUpdate: () => set((state) => ({ activeGoalVersion: state.activeGoalVersion + 1 })),
      setAuth: (token, learner) => {
        try {
          localStorage.setItem('neuronpath-token', token);
        } catch (e) {}
        set({ 
          token, 
          currentLearner: learner, 
          isAuthenticated: true, 
          isOnboarded: true 
        });
      },
      setCurrentLearner: (learner) => set({ 
        currentLearner: learner,
        isAuthenticated: !!learner
      }),
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
      logout: () => {
        try {
          localStorage.removeItem('neuronpath-token');
        } catch (e) {}
        set({ 
          token: null, 
          currentLearner: null, 
          isAuthenticated: false, 
          isOnboarded: false,
          goals: [],
          activeGoal: null,
          activeGoalVersion: 0
        });
      },
    }),
    {
      name: 'neuronpath-storage',
      partialize: (state) => ({
        token: state.token,
        currentLearner: state.currentLearner,
        isAuthenticated: state.isAuthenticated,
        isOnboarded: state.isOnboarded,
        theme: state.theme,
        goals: state.goals,
        activeGoal: state.activeGoal,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          applyThemeToDom(state.theme || 'light');
          if (state.token && state.currentLearner) {
            state.isAuthenticated = true;
          }
          if (state.activeGoal && (!state.goals || state.goals.length === 0)) {
            state.goals = [{ ...state.activeGoal, status: 'active' }];
          }
        }
      },
    }
  )
);
