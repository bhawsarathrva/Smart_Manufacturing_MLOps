import React from 'react';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function KPICard({ title, value, unit, trend, trendValue, icon: Icon, color = 'primary' }) {
  const colorMap = {
    primary: 'text-primary bg-primary/10 border-primary/20',
    accent: 'text-accent bg-accent/10 border-accent/20',
    destructive: 'text-destructive bg-destructive/10 border-destructive/20',
    chart3: 'text-chart-3 bg-chart-3/10 border-chart-3/20',
    chart4: 'text-chart-4 bg-chart-4/10 border-chart-4/20',
  };

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Minus;

  return (
    <div className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-all duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className={cn("p-2.5 rounded-lg border", colorMap[color])}>
          <Icon className="w-5 h-5" />
        </div>
        {trendValue && (
          <div className={cn(
            "flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full",
            trend === 'up' ? "text-accent bg-accent/10" : trend === 'down' ? "text-destructive bg-destructive/10" : "text-muted-foreground bg-muted"
          )}>
            <TrendIcon className="w-3 h-3" />
            {trendValue}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-foreground tracking-tight">
          {value}<span className="text-sm font-normal text-muted-foreground ml-1">{unit}</span>
        </p>
        <p className="text-xs text-muted-foreground uppercase tracking-wider">{title}</p>
      </div>
    </div>
  );
}