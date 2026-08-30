import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';
import { 
  getLearnerGoals, 
  createLearnerGoal, 
  activateLearnerGoal, 
  deleteLearnerGoal 
} from '../../api/learner';
import { LearnerGoal } from '../../types';
import { 
  Target, ChevronDown, Check, Plus, Trash2, 
  AlertTriangle, Loader2, Sparkles, X, Compass
} from 'lucide-react';
import { Button } from '../ui/Button';

const ROLE_PRESETS = [
  'Machine Learning Engineer',
  'Full Stack Developer',
  'Data Scientist',
  'DevOps Engineer',
  'Cloud Architect',
  'AI Engineer',
  'Frontend Developer',
  'Backend Developer'
];

export default function GoalSelector() {
  const navigate = useNavigate();
  const { currentLearner, goals, activeGoal, setGoals, setActiveGoal, triggerGoalUpdate } = useAppStore();

  const [isOpen, setIsOpen] = useState(false);
  const [loadingGoals, setLoadingGoals] = useState(false);
  const [switchingGoalId, setSwitchingGoalId] = useState<number | null>(null);

  // Add Goal Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newGoalRole, setNewGoalRole] = useState('');
  const [newGoalTimeline, setNewGoalTimeline] = useState(6);
  const [creating, setCreating] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  // Delete Goal Confirmation state
  const [goalToDelete, setGoalToDelete] = useState<LearnerGoal | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch all goals on mount or when learner changes
  const fetchGoals = async () => {
    if (!currentLearner) return;
    setLoadingGoals(true);
    try {
      const data = await getLearnerGoals(currentLearner.id);
      if (data && data.length > 0) {
        setGoals(data);
      } else if (activeGoal) {
        setGoals([{ ...activeGoal, status: 'active' }]);
      }
    } catch (err) {
      console.error('Failed to fetch goals:', err);
      if (activeGoal && (!goals || goals.length === 0)) {
        setGoals([{ ...activeGoal, status: 'active' }]);
      }
    } finally {
      setLoadingGoals(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, [currentLearner?.id, activeGoal?.id]);

  // Merge activeGoal into goals list if it's missing from the array
  const displayGoals = React.useMemo(() => {
    let list = Array.isArray(goals) ? [...goals] : [];
    if (activeGoal) {
      const idx = list.findIndex(g => g.id === activeGoal.id);
      if (idx === -1) {
        list = [{ ...activeGoal, status: 'active' }, ...list.map(g => ({ ...g, status: 'inactive' }))];
      } else {
        list = list.map(g => ({
          ...g,
          status: g.id === activeGoal.id ? 'active' : 'inactive'
        }));
      }
    }
    return list;
  }, [goals, activeGoal]);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSwitchGoal = async (goal: LearnerGoal) => {
    if (!currentLearner || goal.id === activeGoal?.id) {
      setIsOpen(false);
      return;
    }
    setSwitchingGoalId(goal.id);
    try {
      const activated = await activateLearnerGoal(currentLearner.id, goal.id);
      setActiveGoal(activated);
      triggerGoalUpdate();
      setIsOpen(false);
    } catch (err) {
      console.error('Failed to activate goal:', err);
      // Still switch active goal in store locally
      setActiveGoal(goal);
      triggerGoalUpdate();
      setIsOpen(false);
    } finally {
      setSwitchingGoalId(null);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentLearner || !newGoalRole.trim()) return;

    setCreating(true);
    setAddError(null);
    try {
      const created = await createLearnerGoal(currentLearner.id, {
        title: newGoalRole.trim(),
        target_role: newGoalRole.trim(),
        timeline_months: Number(newGoalTimeline) || 6,
        set_active: true
      });
      
      const updatedGoals = await getLearnerGoals(currentLearner.id);
      if (updatedGoals && updatedGoals.length > 0) {
        setGoals(updatedGoals);
      } else {
        setGoals([...goals.map(g => ({ ...g, status: 'inactive' })), created]);
      }
      setActiveGoal(created);
      triggerGoalUpdate();
      
      setShowAddModal(false);
      setNewGoalRole('');
      setIsOpen(false);
    } catch (err: any) {
      console.error('Create goal error:', err);
      setAddError(err?.response?.data?.detail || err.message || 'Failed to create new goal.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteGoal = async () => {
    if (!currentLearner || !goalToDelete) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      const res = await deleteLearnerGoal(currentLearner.id, goalToDelete.id);
      
      if (res.active_goal) {
        setActiveGoal(res.active_goal);
        setGoals(res.remaining_goals || []);
        triggerGoalUpdate();
      } else if (res.remaining_goals && res.remaining_goals.length > 0) {
        setActiveGoal(res.remaining_goals[0]);
        setGoals(res.remaining_goals);
        triggerGoalUpdate();
      } else {
        // No goals remain -> send user to onboarding
        setGoals([]);
        setActiveGoal(null);
        triggerGoalUpdate();
        navigate('/onboarding');
      }

      setGoalToDelete(null);
      setIsOpen(false);
    } catch (err: any) {
      console.error('Delete goal error:', err);
      setDeleteError(err?.response?.data?.detail || err.message || 'Failed to delete goal.');
    } finally {
      setDeleting(false);
    }
  };

  if (!currentLearner) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => {
          if (!isOpen) {
            fetchGoals();
          }
          setIsOpen(!isOpen);
        }}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-800 dark:text-slate-200 transition-all text-xs sm:text-sm font-medium shadow-2xs group max-w-[200px] sm:max-w-[280px] truncate"
        title="Switch or manage learning goals"
      >
        <div className="w-5 h-5 rounded-md bg-primary-100 dark:bg-primary-950/80 text-primary-600 dark:text-primary-400 flex items-center justify-center shrink-0">
          <Target className="w-3.5 h-3.5" />
        </div>
        <div className="flex flex-col items-start min-w-0 text-left">
          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 dark:text-slate-500 leading-none">
            Active Goal
          </span>
          <span className="font-semibold text-slate-900 dark:text-slate-100 truncate w-full text-xs sm:text-sm">
            {activeGoal ? activeGoal.target_role || activeGoal.title : 'Set Goal'}
          </span>
        </div>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 shrink-0 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute left-0 sm:right-0 sm:left-auto mt-2 w-72 sm:w-80 bg-white dark:bg-slate-900 rounded-xl shadow-xl border border-slate-200 dark:border-slate-800 z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
          <div className="p-3 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
            <div className="flex items-center gap-2">
              <Compass className="w-4 h-4 text-primary-600 dark:text-primary-400" />
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Your Goals ({displayGoals.length})
              </span>
            </div>
            <button
              onClick={() => {
                setShowAddModal(true);
                setIsOpen(false);
              }}
              className="text-xs font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 flex items-center gap-1 hover:underline"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Goal
            </button>
          </div>

          {/* Goal List */}
          <div className="max-h-64 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-800/60 p-1.5">
            {displayGoals.length === 0 ? (
              <div className="p-4 text-center text-xs text-slate-500 dark:text-slate-400">
                No goals created yet.
              </div>
            ) : (
              displayGoals.map((g) => {
                const isActive = activeGoal?.id === g.id;
                const isSwitching = switchingGoalId === g.id;

                return (
                  <div
                    key={g.id}
                    className={`flex items-center justify-between p-2 rounded-lg transition-colors group ${
                      isActive 
                        ? 'bg-primary-50/80 dark:bg-primary-950/40 text-primary-900 dark:text-primary-100' 
                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <button
                      onClick={() => handleSwitchGoal(g)}
                      disabled={isSwitching}
                      className="flex items-center gap-2.5 flex-1 min-w-0 text-left py-1 pr-2"
                    >
                      <div className={`w-4 h-4 rounded-full flex items-center justify-center shrink-0 ${
                        isActive 
                          ? 'bg-primary-600 text-white' 
                          : 'border border-slate-300 dark:border-slate-600 text-transparent'
                      }`}>
                        {isSwitching ? (
                          <Loader2 className="w-3 h-3 animate-spin text-primary-600" />
                        ) : (
                          <Check className="w-2.5 h-2.5 stroke-[3]" />
                        )}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className={`text-sm font-semibold truncate ${isActive ? 'text-primary-700 dark:text-primary-300' : 'text-slate-800 dark:text-slate-200'}`}>
                            {g.target_role || g.title}
                          </span>
                          {isActive && (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300">
                              Active
                            </span>
                          )}
                        </div>
                        <span className="text-[11px] text-slate-500 dark:text-slate-400">
                          {g.timeline_months} mo timeline
                        </span>
                      </div>
                    </button>

                    {/* Delete button per goal */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setGoalToDelete(g);
                      }}
                      className="p-1.5 text-slate-400 hover:text-red-600 dark:hover:text-red-400 rounded-md hover:bg-red-50 dark:hover:bg-red-950/40 opacity-70 group-hover:opacity-100 transition-all"
                      title="Delete this goal"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* Quick Add Button Footer */}
          <div className="p-2 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50">
            <button
              onClick={() => {
                setShowAddModal(true);
                setIsOpen(false);
              }}
              className="w-full py-2 px-3 rounded-lg border border-dashed border-primary-300 dark:border-primary-700 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-950/30 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Another Learning Goal
            </button>
          </div>
        </div>
      )}

      {/* Add New Goal Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-primary-100 dark:bg-primary-950/60 text-primary-600 dark:text-primary-400 flex items-center justify-center">
                  <Target className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Add New Career Goal</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Create an adaptive learning path for another target role.</p>
                </div>
              </div>
              <button 
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {addError && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs text-red-700 dark:text-red-300 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{addError}</span>
              </div>
            )}

            <form onSubmit={handleCreateGoal} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  Target Role / Career Goal
                </label>
                <input
                  type="text"
                  value={newGoalRole}
                  onChange={(e) => setNewGoalRole(e.target.value)}
                  placeholder="e.g. Full Stack Developer, Data Scientist..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 text-sm focus:outline-hidden focus:ring-2 focus:ring-primary-500"
                  required
                  autoFocus
                />
              </div>

              {/* Quick Presets */}
              <div>
                <span className="block text-[11px] font-semibold text-slate-500 dark:text-slate-400 mb-1.5">
                  Or choose a popular preset:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {ROLE_PRESETS.map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      onClick={() => setNewGoalRole(preset)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
                        newGoalRole === preset
                          ? 'bg-primary-600 text-white shadow-2xs'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                      }`}
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              {/* Timeline selector */}
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1.5 uppercase tracking-wider">
                  Target Timeline
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {[3, 6, 9, 12].map((months) => (
                    <button
                      key={months}
                      type="button"
                      onClick={() => setNewGoalTimeline(months)}
                      className={`py-2 rounded-xl text-xs font-bold transition-all border ${
                        newGoalTimeline === months
                          ? 'bg-primary-50 dark:bg-primary-950/60 border-primary-500 text-primary-600 dark:text-primary-400 ring-1 ring-primary-500'
                          : 'border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {months} Months
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-3 pt-3 border-t border-slate-100 dark:border-slate-800">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowAddModal(false)}
                  disabled={creating}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={creating || !newGoalRole.trim()}
                  className="flex-1 flex items-center justify-center gap-2"
                >
                  {creating ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating Roadmap...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Create & Switch
                    </>
                  )}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Goal Confirmation Modal */}
      {goalToDelete && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 flex items-center justify-center shrink-0">
                <Trash2 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">Delete Career Goal?</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">Permanent action for this specific goal.</p>
              </div>
            </div>

            {deleteError && (
              <div className="mb-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs text-red-700 dark:text-red-300 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{deleteError}</span>
              </div>
            )}

            <p className="text-sm text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">
              Are you sure you want to delete <strong className="text-slate-900 dark:text-slate-100 font-semibold">&ldquo;{goalToDelete.target_role || goalToDelete.title}&rdquo;</strong>? 
              This will remove its corresponding roadmap and progress milestones. 
              <span className="block mt-2 text-xs text-slate-500 dark:text-slate-400">
                Your account and other career goals will remain safe and unaffected.
              </span>
            </p>

            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={() => setGoalToDelete(null)}
                disabled={deleting}
                className="flex-1"
              >
                Keep Goal
              </Button>
              <Button
                variant="primary"
                onClick={handleDeleteGoal}
                disabled={deleting}
                className="flex-1 flex items-center justify-center gap-2 !bg-red-600 hover:!bg-red-700 !text-white border-0"
              >
                {deleting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  'Yes, Delete Goal'
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
