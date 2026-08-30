import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAppStore, applyThemeToDom } from './store/useAppStore';
// Pages
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
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
import ProtectedRoute from './components/layout/ProtectedRoute';

function App() {
  const theme = useAppStore(state => state.theme);

  useEffect(() => {
    applyThemeToDom(theme);
  }, [theme]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
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
        </Route>
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
