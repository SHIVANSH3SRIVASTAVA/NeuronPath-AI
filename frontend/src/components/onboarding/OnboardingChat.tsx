import React, { useState, useRef, useEffect } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Send, Brain } from 'lucide-react';

interface OnboardingChatProps {
  onComplete: (data: { name: string; goalText: string }) => void;
}

export function OnboardingChat({ onComplete }: OnboardingChatProps) {
  const [step, setStep] = useState<'name' | 'goal'>('name');
  const [name, setName] = useState('');
  const nameRef = useRef('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "👋 Welcome to NeuronPath! I'm your AI learning coach. Let's set up your personalized path.\n\nFirst, what's your name?" }
  ]);
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;
    const text = input.trim();
    
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInput('');

    if (step === 'name') {
      setName(text);
      nameRef.current = text;
      setStep('goal');
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Great to meet you, ${text}! 🎯\n\nNow tell me about your learning goal. Be as specific as you like!\n\nFor example:\n• "I want to become a Machine Learning Engineer in 6 months"\n• "I'm a beginner in Python and want to master data science"\n• "I know SQL and Python basics, aiming for a senior data analyst role"`
        }]);
      }, 300);
    } else if (step === 'goal') {
      const learnerName = nameRef.current || name || 'Learner';
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Perfect! Analyzing your goal and generating your personalized learning path... 🧠` 
        }]);
      }, 200);
      setTimeout(() => {
        onComplete({ name: learnerName, goalText: text });
      }, 600);
    }
  };

  return (
    <div className="flex flex-col h-[500px] overflow-hidden bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 transition-colors">
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center gap-3 bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-slate-900 dark:to-slate-800">
        <div className="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-950 text-primary-600 dark:text-primary-400 flex items-center justify-center border border-primary-200 dark:border-primary-800">
          <Brain className="w-6 h-6" />
        </div>
        <div>
          <h2 className="font-bold text-slate-900 dark:text-white">NeuronPath Onboarding</h2>
          <p className="text-xs text-slate-600 dark:text-slate-300">Tell us about yourself and your goals</p>
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 dark:bg-slate-950/60">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 whitespace-pre-line text-sm ${
              m.role === 'user' 
                ? 'bg-primary-600 text-white rounded-br-sm font-medium' 
                : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 rounded-bl-sm shadow-xs'
            }`}>
              {m.content}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex gap-2 bg-white dark:bg-slate-900">
        <Input 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          placeholder={step === 'name' ? 'Enter your name...' : 'Describe your learning goal...'} 
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          className="text-sm"
        />
        <Button onClick={handleSend} disabled={!input.trim()}>
          <Send className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
