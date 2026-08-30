import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { registerLearner } from '../api/auth';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card, CardContent } from '../components/ui/Card';
import { Brain, Lock, Mail, User, ArrowRight, Sun, Moon, AlertCircle } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const { setAuth, theme, toggleTheme } = useAppStore();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isDark = theme === 'dark';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !password.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match. Please verify.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await registerLearner({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password
      });
      setAuth(res.access_token, res.learner);
      navigate('/onboarding', { replace: true });
    } catch (err: any) {
      console.error('Registration error:', err);
      const detail = err.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Registration failed. Please check your details and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col justify-between transition-colors">
      <header className="px-6 py-4 flex justify-between items-center bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <Link to="/" className="flex items-center gap-2.5 text-2xl font-black text-primary-600 dark:text-primary-400 tracking-tight">
          <Brain className="w-8 h-8" /> NeuronPath
        </Link>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-full text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-100 transition-colors"
          aria-label={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDark ? (
            <Sun className="w-5 h-5 text-amber-400 hover:rotate-45 transition-transform" />
          ) : (
            <Moon className="w-5 h-5 text-slate-600 hover:-rotate-12 transition-transform" />
          )}
        </button>
      </header>

      <main className="flex-1 flex items-center justify-center p-4 sm:p-6">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2">
            <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
              Create your account
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Start your personalized AI-driven learning experience
            </p>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 rounded-xl p-3.5 flex items-start gap-2.5 text-xs text-red-700 dark:text-red-300 shadow-2xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <Card className="border-slate-200 dark:border-slate-800 shadow-sm">
            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <Input
                      type="text"
                      required
                      placeholder="Jane Doe"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-9 text-sm"
                      autoComplete="name"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <Input
                      type="email"
                      required
                      placeholder="name@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-9 text-sm"
                      autoComplete="email"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                    Password (min. 6 characters)
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <Input
                      type="password"
                      required
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-9 text-sm"
                      autoComplete="new-password"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-300 block">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                    <Input
                      type="password"
                      required
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="pl-9 text-sm"
                      autoComplete="new-password"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full font-bold shadow-sm mt-2 cursor-pointer"
                >
                  {loading ? 'Creating account...' : 'Create Account & Continue'}
                </Button>
              </form>
            </CardContent>
          </Card>

          <p className="text-center text-xs text-slate-600 dark:text-slate-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-bold text-primary-600 dark:text-primary-400 hover:underline inline-flex items-center gap-0.5"
            >
              Sign in <ArrowRight className="w-3 h-3" />
            </Link>
          </p>
        </div>
      </main>

      <footer className="py-4 text-center text-xs text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800">
        NeuronPath AI &copy; 2026. Secure Email + Password Authentication.
      </footer>
    </div>
  );
}
