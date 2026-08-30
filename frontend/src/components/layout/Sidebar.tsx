import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, Brain, BookOpen, ClipboardCheck, TrendingUp, MessageSquare, User, X } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Map, label: 'My Roadmap', path: '/roadmap' },
  { icon: Brain, label: 'Skills', path: '/skills' },
  { icon: BookOpen, label: 'Resources', path: '/resources' },
  { icon: ClipboardCheck, label: 'Assessments', path: '/assessment' },
  { icon: TrendingUp, label: 'Progress', path: '/progress' },
  { type: 'separator' },
  { icon: MessageSquare, label: 'AI Coach', path: '/coach' },
  { type: 'separator' },
  { icon: User, label: 'Profile', path: '/profile' },
];

export default function Sidebar() {
  const { sidebarOpen, setSidebarOpen } = useAppStore();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-30 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transform transition-all duration-200 ease-in-out md:translate-x-0 md:static md:flex-shrink-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="h-full flex flex-col">
          <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
            <span className="text-xl font-black text-primary-600 dark:text-primary-400 flex items-center gap-2.5 tracking-tight">
              <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400" />
              NeuronPath
            </span>
            <button className="ml-auto md:hidden p-1.5 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" onClick={() => setSidebarOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
            {navItems.map((item, index) => {
              if (item.type === 'separator') {
                return <hr key={`sep-${index}`} className="my-3 border-slate-200 dark:border-slate-800" />;
              }
              const Icon = item.icon!;
              return (
                <NavLink
                  key={item.path}
                  to={item.path!}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold transition-colors ${
                      isActive 
                        ? 'bg-primary-50 dark:bg-primary-950/70 text-primary-700 dark:text-primary-300 shadow-2xs' 
                        : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </NavLink>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
