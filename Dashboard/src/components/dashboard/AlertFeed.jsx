import React from 'react';
import { cn } from '@/lib/utils';
import { AlertTriangle, Info, AlertCircle, ShieldAlert } from 'lucide-react';
import { format } from 'date-fns';

const severityConfig = {
  info: { icon: Info, color: 'text-primary', bg: 'bg-primary/10', border: 'border-primary/20' },
  warning: { icon: AlertTriangle, color: 'text-chart-3', bg: 'bg-chart-3/10', border: 'border-chart-3/20' },
  critical: { icon: AlertCircle, color: 'text-destructive', bg: 'bg-destructive/10', border: 'border-destructive/20' },
  emergency: { icon: ShieldAlert, color: 'text-destructive', bg: 'bg-destructive/20', border: 'border-destructive/30' },
};

export default function AlertsFeed({ alerts = [] }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">Active Alerts</h3>
        <span className="text-xs text-muted-foreground">{alerts.length} active</span>
      </div>
      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {alerts.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-8">No active alerts</p>
        )}
        {alerts.map((alert) => {
          const config = severityConfig[alert.severity] || severityConfig.info;
          const SevIcon = config.icon;
          return (
            <div
              key={alert.id}
              className={cn("p-3 rounded-lg border flex items-start gap-3", config.bg, config.border)}
            >
              <SevIcon className={cn("w-4 h-4 mt-0.5 shrink-0", config.color)} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-foreground truncate">{alert.title}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{alert.machine_name || 'System'}</p>
                <p className="text-[11px] text-muted-foreground mt-1">
                  {alert.created_date ? format(new Date(alert.created_date), 'MMM d, HH:mm') : ''}
                </p>
              </div>
              <span className={cn("text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded", config.color, config.bg)}>
                {alert.severity}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}