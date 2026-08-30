import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useAppStore } from '../store/useAppStore';
import { updateLearner, deleteLearner } from '../api/learner';
import { User, Save, CheckCircle2, AlertCircle, Trash2, AlertTriangle, X } from 'lucide-react';

export default function Profile() {
  const navigate = useNavigate();
  const { currentLearner, setCurrentLearner, logout } = useAppStore();
  const [name, setName] = useState(currentLearner?.name || '');
  const [hours, setHours] = useState(currentLearner?.weekly_hours || 10);
  const [experienceLevel, setExperienceLevel] = useState(currentLearner?.experience_level || 'beginner');
  const [learningStyle, setLearningStyle] = useState(currentLearner?.preferred_formats?.[0] || 'visual');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Delete account modal states
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  
  const handleSave = async () => {
    if (!currentLearner) return;
    setSaving(true);
    setMessage({ text: '', type: '' });
    try {
      const updated = await updateLearner(currentLearner.id, { 
        name, 
        weekly_hours: hours,
        experience_level: experienceLevel,
        preferred_formats: [learningStyle]
      });
      setCurrentLearner(updated);
      setMessage({ text: 'Profile updated successfully!', type: 'success' });
    } catch (err) {
      setMessage({ text: 'Failed to update profile.', type: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!currentLearner) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteLearner(currentLearner.id);
      logout();
      navigate('/login', { 
        replace: true, 
        state: { successMessage: 'Your account and all associated learning data have been permanently deleted.' } 
      });
    } catch (err: any) {
      console.error('Delete account error:', err);
      const detail = err.response?.data?.detail;
      setDeleteError(typeof detail === 'string' ? detail : 'Failed to delete account. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (!currentLearner) return <div className="p-8 text-center text-slate-600 dark:text-slate-400">Please complete onboarding to view your settings.</div>;

  return (
    <div className="max-w-2xl mx-auto space-y-6 pt-6 pb-12">
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <h1 className="text-3xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2.5">
          <User className="w-7 h-7 text-primary-600 dark:text-primary-400" /> Learner Profile & Preferences
        </h1>
        <p className="text-slate-600 dark:text-slate-400 mt-1">
          Manage your schedule commitment, proficiency level, and study styles.
        </p>
      </div>
      
      {message.text && (
        <div className={`p-4 rounded-xl text-sm flex items-center gap-2 border ${message.type === 'success' ? 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800' : 'bg-red-50 dark:bg-red-950/50 text-red-700 dark:text-red-300 border-red-200 dark:border-red-800'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> : <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      <Card>
        <CardHeader className="border-b border-slate-100 dark:border-slate-800">
          <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">Personal Information</h2>
        </CardHeader>
        <CardContent className="space-y-4 p-6">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">Full Name</label>
            <Input value={name} onChange={e => setName(e.target.value)} disabled={saving} />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">Weekly Commitment (Hours)</label>
            <Input type="number" value={hours} onChange={e => setHours(Number(e.target.value))} disabled={saving} />
            <p className="text-xs text-amber-700 dark:text-amber-400 mt-1.5 font-medium">Changing your hours will dynamically calibrate your milestone estimated pacing.</p>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">Experience Level</label>
            <select 
              value={experienceLevel} 
              onChange={e => setExperienceLevel(e.target.value as 'beginner' | 'intermediate' | 'advanced')}
              disabled={saving}
              className="w-full p-2.5 text-sm border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-400 mb-1.5">Preferred Learning Style</label>
            <select 
              value={learningStyle} 
              onChange={e => setLearningStyle(e.target.value)}
              disabled={saving}
              className="w-full p-2.5 text-sm border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="video">Video & Guided Lectures</option>
              <option value="article">Documentation & In-depth Text</option>
              <option value="interactive">Interactive Hands-on Coding</option>
            </select>
          </div>
          <div className="pt-2">
            <Button onClick={handleSave} disabled={saving} className="font-semibold shadow-xs">
              <Save className="w-4 h-4 mr-1.5" />
              {saving ? 'Saving Changes...' : 'Save Changes'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Danger Zone */}
      <Card className="border-red-200 dark:border-red-950/70 bg-red-50/30 dark:bg-red-950/10">
        <CardHeader className="border-b border-red-100 dark:border-red-950/50">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <AlertTriangle className="w-5 h-5" />
            <h2 className="text-base font-bold">Danger Zone</h2>
          </div>
        </CardHeader>
        <CardContent className="p-6 space-y-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">Delete Account</h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
              Permanently delete your account and all associated learning records, goals, personalized roadmaps, skill assessments, milestone progress, and chat history. This action cannot be undone.
            </p>
          </div>
          <Button 
            variant="outline" 
            onClick={() => {
              setDeleteError(null);
              setShowDeleteModal(true);
            }} 
            className="border-red-300 dark:border-red-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/50 hover:border-red-400 font-semibold"
          >
            <Trash2 className="w-4 h-4 mr-1.5" />
            Delete Account
          </Button>
        </CardContent>
      </Card>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-xs animate-in fade-in duration-150">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <div className="flex items-start justify-between">
              <div className="w-10 h-10 rounded-full bg-red-100 dark:bg-red-950/60 flex items-center justify-center text-red-600 dark:text-red-400 shrink-0">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <button 
                onClick={() => !deleting && setShowDeleteModal(false)}
                disabled={deleting}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg transition-colors cursor-pointer"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2">
              <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                Delete Account Permanently?
              </h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                This action is <strong className="text-red-600 dark:text-red-400 font-semibold">irreversible</strong>. Your account, learning goals, customized roadmaps, skill assessments, milestone progress, and AI coach conversations will be immediately wiped.
              </p>
            </div>

            {deleteError && (
              <div className="p-3 rounded-lg text-xs bg-red-50 dark:bg-red-950/60 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{deleteError}</span>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button
                variant="outline"
                onClick={() => setShowDeleteModal(false)}
                disabled={deleting}
                className="flex-1 font-semibold"
              >
                Cancel
              </Button>
              <Button
                onClick={handleDeleteAccount}
                disabled={deleting}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold shadow-xs"
              >
                {deleting ? 'Deleting Account...' : 'Yes, Delete Account'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
