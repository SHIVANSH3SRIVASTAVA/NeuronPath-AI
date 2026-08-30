import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore, applyThemeToDom } from './store/useAppStore';
// Pages
import Landing from './pages/Landing';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import Roadmap from './pages/Roadmap';
import Skills from './pages/Skills';
import Resources from './pages/Resources';
import Assessment from './pages/Assessment';
import Progress from './pages/Progress';
import Coach from './pages/Coach';
import Profile from './pages/Profile';
import AppLayout from './components/layout/AppLayout';

function App() {
  const theme = useAppStore(state => state.theme);

  useEffect(() => {
    applyThemeToDom(theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/onboarding" element={<Onboarding />} />
        
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/roadmap" element={<Roadmap />} />
          <Route path="/skills" element={<Skills />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/assessment/:id" element={<Assessment />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/coach" element={<Coach />} />
          <Route path="/profile" element={<Profile />} />
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
