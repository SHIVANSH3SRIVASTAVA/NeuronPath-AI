import React, { useState, useEffect, useRef } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { 
  getLearnerGoals, 
  createLearnerGoal, 
  activateLearnerGoal, 
  deleteLearnerGoal 
} from '../../api/learner';
import { LearnerGoal } from '../../types';
import { 
  Target, ChevronDown, Plus, Trash2, Check, 
  Sparkles, AlertCircle, Loader2, Compass 
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Modal } from '../ui/Modal';

const ROLE_PRESETS = [
  { role: 'Machine Learning Engineer', title: 'Machine Learning & AI Engineering', months: 6 },
  { role: 'Full Stack Developer', title: 'Full Stack Web Development', months: 6 },
  { role: 'Data Scientist', title: 'Data Science & Statistical Analysis', months: 6 },
  { role: 'DevOps Engineer', title: 'DevOps & Cloud Infrastructure', months: 6 },
  { role: 'Frontend Developer', title: 'Modern Frontend Engineering', months: 4 },
  { role: 'Backend Developer', title: 'Scalable Backend Systems', months: 6 },
  { role: 'SQL Developer', title: 'SQL & Database Engineering', months: 4 },
  { role: 'AI Engineer', title: 'Applied Generative AI Engineering', months: 6 },
  { role: 'Cloud Architect', title: 'Cloud Architecture & Security', months: 8 },
];

export function GoalDropdown() {
  const { 
    currentLearner, 
    goals, 
    activeGoal, 
    setGoals, 
    setActiveGoal, 
    triggerGoalUpdate,
    goalsVersion 
  } = useAppStore();

  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);
  
  // Add Goal Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [targetRole, setTargetRole] = useState('');
  const [goalTitle, setGoalTitle] = useState('');
  const [timelineMonths, setTimelineMonths] = useState(6);
  const [addError, setAddError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  // Delete Goal Modal state
  const [goalToDelete, setGoalToDelete] = useState<LearnerGoal | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fetch goals on mount or when learner/version changes
  const fetchGoals = async () => {
    if (!currentLearner) return;
    try {
      const fetched = await getLearnerGoals(currentLearner.id);
      if (fetched && fetched.length > 0) {
        setGoals(fetched);
      }
    } catch (err) {
      console.error('Failed to fetch goals:', err);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, [currentLearner?.id, goalsVersion]);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectGoal = async (goal: LearnerGoal) => {
    if (goal.id === activeGoal?.id) {
      setIsOpen(false);
      return;
    }
    setActionLoadingId(goal.id);
    try {
      const activated = await activateLearnerGoal(goal.id);
      setActiveGoal(activated);
      triggerGoalUpdate();
      setIsOpen(false);
    } catch (err: any) {
      console.error('Failed to switch goal:', err);
    } finally {
      setActionLoadingId(null);
    }
  };

  const handlePresetSelect = (preset: typeof ROLE_PRESETS[0]) => {
    setTargetRole(preset.role);
    setGoalTitle(preset.title);
    setTimelineMonths(preset.months);
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole.trim()) {
      setAddError('Please enter a target role or select a preset.');
      return;
    }
    setCreating(true);
    setAddError(null);
    try {
      const created = await createLearnerGoal({
        title: (goalTitle.trim() || `${targetRole.trim()} Mastery`),
        target_role: targetRole.trim(),
        timeline_months: Number(timelineMonths) || 6,
        set_active: true
      });
      
      // Refresh goals from backend
      if (currentLearner) {
        const updatedList = await getLearnerGoals(currentLearner.id);
        setGoals(updatedList);
      }
      setActiveGoal(created);
      triggerGoalUpdate();

      setShowAddModal(false);
      setTargetRole('');
      setGoalTitle('');
      setIsOpen(false);
    } catch (err: any) {
      console.error('Failed to create goal:', err);
      setAddError(err?.response?.data?.detail || 'Failed to create new goal. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteGoal = async () => {
    if (!goalToDelete) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      const res = await deleteLearnerGoal(goalToDelete.id);
      if (res && res.goals) {
        setGoals(res.goals);
        if (res.active_goal) {
          setActiveGoal(res.active_goal);
        }
      } else if (currentLearner) {
        const updatedList = await getLearnerGoals(currentLearner.id);
        setGoals(updatedList);
      }
      triggerGoalUpdate();
      setGoalToDelete(null);
      setIsOpen(false);
    } catch (err: any) {
      console.error('Failed to delete goal:', err);
      setDeleteError(err?.response?.data?.detail || 'Failed to delete goal.');
    } finally {
      setDeleting(false);
    }
  };

  const currentActive = activeGoal || (goals.length > 0 ? goals[0] : null);
  const displayRole = currentActive?.target_role || currentActive?.title || 'Personalized Goal';

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-semibold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors border border-slate-200 dark:border-slate-700 focus:outline-none focus:ring-2 focus:ring-primary-500 cursor-pointer"
        aria-label="Goals Dropdown"
      >
        <Target className="w-4 h-4 text-primary-600 dark:text-primary-400" />
        <span className="hidden sm:inline text-xs text-slate-500 dark:text-slate-400 font-medium">Goal:</span>
        <span className="max-w-[140px] sm:max-w-[200px] truncate text-slate-900 dark:text-white font-bold">{displayRole}</span>
        <span className="text-[10px] px-1.5 py-0.5 rounded bg-primary-100 dark:bg-primary-950 text-primary-700 dark:text-primary-300 font-bold border border-primary-200 dark:border-primary-800 ml-0.5">
          {goals.length}/3
        </span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute left-0 mt-2 w-72 sm:w-84 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-800 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
          <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Learning Goals ({goals.length}/3)
            </span>
            {goals.length < 3 && (
              <button
                onClick={() => {
                  setShowAddModal(true);
                  setAddError(null);
                }}
                className="text-xs font-bold text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1 cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Add Goal
              </button>
            )}
          </div>

          <div className="py-1 max-h-64 overflow-y-auto">
            {goals.length === 0 ? (
              <div className="px-4 py-3 text-center text-xs text-slate-500 dark:text-slate-400">
                No active learning goals.
              </div>
            ) : (
              goals.map((g) => {
                const isActive = g.id === currentActive?.id;
                const isItemLoading = actionLoadingId === g.id;

                return (
                  <div
                    key={g.id}
                    className={`flex items-center justify-between px-3 py-2 mx-1 rounded-lg transition-colors group ${
                      isActive 
                        ? 'bg-primary-50 dark:bg-primary-950/50 text-primary-900 dark:text-primary-200 font-semibold' 
                        : 'hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <button
                      onClick={() => handleSelectGoal(g)}
                      disabled={isItemLoading}
                      className="flex-1 flex items-center gap-2.5 text-left min-w-0 pr-2 cursor-pointer focus:outline-none"
                    >
                      <div className={`w-2 h-2 rounded-full shrink-0 ${isActive ? 'bg-primary-600 dark:bg-primary-400 animate-pulse' : 'bg-slate-300 dark:bg-slate-600'}`} />
                      <div className="truncate flex-1">
                        <p className="text-xs font-bold truncate leading-tight">
                          {g.target_role || g.title}
                        </p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate leading-tight mt-0.5">
                          {g.timeline_months} mo timeline {isActive && '• Current Active'}
                        </p>
                      </div>
                      {isItemLoading && <Loader2 className="w-3.5 h-3.5 animate-spin text-primary-600 shrink-0" />}
                      {isActive && !isItemLoading && <Check className="w-3.5 h-3.5 text-primary-600 dark:text-primary-400 shrink-0" />}
                    </button>

                    {/* Delete button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setGoalToDelete(g);
                        setDeleteError(null);
                      }}
                      className="p-1.5 rounded-md text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors focus:outline-none cursor-pointer"
                      title={goals.length <= 1 ? "Cannot delete only goal" : `Delete ${g.target_role || g.title}`}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* Add Goal option inside dropdown */}
          <div className="border-t border-slate-100 dark:border-slate-800 px-3 pt-2 pb-1 mt-1">
            {goals.length < 3 ? (
              <button
                onClick={() => {
                  setShowAddModal(true);
                  setAddError(null);
                }}
                className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-bold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-950/40 hover:bg-primary-100 dark:hover:bg-primary-900/60 border border-primary-200 dark:border-primary-800/60 transition-colors cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Add Goal ({3 - goals.length} remaining)
              </button>
            ) : (
              <p className="text-[11px] text-center text-slate-400 dark:text-slate-500 py-1">
                Maximum limit of 3 goals reached
              </p>
            )}
          </div>
        </div>
      )}

      {/* ADD GOAL MODAL */}
      <Modal
        isOpen={showAddModal}
        onClose={() => !creating && setShowAddModal(false)}
        title="Add New Learning Goal"
      >
        <form onSubmit={handleCreateGoal} className="space-y-4">
          <p className="text-xs text-slate-600 dark:text-slate-400">
            You can have up to 3 independent goals. Each goal generates its own custom roadmap and progress track.
          </p>

          {addError && (
            <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{addError}</span>
            </div>
          )}

          {/* Quick presets */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
              Popular Career Presets:
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-40 overflow-y-auto p-1 border border-slate-200 dark:border-slate-800 rounded-lg">
              {ROLE_PRESETS.map((p) => {
                const isSelected = targetRole === p.role;
                return (
                  <button
                    key={p.role}
                    type="button"
                    onClick={() => handlePresetSelect(p)}
                    className={`text-left p-2 rounded-md text-xs transition-colors border ${
                      isSelected
                        ? 'bg-primary-50 dark:bg-primary-950 border-primary-500 text-primary-700 dark:text-primary-300 font-bold'
                        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700/50'
                    }`}
                  >
                    <div className="truncate font-semibold">{p.role}</div>
                    <div className="text-[10px] text-slate-400 dark:text-slate-500">{p.months} months</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Target Role Input */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
              Target Role / Job Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Machine Learning Engineer, SQL Developer"
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Goal Title / Focus */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
              Goal Focus / Track Title (Optional)
            </label>
            <input
              type="text"
              placeholder="e.g. Full Stack Web Development Mastery"
              value={goalTitle}
              onChange={(e) => setGoalTitle(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Timeline */}
          <div>
            <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
              Target Timeline (Months)
            </label>
            <select
              value={timelineMonths}
              onChange={(e) => setTimelineMonths(Number(e.target.value))}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value={3}>3 Months (Accelerated)</option>
              <option value={6}>6 Months (Standard)</option>
              <option value={9}>9 Months (In-depth)</option>
              <option value={12}>12 Months (Comprehensive)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setShowAddModal(false)}
              disabled={creating}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              disabled={creating || !targetRole.trim()}
              className="flex items-center gap-1.5"
            >
              {creating ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Creating Roadmap...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Create & Activate Goal
                </>
              )}
            </Button>
          </div>
        </form>
      </Modal>

      {/* DELETE GOAL CONFIRMATION MODAL */}
      <Modal
        isOpen={!!goalToDelete}
        onClose={() => !deleting && setGoalToDelete(null)}
        title="Delete Learning Goal"
      >
        <div className="space-y-4">
          {goals.length <= 1 ? (
            <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/60 rounded-lg text-xs text-amber-800 dark:text-amber-300 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">Cannot delete your only learning goal</p>
                <p className="mt-0.5">NeuronPath requires at least one active learning goal to generate your roadmap. Please add another goal before deleting this one.</p>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm text-slate-700 dark:text-slate-300">
                Are you sure you want to delete <strong className="text-slate-900 dark:text-white font-bold">{goalToDelete?.target_role || goalToDelete?.title}</strong>?
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                This will permanently delete this goal and its associated roadmap milestones and learning items. Your other goals will remain unaffected.
              </p>
            </>
          )}

          {deleteError && (
            <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-lg text-xs text-red-700 dark:text-red-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{deleteError}</span>
            </div>
          )}

          <div className="flex justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setGoalToDelete(null)}
              disabled={deleting}
            >
              {goals.length <= 1 ? 'Close' : 'Cancel'}
            </Button>
            {goals.length > 1 && (
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={handleDeleteGoal}
                disabled={deleting}
                className="flex items-center gap-1.5"
              >
                {deleting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" /> Delete Goal
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
