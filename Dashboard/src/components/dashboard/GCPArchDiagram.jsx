import React from 'react';
import { Cloud, Database, Cpu, Camera, Brain, ArrowRight, Server, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

const layers = [
  {
    label: 'Edge Layer',
    color: 'primary',
    items: [
      { icon: Cpu, label: 'IoT Sensors' },
      { icon: Camera, label: 'Camera Feeds' },
      { icon: Server, label: 'Edge Compute' },
    ]
  },
  {
    label: 'GCP Ingestion',
    color: 'accent',
    items: [
      { icon: Cloud, label: 'Pub/Sub' },
      { icon: Database, label: 'Dataflow' },
      { icon: Shield, label: 'Secret Manager' },
    ]
  },
  {
    label: 'AI/ML Pipeline',
    color: 'chart3',
    items: [
      { icon: Brain, label: 'Vertex AI' },
      { icon: Database, label: 'BigQuery' },
      { icon: Cpu, label: 'Phi-3 SLM' },
    ]
  },
];

const colorClasses = {
  primary: { bg: 'bg-primary/10', border: 'border-primary/30', text: 'text-primary', icon: 'text-primary' },
  accent: { bg: 'bg-accent/10', border: 'border-accent/30', text: 'text-accent', icon: 'text-accent' },
  chart3: { bg: 'bg-chart-3/10', border: 'border-chart-3/30', text: 'text-chart-3', icon: 'text-chart-3' },
};

export default function GCPArchDiagram() {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-4">GCP Cloud Architecture</h3>
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {layers.map((layer, i) => {
          const c = colorClasses[layer.color];
          return (
            <React.Fragment key={layer.label}>
              <div className={cn("flex-1 min-w-[140px] rounded-lg border p-3", c.bg, c.border)}>
                <p className={cn("text-[10px] font-bold uppercase tracking-widest mb-3", c.text)}>{layer.label}</p>
                <div className="space-y-2">
                  {layer.items.map(({ icon: ItemIcon, label }) => (
                    <div key={label} className="flex items-center gap-2">
                      <ItemIcon className={cn("w-3.5 h-3.5", c.icon)} />
                      <span className="text-xs text-foreground/80">{label}</span>
                    </div>
                  ))}
                </div>
              </div>
              {i < layers.length - 1 && (
                <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}