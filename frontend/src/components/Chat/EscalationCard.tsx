import React from 'react';
import { AlertCircle, Ticket, UserCheck, ShieldAlert } from 'lucide-react';
import { EscalationInfo } from '../../types';

interface EscalationCardProps {
  escalation: EscalationInfo;
}

export const EscalationCard: React.FC<EscalationCardProps> = ({ escalation }) => {
  return (
    <div className="mx-6 my-4 p-4 rounded-xl bg-gradient-to-r from-amber-950/40 via-amber-900/30 to-amber-950/40 border border-amber-600/40 shadow-lg shadow-amber-950/30 backdrop-blur animate-fadeIn">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-amber-200 flex items-center gap-2">
              <span>Customer Care Support Ticket Opened</span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-amber-500/30 text-amber-300 font-bold border border-amber-500/40">
                {escalation.priority} PRIORITY
              </span>
            </h3>
            <span className="text-xs font-mono font-medium text-amber-300/90 bg-amber-950/80 px-2 py-1 rounded border border-amber-700/50 flex items-center gap-1.5">
              <Ticket className="w-3.5 h-3.5 text-amber-400" />
              {escalation.ticket_id}
            </span>
          </div>

          <p className="text-xs text-amber-200/80 mt-1.5 leading-relaxed">
            {escalation.reason}
          </p>

          <div className="mt-3 flex items-center gap-2 text-xs text-emerald-400 font-medium">
            <UserCheck className="w-4 h-4" />
            <span>A tier-2 customer support agent has been notified and assigned to your case.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
