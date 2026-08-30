import React, { useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Card, CardContent, CardHeader } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { ProgressData, ProgressionPoint } from '../../types';
import {
  TrendingUp,
  Award,
  Zap,
  Target,
  CheckCircle2,
  Clock,
  Sparkles,
  HelpCircle,
  BarChart2,
} from 'lucide-react';

interface MasteryGrowthChartProps {
  progressData: ProgressData;
}

export function MasteryGrowthChart({ progressData }: MasteryGrowthChartProps) {
  const [activeMetric, setActiveMetric] = useState<'combined' | 'progress' | 'mastery'>('combined');
  const [hoveredPoint, setHoveredPoint] = useState<ProgressionPoint | null>(null);

  // Extract or fallback to progression timeline points
  const rawTimeline = progressData.progression_timeline || [];

  // If no timeline exists yet, generate starting baseline and target checkpoints
  const timelineData: ProgressionPoint[] = rawTimeline.length > 0
    ? rawTimeline
    : [
        {
          id: 'start',
          label: 'Start',
          title: 'Onboarding Baseline',
          order_index: -1,
          status: 'completed',
          progress: 0,
          target_progress: 0,
          mastery: progressData.baseline_mastery || 0,
          assessment_score: null,
          completed_items: 0,
          total_items: 0,
          estimated_hours: 0,
          date: 'Start',
          is_current: false,
        },
        {
          id: 'm1',
          label: 'M1',
          title: progressData.current_milestone_title || 'Foundational Milestone',
          order_index: 0,
          status: 'available',
          progress: progressData.overall_progress || 0,
          target_progress: 100,
          mastery: progressData.current_mastery || 0,
          assessment_score: progressData.average_score > 0 ? progressData.average_score : null,
          completed_items: 0,
          total_items: 1,
          estimated_hours: 8,
          date: 'Step 1',
          is_current: true,
        },
      ];

  const currentMastery = progressData.current_mastery ?? Math.round(progressData.overall_progress * 0.8);
  const baselineMastery = progressData.baseline_mastery ?? 0;
  const masteryGrowth = progressData.mastery_growth ?? Math.max(0, currentMastery - baselineMastery);
  const velocityStatus = progressData.velocity_status || (progressData.overall_progress > 0 ? 'Steady Growth' : 'Getting Started');
  const velocityBadge = progressData.velocity_badge || 'Active Pace';
  const activeMilestone = progressData.current_milestone_title || 'Active Curriculum';

  // Custom Chart Tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data: ProgressionPoint = payload[0].payload;
      const statusVariants: Record<string, 'success' | 'primary' | 'warning' | 'default'> = {
        completed: 'success',
        in_progress: 'primary',
        available: 'warning',
        locked: 'default',
      };
      const statusLabels: Record<string, string> = {
        completed: 'Completed',
        in_progress: 'In Progress',
        available: 'Available Now',
        locked: 'Upcoming (Locked)',
      };

      return (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl p-4 min-w-[240px] space-y-2.5 z-50 text-xs">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
            <div className="flex items-center gap-1.5 font-bold text-slate-900 dark:text-white">
              <span className="px-1.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-mono text-[11px]">
                {data.label}
              </span>
              <span className="truncate max-w-[150px]">{data.title}</span>
            </div>
            <Badge variant={statusVariants[data.status] || 'default'} className="capitalize text-[10px]">
              {statusLabels[data.status] || data.status}
            </Badge>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />
                Curriculum Progress:
              </span>
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                {Math.round(data.progress)}%
              </span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-500 inline-block" />
                Skill Mastery:
              </span>
              <span className="font-bold text-cyan-600 dark:text-cyan-400">
                {Math.round(data.mastery)}%
              </span>
            </div>

            <div className="flex items-center justify-between text-slate-400 dark:text-slate-500">
              <span>Target Benchmark:</span>
              <span className="font-medium font-mono">{Math.round(data.target_progress)}%</span>
            </div>

            {data.assessment_score !== null && (
              <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800/60 text-amber-600 dark:text-amber-400 font-semibold">
                <span className="flex items-center gap-1">
                  <Award className="w-3.5 h-3.5" /> Assessment Score:
                </span>
                <span>{Math.round(data.assessment_score)}%</span>
              </div>
            )}

            {data.total_items > 0 && (
              <div className="flex items-center justify-between text-[11px] text-slate-400 dark:text-slate-500 pt-0.5">
                <span>Tasks Completed:</span>
                <span>{data.completed_items} of {data.total_items} items</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="col-span-1 md:col-span-2 overflow-hidden border-slate-200 dark:border-slate-800 shadow-sm">
      <CardHeader className="p-6 pb-4 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <div className="p-1.5 rounded-lg bg-primary-100 dark:bg-primary-950 text-primary-600 dark:text-primary-400">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h2 className="text-base font-bold text-slate-900 dark:text-slate-100">
                Learning Velocity & Mastery Growth
              </h2>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Real-time progression curve tracking curriculum completion, verified skill mastery, and milestone velocity.
            </p>
          </div>

          {/* Metric View Selector */}
          <div className="flex items-center bg-slate-200/70 dark:bg-slate-800 p-1 rounded-lg self-start sm:self-auto text-xs font-semibold">
            <button
              onClick={() => setActiveMetric('combined')}
              className={`px-3 py-1 rounded-md transition-all ${
                activeMetric === 'combined'
                  ? 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              All Curves
            </button>
            <button
              onClick={() => setActiveMetric('progress')}
              className={`px-3 py-1 rounded-md transition-all ${
                activeMetric === 'progress'
                  ? 'bg-white dark:bg-slate-900 text-emerald-600 dark:text-emerald-400 shadow-xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Curriculum %
            </button>
            <button
              onClick={() => setActiveMetric('mastery')}
              className={`px-3 py-1 rounded-md transition-all ${
                activeMetric === 'mastery'
                  ? 'bg-white dark:bg-slate-900 text-cyan-600 dark:text-cyan-400 shadow-xs font-bold'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              Skill Mastery
            </button>
          </div>
        </div>

        {/* Real KPI Summary Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 mt-2 border-t border-slate-100 dark:border-slate-800/60 text-xs">
          <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
            <span className="text-slate-500 dark:text-slate-400 block text-[11px] font-medium">Curriculum Progress</span>
            <div className="flex items-baseline gap-1.5 mt-0.5">
              <span className="text-lg font-black text-emerald-600 dark:text-emerald-400">
                {Math.round(progressData.overall_progress)}%
              </span>
              <span className="text-[10px] text-slate-400">
                ({progressData.milestones_completed}/{progressData.milestones_total} done)
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
            <span className="text-slate-500 dark:text-slate-400 block text-[11px] font-medium">Verified Mastery</span>
            <div className="flex items-baseline gap-1.5 mt-0.5">
              <span className="text-lg font-black text-cyan-600 dark:text-cyan-400">
                {Math.round(currentMastery)}%
              </span>
              {masteryGrowth > 0 ? (
                <span className="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 flex items-center">
                  +{Math.round(masteryGrowth)}%
                </span>
              ) : (
                <span className="text-[10px] text-slate-400">Baseline</span>
              )}
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
            <span className="text-slate-500 dark:text-slate-400 block text-[11px] font-medium">Learning Velocity</span>
            <div className="flex items-center gap-1.5 mt-1">
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              <span className="font-bold text-slate-800 dark:text-slate-200">
                {velocityStatus}
              </span>
            </div>
          </div>

          <div className="p-2.5 rounded-lg bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
            <span className="text-slate-500 dark:text-slate-400 block text-[11px] font-medium">Active Focus</span>
            <div className="flex items-center gap-1.5 mt-1 truncate">
              <Target className="w-3.5 h-3.5 text-primary-500 shrink-0" />
              <span className="font-bold text-slate-800 dark:text-slate-200 truncate" title={activeMilestone}>
                {activeMilestone}
              </span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 pt-4 space-y-4">
        {/* Main Progression Area Chart */}
        <div className="h-64 sm:h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={timelineData}
              margin={{ top: 10, right: 15, left: -15, bottom: 0 }}
              onMouseMove={(e) => {
                if (e && e.activePayload && e.activePayload[0]) {
                  setHoveredPoint(e.activePayload[0].payload);
                }
              }}
              onMouseLeave={() => setHoveredPoint(null)}
            >
              <defs>
                {/* Emerald Gradient for Curriculum Progress */}
                <linearGradient id="curriculumGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>

                {/* Cyan Gradient for Skill Mastery */}
                <linearGradient id="masteryGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke="#334155"
                opacity={0.2}
              />

              <XAxis
                dataKey="label"
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickLine={false}
                axisLine={{ stroke: '#334155', opacity: 0.3 }}
              />

              <YAxis
                domain={[0, 100]}
                ticks={[0, 25, 50, 75, 100]}
                tick={{ fontSize: 11, fill: '#64748b' }}
                tickFormatter={(v) => `${v}%`}
                tickLine={false}
                axisLine={false}
              />

              <Tooltip content={<CustomTooltip />} />

              {/* Target Benchmark Trajectory Line (Dashed) */}
              <Line
                type="monotone"
                dataKey="target_progress"
                name="Target Benchmark"
                stroke="#64748b"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                opacity={0.6}
              />

              {/* Verified Skill Mastery Curve */}
              {(activeMetric === 'combined' || activeMetric === 'mastery') && (
                <Area
                  type="monotone"
                  dataKey="mastery"
                  name="Skill Mastery"
                  stroke="#06b6d4"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#masteryGradient)"
                  dot={{ r: 3.5, fill: '#06b6d4', strokeWidth: 1.5, stroke: '#ffffff' }}
                  activeDot={{ r: 6, fill: '#06b6d4', stroke: '#ffffff', strokeWidth: 2 }}
                />
              )}

              {/* Actual Curriculum Progress Area */}
              {(activeMetric === 'combined' || activeMetric === 'progress') && (
                <Area
                  type="monotone"
                  dataKey="progress"
                  name="Curriculum Progress"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#curriculumGradient)"
                  dot={{ r: 4, fill: '#10b981', strokeWidth: 1.5, stroke: '#ffffff' }}
                  activeDot={{ r: 6.5, fill: '#10b981', stroke: '#ffffff', strokeWidth: 2 }}
                />
              )}
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Legend and Explanation Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100 dark:border-slate-800/80 text-xs">
          <div className="flex flex-wrap items-center gap-4 text-slate-600 dark:text-slate-400">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-1.5 rounded-full bg-emerald-500 inline-block" />
              <span className="font-semibold text-slate-800 dark:text-slate-200">Curriculum Completed (%)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-1.5 rounded-full bg-cyan-500 inline-block" />
              <span className="font-semibold text-slate-800 dark:text-slate-200">Demonstrated Mastery (%)</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <span className="w-3 h-0.5 border-t border-dashed border-slate-400 inline-block" />
              <span>Target Benchmark Path</span>
            </div>
          </div>

          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800/40 px-2.5 py-1 rounded-md border border-slate-100 dark:border-slate-800/60">
            <Sparkles className="w-3 h-3 text-amber-500 shrink-0" />
            <span>
              {progressData.milestones_completed === 0
                ? 'Complete learning items in your active milestone to elevate your progression curve.'
                : `Completed ${progressData.milestones_completed} of ${progressData.milestones_total} milestones across your personalized roadmap.`}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
