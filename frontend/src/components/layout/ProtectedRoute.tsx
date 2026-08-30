import React from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { currentLearner, token } = useAppStore();
  const location = useLocation();

  if (!currentLearner && !token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children ? <>{children}</> : <Outlet />;
}

export default ProtectedRoute;
