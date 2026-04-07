import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const mockData = [
  { time: '00:00', output: 120, defects: 3, oee: 87 },
  { time: '02:00', output: 115, defects: 2, oee: 89 },
  { time: '04:00', output: 130, defects: 4, oee: 85 },
  { time: '06:00', output: 180, defects: 5, oee: 88 },
  { time: '08:00', output: 220, defects: 6, oee: 91 },
  { time: '10:00', output: 245, defects: 3, oee: 93 },
  { time: '12:00', output: 200, defects: 8, oee: 86 },
  { time: '14:00', output: 235, defects: 4, oee: 90 },
  { time: '16:00', output: 250, defects: 2, oee: 94 },
  { time: '18:00', output: 210, defects: 5, oee: 89 },
  { time: '20:00', output: 175, defects: 3, oee: 91 },
  { time: '22:00', output: 140, defects: 2, oee: 92 },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-card border border-border rounded-lg p-3 shadow-xl">
      <p className="text-xs font-mono text-muted-foreground mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} className="text-xs font-medium" style={{ color: p.stroke }}>
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

export default function ProductionChart() {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider">Production Output (24h)</h3>
      </div>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={mockData}>
          <defs>
            <linearGradient id="outputGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(187, 92%, 50%)" stopOpacity={0.3} />
              <stop offset="100%" stopColor="hsl(187, 92%, 50%)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="oeeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(160, 84%, 44%)" stopOpacity={0.2} />
              <stop offset="100%" stopColor="hsl(160, 84%, 44%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 30%, 16%)" />
          <XAxis dataKey="time" tick={{ fontSize: 11, fill: 'hsl(215, 20%, 55%)' }} stroke="hsl(222, 30%, 16%)" />
          <YAxis tick={{ fontSize: 11, fill: 'hsl(215, 20%, 55%)' }} stroke="hsl(222, 30%, 16%)" />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="output" name="Output" stroke="hsl(187, 92%, 50%)" fill="url(#outputGradient)" strokeWidth={2} />
          <Area type="monotone" dataKey="oee" name="OEE %" stroke="hsl(160, 84%, 44%)" fill="url(#oeeGradient)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}