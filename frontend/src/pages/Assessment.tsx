import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { getAssessment, generateAssessment, submitAssessment } from '../api/assessment';
import { Assessment, AssessmentResult } from '../types';
import { QuestionCard } from '../components/assessment/QuestionCard';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { Sparkles, Trophy, CheckCircle2, XCircle, ArrowLeft, ArrowRight, Map, AlertCircle } from 'lucide-react';

export default function AssessmentPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { currentLearner, goalsVersion, activeGoal } = useAppStore();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<AssessmentResult | null>(null);
  const [activeQuestion, setActiveQuestion] = useState(0);

  useEffect(() => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    if (id) {
      getAssessment(parseInt(id, 10))
        .then(setAssessment)
        .catch(err => {
          console.error('Failed to load assessment by ID:', err);
          setError('Failed to load assessment. Click below to generate.');
        })
        .finally(() => setLoading(false));
    } else {
      generateAssessment(currentLearner.id)
        .then(setAssessment)
        .catch(err => {
          console.error('Failed to auto-generate assessment:', err);
          setError(err?.response?.data?.detail || 'Failed to load assessment. Click below to generate.');
        })
        .finally(() => setLoading(false));
    }
  }, [id, currentLearner, goalsVersion, activeGoal?.id]);

  const handleGenerate = async () => {
    if (!currentLearner) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setAnswers({});
    setActiveQuestion(0);
    try {
      const newAssessment = await generateAssessment(currentLearner.id);
      setAssessment(newAssessment);
    } catch (err: any) {
      console.error('Generate assessment error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to generate assessment.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId: number, optionIndex: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionIndex }));
  };

  const handleSubmit = async () => {
    if (!currentLearner || !assessment) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await submitAssessment(currentLearner.id, assessment.id, answers);
      setResults(res);
    } catch (err: any) {
      console.error('Submit assessment error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to submit assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!currentLearner) {
    return (
      <div className="max-w-2xl mx-auto py-16 text-center text-slate-600 dark:text-slate-400">
        Please complete onboarding to access assessments.
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4 pt-8 pb-16">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    );
  }

  // Results State
  if (results) {
    const rawScore = Number(results.score) || 0;
    const scoreVal = rawScore <= 1.0 && rawScore > 0 ? Math.round(rawScore * 100) : Math.round(rawScore);
    const isPassing = scoreVal >= 70;
    const totalQ = results.total_questions || assessment?.questions?.length || 0;
    const correctCount = results.correct_answers ?? 0;
    const adaptations = results.adaptation_actions || (results as any).adaptations || [];
    const skillScores = (results as any).skill_breakdown || results.skill_scores || {};

    return (
      <div className="max-w-3xl mx-auto space-y-6 pt-6 pb-16 animate-in fade-in duration-300">
        <div className="text-center pb-4 border-b border-slate-200 dark:border-slate-800">
          <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-3 ${isPassing ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400' : 'bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400'}`}>
            <Trophy className="w-8 h-8" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Assessment Results</h1>
          <p className="text-slate-600 dark:text-slate-300 mt-1">
            {isPassing ? 'Outstanding performance! Your mastery is confirmed.' : 'Good effort! Review the feedback below to strengthen key areas.'}
          </p>
        </div>

        {/* Score Overview Card */}
        <Card className="border-slate-200 dark:border-slate-800">
          <CardContent className="p-6 text-center">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Overall Score</span>
            <div className={`text-5xl font-black my-2 ${isPassing ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
              {scoreVal}%
            </div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              {correctCount} of {totalQ} questions correct
            </p>
          </CardContent>
        </Card>

        {/* Skill Scores Breakdown */}
        {skillScores && Object.keys(skillScores).length > 0 && (
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100 dark:border-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Skill Proficiency Impact</h2>
            </CardHeader>
            <CardContent className="pt-4 space-y-3">
              {Object.entries(skillScores).map(([sName, score]) => (
                <div key={sName} className="flex items-center justify-between p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800">
                  <span className="text-sm font-semibold text-slate-900 dark:text-white">{sName}</span>
                  <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                    Number(score) >= 70 
                      ? 'bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300' 
                      : Number(score) >= 50 
                      ? 'bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300' 
                      : 'bg-red-100 dark:bg-red-950 text-red-800 dark:text-red-300'
                  }`}>
                    {Math.round(Number(score))}%
                  </span>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {Array.isArray(adaptations) && adaptations.length > 0 && (
          <Card className="border-primary-200 dark:border-primary-800">
            <CardHeader className="pb-3 border-b border-primary-100 dark:border-primary-900 bg-primary-50/50 dark:bg-primary-950/40">
              <h2 className="text-base font-bold text-primary-900 dark:text-primary-200 flex items-center gap-2">
                <Map className="w-5 h-5 text-primary-600 dark:text-primary-400" /> Automatic Roadmap Adaptations
              </h2>
            </CardHeader>
            <CardContent className="pt-4">
              <ul className="space-y-2 text-slate-700 dark:text-slate-300 text-sm">
                {adaptations.map((adapt: string, idx: number) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-primary-600 dark:text-primary-400 mt-0.5 shrink-0" />
                    <span>{adapt}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Detailed Question Review */}
        {Array.isArray(results.explanations) && results.explanations.length > 0 && (
          <Card>
            <CardHeader className="pb-3 border-b border-slate-100 dark:border-slate-800">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">Question Review & Explanations</h2>
            </CardHeader>
            <CardContent className="pt-4 space-y-4">
              {results.explanations.map((exp: any, i: number) => (
                <div key={i} className={`p-4 rounded-xl border ${exp?.correct ? 'border-emerald-200 dark:border-emerald-900 bg-emerald-50/30 dark:bg-emerald-950/30' : 'border-red-200 dark:border-red-900 bg-red-50/30 dark:bg-red-950/30'}`}>
                  <div className="flex items-start gap-2.5 mb-1.5">
                    {exp?.correct ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">{i + 1}. {exp?.question_text}</p>
                      <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 font-medium">
                        Correct Answer: <span className="font-bold text-emerald-700 dark:text-emerald-300">{exp?.correct_answer}</span>
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 italic">{exp?.explanation}</p>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <div className="flex gap-4 pt-2">
          <Button onClick={() => navigate('/roadmap')} className="flex-1 font-bold">
            View Updated Roadmap
          </Button>
          <Button variant="outline" onClick={handleGenerate} className="flex-1 font-bold">
            Retake Assessment
          </Button>
        </div>
      </div>
    );
  }

  // Initial / Empty State if no assessment loaded
  if (!assessment || !assessment.questions || assessment.questions.length === 0) {
    return (
      <div className="max-w-2xl mx-auto py-12 px-4 text-center">
        <div className="w-16 h-16 bg-primary-50 dark:bg-primary-950/70 text-primary-600 dark:text-primary-400 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-primary-100 dark:border-primary-900">
          <Sparkles className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Adaptive Skill Assessment</h1>
        <p className="text-slate-600 dark:text-slate-300 mb-8 max-w-md mx-auto leading-relaxed">
          Test your mastery of the concepts in your active learning milestone. Your score dynamically adapts your personalized roadmap.
        </p>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 rounded-xl text-sm flex items-center gap-2 text-left">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <Button onClick={handleGenerate} size="lg" className="font-bold shadow-md cursor-pointer">
          <Sparkles className="w-4 h-4 mr-2" />
          Generate Milestone Assessment
        </Button>
      </div>
    );
  }

  const questions = assessment.questions;
  const currentQ = questions[activeQuestion];
  const handleNext = () => setActiveQuestion(p => Math.min(questions.length - 1, p + 1));
  const handlePrev = () => setActiveQuestion(p => Math.max(0, p - 1));

  return (
    <div className="max-w-3xl mx-auto space-y-6 pt-6 pb-16">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{assessment.title || 'Milestone Assessment'}</h1>
          <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">Question {activeQuestion + 1} of {questions.length}</p>
        </div>
        <div className="flex gap-1.5 flex-wrap">
          {questions.map((q, idx) => (
            <button
              key={q.id || idx}
              onClick={() => setActiveQuestion(idx)}
              className={`w-7 h-7 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                activeQuestion === idx
                  ? 'bg-primary-600 text-white shadow-xs'
                  : answers[q.id] !== undefined
                  ? 'bg-primary-100 dark:bg-primary-950 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-900 text-red-700 dark:text-red-300 rounded-lg text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {currentQ && (
        <QuestionCard
          question={currentQ}
          selectedOptionIndex={answers[currentQ.id]}
          onSelect={(optIdx) => handleSelectOption(currentQ.id, optIdx)}
        />
      )}

      <div className="flex items-center justify-between pt-2">
        <Button 
          variant="outline" 
          onClick={handlePrev} 
          disabled={activeQuestion === 0}
          className="font-semibold"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Previous
        </Button>

        {activeQuestion < questions.length - 1 ? (
          <Button onClick={handleNext} className="font-semibold">
            Next <ArrowRight className="w-4 h-4 ml-1.5" />
          </Button>
        ) : (
          <Button 
            onClick={handleSubmit} 
            disabled={submitting || Object.keys(answers).length < questions.length}
            className="font-bold shadow-md cursor-pointer"
          >
            {submitting ? 'Evaluating Submission...' : 'Submit Assessment'}
          </Button>
        )}
      </div>
    </div>
  );
}
