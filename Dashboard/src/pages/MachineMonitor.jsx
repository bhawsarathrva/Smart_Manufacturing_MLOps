import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { cn } from '@/lib/utils';
import { Cpu, Thermometer, Zap, Clock, Activity, Wrench, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const statusConfig = {
  running: { label: 'Running', color: 'bg-accent text-accent-foreground' },
  idle: { label: 'Idle', color: 'bg-chart-3/20 text-chart-3' },
  maintenance: { label: 'Maintenance', color: 'bg-chart-4/20 text-chart-4' },
  error: { label: 'Error', color: 'bg-destructive/20 text-destructive' },
  offline: { label: 'Offline', color: 'bg-muted text-muted-foreground' },
};

const mockTrendData = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i}:00`,
  temp: 45 + Math.random() * 30,
  vibration: 1.2 + Math.random() * 2,
  power: 12 + Math.random() * 8,
}));

export default function MachineMonitor() {
  const [search, setSearch] = useState('');
  const [selectedMachine, setSelectedMachine] = useState(null);

  const { data: machines = [] } = useQuery({
    queryKey: ['machines'],
    queryFn: () => base44.entities.Machine.list(),
    initialData: [],
  });

  const filtered = machines.filter(m =>
    m.name?.toLowerCase().includes(search.toLowerCase()) ||
    m.location?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Machine Monitor</h1>
          <p className="text-sm text-muted-foreground mt-1">Real-time equipment health monitoring</p>
        </div>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search machines..." className="pl-10" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Machine List */}
        <div className="lg:col-span-1 space-y-3 max-h-[600px] overflow-y-auto pr-1">
          {filtered.map((machine) => {
            const status = statusConfig[machine.status] || statusConfig.offline;
            return (
              <button
                key={machine.id}
                onClick={() => setSelectedMachine(machine)}
                className={cn(
                  "w-full text-left p-4 rounded-xl border transition-all duration-200",
                  selectedMachine?.id === machine.id
                    ? "bg-primary/5 border-primary/30"
                    : "bg-card border-border hover:border-primary/20"
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm text-foreground">{machine.name}</span>
                  <Badge className={cn("text-[10px]", status.color)}>{status.label}</Badge>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1"><Thermometer className="w-3 h-3" />{machine.temperature || '--'}°C</div>
                  <div className="flex items-center gap-1"><Zap className="w-3 h-3" />{machine.power_consumption || '--'}kW</div>
                  <div className="flex items-center gap-1"><Activity className="w-3 h-3" />OEE {machine.oee_score || '--'}%</div>
                </div>
              </button>
            );
          })}
          {filtered.length === 0 && (
            <div className="text-center py-12 text-muted-foreground text-sm">No machines found</div>
          )}
        </div>

        {/* Machine Detail */}
        <div className="lg:col-span-2">
          {selectedMachine ? (
            <div className="space-y-4">
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-foreground">{selectedMachine.name}</h2>
                    <p className="text-sm text-muted-foreground">{selectedMachine.location} • {selectedMachine.type}</p>
                  </div>
                  <Badge className={cn("text-xs", statusConfig[selectedMachine.status]?.color)}>
                    {selectedMachine.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[
                    { icon: Thermometer, label: 'Temperature', value: `${selectedMachine.temperature || '--'}°C` },
                    { icon: Activity, label: 'Vibration', value: `${selectedMachine.vibration || '--'} mm/s` },
                    { icon: Zap, label: 'Power', value: `${selectedMachine.power_consumption || '--'} kW` },
                    { icon: Clock, label: 'Cycle Time', value: `${selectedMachine.cycle_time || '--'}s` },
                  ].map(({ icon: StatIcon, label, value }) => (
                    <div key={label} className="bg-secondary rounded-lg p-3">
                      <StatIcon className="w-4 h-4 text-primary mb-1" />
                      <p className="text-xs text-muted-foreground">{label}</p>
                      <p className="text-lg font-bold text-foreground">{value}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">Sensor Trends (24h)</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={mockTrendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 30%, 16%)" />
                    <XAxis dataKey="hour" tick={{ fontSize: 10, fill: 'hsl(215, 20%, 55%)' }} stroke="hsl(222, 30%, 16%)" />
                    <YAxis tick={{ fontSize: 10, fill: 'hsl(215, 20%, 55%)' }} stroke="hsl(222, 30%, 16%)" />
                    <Tooltip contentStyle={{ background: 'hsl(222, 44%, 8%)', border: '1px solid hsl(222, 30%, 16%)', borderRadius: '8px', fontSize: '12px' }} />
                    <Line type="monotone" dataKey="temp" name="Temp (°C)" stroke="hsl(187, 92%, 50%)" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="vibration" name="Vibration" stroke="hsl(160, 84%, 44%)" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="power" name="Power (kW)" stroke="hsl(43, 96%, 58%)" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div className="bg-card border border-border rounded-xl flex items-center justify-center h-96 text-muted-foreground text-sm">
              <div className="text-center">
                <Cpu className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Select a machine to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}