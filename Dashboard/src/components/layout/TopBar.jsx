import React from 'react';
import { Bell, Search, Wifi, WifiOff } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';

export default function TopBar({ alertCount = 0 }) {
  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur-xl flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div className="relative w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search machines, alerts, models..."
            className="pl-10 bg-secondary border-border h-9 text-sm"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Live Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/10 border border-accent/20">
          <Wifi className="w-3.5 h-3.5 text-accent" />
          <span className="text-xs font-medium text-accent">Live</span>
        </div>

        {/* Alert Bell */}
        <button className="relative p-2 rounded-lg hover:bg-secondary transition-colors">
          <Bell className="w-5 h-5 text-muted-foreground" />
          {alertCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-destructive text-[10px] font-bold text-destructive-foreground flex items-center justify-center">
              {alertCount > 9 ? '9+' : alertCount}
            </span>
          )}
        </button>

        {/* Timestamp */}
        <div className="text-xs font-mono text-muted-foreground">
          {new Date().toLocaleTimeString()}
        </div>
      </div>
    </header>
  );
}