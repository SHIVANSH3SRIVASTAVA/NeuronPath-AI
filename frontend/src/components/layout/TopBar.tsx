import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';
import GoalSelector from '../goals/GoalSelector';
import { 
  Bell, User, LogOut, Menu, 
  Sparkles, Map, Brain, CheckCheck, 
  ChevronRight, BookOpen, Sun, Moon
} from 'lucide-react';

interface NotificationItem {
  id: string;
  title: string;
  message: string;
  time: string;
  read: boolean;
  type: 'assessment' | 'roadmap' | 'coach';
  link: string;
}

export default function TopBar() {
  const navigate = useNavigate();
  const { currentLearner, logout, toggleSidebar, theme, toggleTheme } = useAppStore();
  
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [unreadCount, setUnreadCount] = useState(2);
  
  const notifRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  const notifications: NotificationItem[] = [
    {
      id: '1',
      title: 'Milestone Assessment Ready',
      message: 'Take your adaptive milestone assessment to validate your skills.',
      time: 'Just now',
      read: false,
      type: 'assessment',
      link: '/assessment'
    },
    {
      id: '2',
      title: 'Roadmap Optimized',
      message: 'Your personalized learning path has been synchronized.',
      time: '1h ago',
      read: false,
      type: 'roadmap',
      link: '/roadmap'
    },
    {
      id: '3',
      title: 'AI Coach Check-in',
      message: 'Your AI Learning Coach is available with personalized guidance.',
      time: '1d ago',
      read: true,
      type: 'coach',
      link: '/coach'
    }
  ];

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setShowProfileMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getInitials = (name?: string) => {
    if (!name) return 'NP';
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  const handleLogout = () => {
    logout();
    setShowProfileMenu(false);
    navigate('/login');
  };

  const handleNotifClick = (link: string) => {
    setShowNotifications(false);
    navigate(link);
  };

  const markAllRead = () => {
    setUnreadCount(0);
  };

  const isDark = theme === 'dark';

  return (
    <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 md:px-6 relative z-40 transition-colors">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar}
          className="p-2 -ml-2 md:hidden rounded-lg text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-300"
          aria-label="Toggle Navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Multi-Goal Switcher & Manager */}
        <GoalSelector />
      </div>

      <div className="flex items-center gap-2 sm:gap-3">
        {/* Theme Toggle Button - Placed immediately LEFT of notification bell */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 cursor-pointer"
          aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          title={isDark ? 'Dark Mode active (Click for Light Mode)' : 'Light Mode active (Click for Dark Mode)'}
        >
          {isDark ? (
            <Sun className="w-5 h-5 text-amber-400 hover:rotate-45 transition-transform" />
          ) : (
            <Moon className="w-5 h-5 text-slate-700 hover:-rotate-12 transition-transform" />
          )}
        </button>

        {/* Notifications Dropdown */}
        <div className="relative" ref={notifRef}>
          <button 
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfileMenu(false);
            }}
            className="p-2 rounded-full text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white transition-colors relative focus:outline-none focus:ring-2 focus:ring-primary-500 cursor-pointer"
            aria-label="Notifications"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 bg-primary-600 rounded-full border-2 border-white dark:border-slate-900 animate-pulse" />
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2.5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-slate-900 dark:text-white text-sm">Notifications</span>
                  {unreadCount > 0 && (
                    <span className="px-2 py-0.5 bg-primary-100 dark:bg-primary-950 text-primary-700 dark:text-primary-300 text-xs font-semibold rounded-full border border-primary-200 dark:border-primary-800">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button 
                    onClick={markAllRead}
                    className="text-xs text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 font-semibold flex items-center gap-1 cursor-pointer"
                  >
                    <CheckCheck className="w-3.5 h-3.5" /> Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800">
                {notifications.map((item) => (
                  <div 
                    key={item.id} 
                    onClick={() => handleNotifClick(item.link)}
                    className={`p-3.5 hover:bg-slate-50 dark:hover:bg-slate-800/60 cursor-pointer transition-colors flex items-start gap-3 ${!item.read && unreadCount > 0 ? 'bg-primary-50/50 dark:bg-primary-950/40' : ''}`}
                  >
                    <div className="mt-0.5 p-2 rounded-lg bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300 shrink-0">
                      {item.type === 'assessment' ? <Sparkles className="w-4 h-4" /> : item.type === 'roadmap' ? <Map className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-xs font-bold text-slate-900 dark:text-white truncate">{item.title}</p>
                        <span className="text-[10px] text-slate-500 dark:text-slate-400">{item.time}</span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-0.5 line-clamp-2">{item.message}</p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="px-4 py-2 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80 text-center">
                <button 
                  onClick={() => { setShowNotifications(false); navigate('/dashboard'); }}
                  className="text-xs text-slate-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 font-semibold inline-flex items-center gap-1 cursor-pointer"
                >
                  View Learning Activity <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar & Menu */}
        <div className="relative" ref={profileRef}>
          <button 
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 p-1 rounded-full hover:ring-2 hover:ring-primary-400 dark:hover:ring-primary-500 transition-all focus:outline-none cursor-pointer"
            aria-label="User profile menu"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-600 to-indigo-500 text-white flex items-center justify-center font-bold text-xs shadow-xs">
              {getInitials(currentLearner?.name)}
            </div>
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-3 border-b border-slate-100 dark:border-slate-800">
                <p className="text-sm font-bold text-slate-900 dark:text-white truncate">{currentLearner?.name || 'Active Learner'}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{currentLearner?.email || 'Personalized Track'}</p>
                <div className="mt-1.5 flex items-center gap-2">
                  <span className="px-2 py-0.5 bg-primary-50 dark:bg-primary-950 text-primary-700 dark:text-primary-300 text-[10px] font-semibold rounded-full capitalize border border-primary-100 dark:border-primary-800">
                    {currentLearner?.experience_level || 'Beginner'} Level
                  </span>
                  <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
                    {currentLearner?.weekly_hours || 10}h / week
                  </span>
                </div>
              </div>

              <div className="py-1">
                <button
                  onClick={() => { setShowProfileMenu(false); navigate('/profile'); }}
                  className="w-full px-4 py-2 text-left text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2.5 transition-colors cursor-pointer"
                >
                  <User className="w-4 h-4 text-slate-500 dark:text-slate-400" /> Profile & Settings
                </button>
                <button
                  onClick={() => { setShowProfileMenu(false); navigate('/roadmap'); }}
                  className="w-full px-4 py-2 text-left text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2.5 transition-colors cursor-pointer"
                >
                  <Map className="w-4 h-4 text-slate-500 dark:text-slate-400" /> My Learning Roadmap
                </button>
                <button
                  onClick={() => { setShowProfileMenu(false); navigate('/resources'); }}
                  className="w-full px-4 py-2 text-left text-xs font-medium text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 flex items-center gap-2.5 transition-colors cursor-pointer"
                >
                  <BookOpen className="w-4 h-4 text-slate-500 dark:text-slate-400" /> Recommended Resources
                </button>
              </div>

              <div className="border-t border-slate-100 dark:border-slate-800 pt-1">
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-2 text-left text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 flex items-center gap-2.5 transition-colors cursor-pointer"
                >
                  <LogOut className="w-4 h-4 text-red-500 dark:text-red-400" /> Log Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
