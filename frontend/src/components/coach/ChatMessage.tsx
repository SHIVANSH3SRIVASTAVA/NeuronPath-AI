import React from 'react';
import { ChatMessage } from '../../types';

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[80%] px-5 py-3.5 rounded-2xl transition-colors ${
        isUser 
          ? 'bg-primary-600 text-white rounded-br-none shadow-xs' 
          : 'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 rounded-bl-none shadow-2xs'
      }`}>
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
      </div>
    </div>
  );
}
