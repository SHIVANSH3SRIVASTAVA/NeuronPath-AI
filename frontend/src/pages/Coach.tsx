import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '../store/useAppStore';
import { getCoachHistory, sendCoachMessage } from '../api/coach';
import { ChatMessageBubble } from '../components/coach/ChatMessage';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Send, Bot, Sparkles } from 'lucide-react';
import { ChatMessage } from '../types';

export default function Coach() {
  const { currentLearner } = useAppStore();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);

  const suggestions = [
    'What should I learn next for my goal?',
    'What are my biggest skill gaps right now?',
    'How is my overall progress?',
    'Quiz me on core concepts'
  ];

  useEffect(() => {
    if (!currentLearner) return;
    setInitialLoad(true);
    getCoachHistory(currentLearner.id)
      .then(history => {
        if (history && history.length > 0) {
          setMessages(history);
        } else {
          setMessages([{ 
            role: 'assistant', 
            content: `Hi ${currentLearner.name || 'there'}! I am your NeuronPath AI Learning Coach. I can help you understand complex concepts, analyze your skill gaps, guide your roadmap, and suggest the best next steps. What would you like to explore today?` 
          }]);
        }
      })
      .catch(console.error)
      .finally(() => setInitialLoad(false));
  }, [currentLearner]);

  useEffect(() => { 
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); 
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || input).trim();
    if (!text || !currentLearner) return;
    
    const userMsg: ChatMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const response = await sendCoachMessage(currentLearner.id, userMsg.content);
      const assistantMsg: ChatMessage = { role: 'assistant', content: response.content, intent: response.intent };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I had trouble connecting to the coach service. Please try again in a moment.' }]);
    } finally {
      setLoading(false);
    }
  };

  if (!currentLearner) return <div className="p-8 text-center text-slate-600 dark:text-slate-400">Please complete onboarding to chat with your AI coach.</div>;

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">
      <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-gradient-to-r from-primary-50 to-indigo-50 dark:from-slate-850 dark:to-slate-900">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-600 dark:bg-primary-500 text-white flex items-center justify-center shadow-xs">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              AI Learning Coach <Sparkles className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400">Tailored to {currentLearner.name}'s learning profile</p>
          </div>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50/50 dark:bg-slate-950/40">
        {initialLoad ? (
          <div className="text-center text-slate-400 dark:text-slate-500 mt-10 text-sm">Loading your conversation history...</div>
        ) : (
          messages.map((m, i) => <ChatMessageBubble key={i} message={m} />)
        )}
        {loading && (
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-xs italic ml-4 py-2">
            <div className="w-2 h-2 rounded-full bg-primary-400 animate-bounce" />
            <div className="w-2 h-2 rounded-full bg-primary-500 animate-bounce delay-100" />
            <div className="w-2 h-2 rounded-full bg-primary-600 animate-bounce delay-200" />
            <span>Coach is analyzing your learning path...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      
      <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 transition-colors">
        <div className="flex gap-2 mb-3 overflow-x-auto pb-1 scrollbar-none">
          {suggestions.map((s, i) => (
            <button 
              key={i} 
              onClick={() => handleSend(s)} 
              disabled={loading || initialLoad}
              className="shrink-0 text-xs px-3 py-1.5 bg-slate-100 dark:bg-slate-800 hover:bg-primary-50 dark:hover:bg-primary-950 hover:text-primary-700 dark:hover:text-primary-300 hover:border-primary-200 dark:hover:border-primary-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-full transition-all"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <Input 
            value={input} 
            onChange={e => setInput(e.target.value)} 
            placeholder="Ask your coach anything about your path or concepts..." 
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()} 
            disabled={loading || initialLoad}
            className="text-sm"
          />
          <Button onClick={() => handleSend()} disabled={loading || initialLoad || !input.trim()}>
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
