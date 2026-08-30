import React from 'react';
import { AssessmentQuestion } from '../../types';
import { Card, CardContent } from '../ui/Card';
import { HelpCircle, CheckCircle2 } from 'lucide-react';

interface QuestionCardProps {
  question: AssessmentQuestion;
  selectedOptionIndex?: number;
  onSelect: (optionIndex: number) => void;
}

export function QuestionCard({ 
  question, 
  selectedOptionIndex, 
  onSelect 
}: QuestionCardProps) {
  const options = question.options || [];

  return (
    <Card className="mb-6 shadow-2xs">
      <CardContent className="p-6 md:p-8">
        <div className="flex items-start gap-3.5 mb-6">
          <div className="p-2 rounded-lg bg-primary-50 dark:bg-primary-950/70 text-primary-600 dark:text-primary-400 shrink-0 mt-0.5 border border-primary-100 dark:border-primary-900">
            <HelpCircle className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[11px] font-bold uppercase tracking-wider text-primary-700 dark:text-primary-300 bg-primary-50 dark:bg-primary-950/80 px-2.5 py-0.5 rounded-md border border-primary-100 dark:border-primary-900">
              {question.difficulty || 'Intermediate'}
            </span>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mt-2 leading-snug">
              {question.question_text}
            </h3>
          </div>
        </div>

        <div className="space-y-3">
          {options.map((opt, i) => {
            const isSelected = selectedOptionIndex === i;
            const letter = String.fromCharCode(65 + i);

            return (
              <button
                key={i}
                type="button"
                onClick={() => onSelect(i)}
                className={`w-full text-left p-4 rounded-xl border-2 transition-all flex items-center justify-between gap-3 ${
                  isSelected 
                    ? 'border-primary-600 dark:border-primary-500 bg-primary-50/70 dark:bg-primary-950/60 text-primary-950 dark:text-primary-100 font-semibold ring-2 ring-primary-200 dark:ring-primary-900' 
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/60 text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900'
                }`}
              >
                <div className="flex items-center gap-3.5 flex-1 min-w-0">
                  <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 transition-colors ${
                    isSelected ? 'bg-primary-600 dark:bg-primary-500 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                  }`}>
                    {letter}
                  </span>
                  <span className="text-sm leading-relaxed">{opt}</span>
                </div>

                {isSelected && (
                  <CheckCircle2 className="w-5 h-5 text-primary-600 dark:text-primary-400 shrink-0 ml-2" />
                )}
              </button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
