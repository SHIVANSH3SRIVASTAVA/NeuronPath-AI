import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../ui/Card';
import { Button } from '../ui/Button';
import { PlayCircle, ArrowRight, BookOpen, ClipboardCheck, Trophy, Target } from 'lucide-react';

interface NextActionProps {
  action: {
    action: string;
    description: string;
    type?: string;
    title?: string;
    id?: number;
    resource_id?: number;
    milestone_id?: number;
  };
}

const ACTION_CONFIG: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  start_resource: { label: '📚 Start Learning', icon: <BookOpen className="w-5 h-5" />, color: 'border-l-primary-500' },
  take_assessment: { label: '📝 Take Assessment', icon: <ClipboardCheck className="w-5 h-5" />, color: 'border-l-amber-500' },
  create_goal: { label: '🎯 Set Your Goal', icon: <Target className="w-5 h-5" />, color: 'border-l-secondary-500' },
  all_completed: { label: '🎉 Path Complete!', icon: <Trophy className="w-5 h-5" />, color: 'border-l-emerald-500' },
};

export function NextBestAction({ action }: NextActionProps) {
  const navigate = useNavigate();
  if (!action) return null;
  
  const config = ACTION_CONFIG[action.action] || ACTION_CONFIG['start_resource'];
  
  const handleClick = () => {
    if (action.action === 'take_assessment') {
      navigate('/assessment');
    } else if (action.action === 'start_resource') {
      navigate('/roadmap');
    } else if (action.action === 'create_goal') {
      navigate('/onboarding');
    } else {
      navigate('/roadmap');
    }
  };

  return (
    <Card className={`border-l-4 ${config.color}`}>
      <CardContent className="flex items-start sm:items-center justify-between flex-col sm:flex-row gap-4 p-5">
        <div className="flex items-start gap-3.5">
          <div className="mt-1 text-primary-600 dark:text-primary-400 p-2 rounded-lg bg-primary-50 dark:bg-primary-950/80 shrink-0">
            {config.icon}
          </div>
          <div>
            <p className="text-xs font-bold text-primary-700 dark:text-primary-300 mb-0.5 uppercase tracking-wider">Next Recommended Step</p>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{config.label}</h3>
            <p className="text-slate-700 dark:text-slate-300 text-sm leading-relaxed">{action.description}</p>
          </div>
        </div>
        {action.action !== 'all_completed' && (
          <Button onClick={handleClick} className="shrink-0 group font-bold shadow-xs">
            <PlayCircle className="w-4 h-4 mr-2" />
            Continue
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
