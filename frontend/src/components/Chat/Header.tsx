import React from 'react';
import { Bot, Shield, Globe, RefreshCw, BarChart2 } from 'lucide-react';
import { MessageMeta } from '../../types';

interface HeaderProps {
  isConnected: boolean;
  isEscalated: boolean;
  currentMeta: MessageMeta;
  onReset: () => void;
  onOpenAdmin: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  isConnected,
  isEscalated,
  currentMeta,
  onReset,
  onOpenAdmin,
}) => {
  return (
    <header className="bg-slate-800/90 backdrop-blur border-b border-slate-700/60 px-6 py-4 flex items-center justify-between sticky top-0 z-20 shadow-md">
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center text-white shadow-lg shadow-brand-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <span
            className={`absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 rounded-full border-2 border-slate-800 ${
              isConnected ? 'bg-emerald-500' : 'bg-rose-500'
            }`}
            title={isConnected ? 'Connected' : 'Disconnected'}
          />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-semibold text-slate-100 text-base">NovaTech AI Care</h1>
            <span className="text-[11px] bg-slate-700/80 text-slate-300 font-medium px-2 py-0.5 rounded-full border border-slate-600/50">
              Gemini 2.5 Flash
            </span>
            {isEscalated && (
              <span className="text-[11px] bg-amber-500/20 text-amber-300 font-semibold px-2 py-0.5 rounded-full border border-amber-500/30 flex items-center gap-1 animate-pulse">
                <Shield className="w-3 h-3" /> Escalated to Human
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400">Real-time token streaming with RAG & tool calling</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {currentMeta.language && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs bg-slate-700/60 text-slate-300 px-2.5 py-1.5 rounded-lg border border-slate-600/50">
            <Globe className="w-3.5 h-3.5 text-indigo-400" />
            <span>Lang: <strong className="uppercase">{currentMeta.language}</strong></span>
          </div>
        )}

        <button
          onClick={onReset}
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-700/60 rounded-lg transition-colors border border-transparent hover:border-slate-600/50"
          title="New Conversation"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        <button
          onClick={onOpenAdmin}
          className="flex items-center gap-2 px-3 py-1.5 bg-slate-700/80 hover:bg-slate-700 text-slate-200 hover:text-white rounded-lg text-xs font-medium transition-all border border-slate-600 shadow-sm"
        >
          <BarChart2 className="w-4 h-4 text-brand-400" />
          <span>Admin Portal</span>
        </button>
      </div>
    </header>
  );
};
