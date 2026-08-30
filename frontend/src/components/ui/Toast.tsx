// Simplified toast for the sake of completion. 
// A full toast system would use context/zustand, but we'll create a basic UI component here.
import React from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

export function Toast({ title, type = 'info', onClose }: { title: string, type?: 'success' | 'error' | 'info', onClose?: () => void }) {
  const icons = {
    success: <CheckCircle className="w-5 h-5 text-emerald-500" />,
    error: <AlertCircle className="w-5 h-5 text-red-500" />,
    info: <Info className="w-5 h-5 text-primary-500" />
  };
  return (
    <div className="fixed bottom-4 right-4 flex items-center gap-3 bg-white border border-slate-200 shadow-lg rounded-lg p-4 max-w-sm animate-in slide-in-from-bottom-5">
      {icons[type]}
      <p className="text-sm font-medium text-slate-800 flex-1">{title}</p>
      {onClose && (
        <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
