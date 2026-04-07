import React from 'react';
import { cn } from '@/lib/utils';
import { Cpu, Thermometer, Zap, Clock } from 'lucide-react';

const statusColors = {
  running: 'bg-accent/20 border-accent/40 text-accent',
  idle: 'bg-chart-3/20 border-chart-3/40 text-chart-3',
  maintenance: 'bg-chart-4/20 border-chart-4/40 text-chart-4',
  error: 'bg-destructive/20 border-destructive/40 text-destructive',
  offline: 'bg-muted border-border text-muted-foreground',
};

const statusDot = {
  running: 'bg-accent',
  idle: 'bg-chart-3',
  maintenance: 'bg-chart-4',
  error: 'bg-destructive',
  offline: 'bg-muted-foreground',
};

export default function MachineStatusGrid({ machines = [] }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">Machine Status</h3>
        <span className="text-xs text-muted-foreground">{machines.length} machines</span>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {machines.map((machine) => (
          <div
            key={machine.id}
            className={cn(
              "p-3 rounded-lg border transition-all duration-200 hover:scale-[1.02]",
              statusColors[machine.status] || statusColors.offline
            )}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className={cn("w-2 h-2 rounded-full animate-pulse-glow", statusDot[machine.status])} />
              <span className="text-xs font-semibold truncate">{machine.name}</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px]">
                <span className="flex items-center gap-1 opacity-70">
                  <Thermometer className="w-3 h-3" />{machine.temperature || '--'}°C
                </span>
                <span className="flex items-center gap-1 opacity-70">
                  <Zap className="w-3 h-3" />{machine.power_consumption || '--'}kW
                </span>
              </div>
              <div className="flex items-center justify-between text-[11px]">
                <span className="opacity-70">OEE</span>
                <span className="font-semibold">{machine.oee_score || '--'}%</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}