import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { Button } from '../components/ui/Button';
import { Card, CardContent } from '../components/ui/Card';
import { Map, MessageSquare, Brain, Sun, Moon, ArrowRight } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useAppStore();

  const isDark = theme === 'dark';

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col transition-colors">
      <header className="px-6 py-4 flex justify-between items-center bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-center gap-2.5 text-2xl font-black text-primary-600 dark:text-primary-400 tracking-tight">
          <Brain className="w-8 h-8" /> NeuronPath
        </div>
        <div className="flex gap-3 items-center">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
            aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {isDark ? (
              <Sun className="w-5 h-5 text-amber-400 hover:rotate-45 transition-transform" />
            ) : (
              <Moon className="w-5 h-5 text-slate-600 hover:-rotate-12 transition-transform" />
            )}
          </button>

          <Button onClick={() => navigate('/onboarding')}>Get Started</Button>
        </div>
      </header>
      
      <main className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <h1 className="text-5xl md:text-6xl font-black text-slate-900 dark:text-slate-100 mb-6 tracking-tight max-w-3xl">
          Your skills. <span className="text-primary-600 dark:text-primary-400">Your pace.</span> Your path.
        </h1>
        <p className="text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-12 max-w-2xl leading-relaxed">
          AI-powered personalized learning roadmaps tailored to your unique career goals, schedule, and learning style.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-16">
          <Button size="lg" onClick={() => navigate('/onboarding')} className="text-base px-8 font-semibold shadow-md inline-flex items-center gap-2">
            Start Your Learning Journey <ArrowRight className="w-4 h-4" />
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl w-full text-left">
          <Card>
            <CardContent className="pt-6">
              <Map className="w-10 h-10 text-primary-500 mb-4" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">Personalized Roadmaps</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Dynamic learning paths that decompose your career goals into granular, prerequisite-aware milestones.</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <MessageSquare className="w-10 h-10 text-primary-500 mb-4" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">AI Learning Coach</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Intelligent tutoring and continuous guidance tailored to your live progress whenever you need assistance.</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <Brain className="w-10 h-10 text-primary-500 mb-4" />
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-2">Skill Gap Analysis</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">Adaptive diagnostic assessments that benchmark your proficiencies against market standards.</p>
            </CardContent>
          </Card>
        </div>
      </main>
      
      <footer className="py-6 text-center text-xs text-slate-400 dark:text-slate-500 border-t border-slate-200 dark:border-slate-800">
        © 2026 NeuronPath. All rights reserved. Personalized AI-driven continuous learning.
      </footer>
    </div>
  );
}
