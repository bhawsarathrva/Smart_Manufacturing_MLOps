import React from 'react';
import { Database, ArrowRight, Cloud, Server, Brain, Layers, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

const pipelineStages = [
  {
    name: 'Data Ingestion',
    icon: Server,
    color: 'primary',
    status: 'active',
    components: [
      { name: 'Azure IoT Hub', status: 'running', throughput: '12.4K msgs/min' },
      { name: 'Event Hubs', status: 'running', throughput: '8.2K events/min' },
      { name: 'Edge Gateway', status: 'running', throughput: '3.1K signals/sec' },
    ]
  },
  {
    name: 'Stream Processing',
    icon: Layers,
    color: 'accent',
    status: 'active',
    components: [
      { name: 'Azure Stream Analytics', status: 'running', throughput: '45ms latency' },
      { name: 'Real-time Anomaly Detection', status: 'running', throughput: '99.2% uptime' },
      { name: 'Data Enrichment', status: 'running', throughput: '10K records/min' },
    ]
  },
  {
    name: 'Storage & Lakehouse',
    icon: Database,
    color: 'chart3',
    status: 'active',
    components: [
      { name: 'Azure Data Lake Gen2', status: 'running', throughput: '2.4 TB stored' },
      { name: 'Azure Synapse Analytics', status: 'running', throughput: 'Hot/Cold tiering' },
      { name: 'Cosmos DB (Hot Path)', status: 'running', throughput: '<10ms reads' },
    ]
  },
  {
    name: 'ML Pipeline',
    icon: Brain,
    color: 'chart4',
    status: 'active',
    components: [
      { name: 'Azure ML Workspace', status: 'running', throughput: '3 active experiments' },
      { name: 'Feature Store', status: 'running', throughput: '142 features' },
      { name: 'Model Training (Phi-3 SLM)', status: 'training', throughput: 'Epoch 12/50' },
    ]
  },
  {
    name: 'Serving & Monitoring',
    icon: Cloud,
    color: 'primary',
    status: 'active',
    components: [
      { name: 'Azure ML Endpoints', status: 'running', throughput: '23ms avg inference' },
      { name: 'Dashboard API', status: 'running', throughput: '99.9% SLA' },
      { name: 'Alerts & Notifications', status: 'running', throughput: '47 rules active' },
    ]
  },
];

const statusIcons = {
  running: CheckCircle,
  training: Clock,
  error: AlertCircle,
};

const colorMap = {
  primary: 'text-primary bg-primary/10 border-primary/20',
  accent: 'text-accent bg-accent/10 border-accent/20',
  chart3: 'text-chart-3 bg-chart-3/10 border-chart-3/20',
  chart4: 'text-chart-4 bg-chart-4/10 border-chart-4/20',
};

export default function DataPipeline() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Data Pipeline</h1>
        <p className="text-sm text-muted-foreground mt-1">Azure-based data ingestion, processing, and ML pipeline architecture</p>
      </div>

      {/* Pipeline Visualization */}
      <div className="space-y-4">
        {pipelineStages.map((stage, idx) => {
          const StageIcon = stage.icon;
          const c = colorMap[stage.color];
          return (
            <div key={stage.name}>
              <Card className="bg-card border-border">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-3 text-base">
                    <div className={cn("p-2 rounded-lg border", c)}>
                      <StageIcon className="w-4 h-4" />
                    </div>
                    <div>
                      <span className="text-foreground">{stage.name}</span>
                      <span className="text-xs text-muted-foreground ml-3 font-mono">Stage {idx + 1}/5</span>
                    </div>
                    <Badge className={cn("ml-auto", c)}>{stage.status}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {stage.components.map((comp) => {
                      const StatusIcon = statusIcons[comp.status] || CheckCircle;
                      return (
                        <div key={comp.name} className="bg-secondary rounded-lg p-3 border border-border">
                          <div className="flex items-center gap-2 mb-2">
                            <StatusIcon className={cn(
                              "w-3.5 h-3.5",
                              comp.status === 'running' ? 'text-accent' : comp.status === 'training' ? 'text-chart-3' : 'text-destructive'
                            )} />
                            <span className="text-sm font-medium text-foreground">{comp.name}</span>
                          </div>
                          <p className="text-xs font-mono text-muted-foreground">{comp.throughput}</p>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
              {idx < pipelineStages.length - 1 && (
                <div className="flex justify-center py-1">
                  <ArrowRight className="w-5 h-5 text-muted-foreground rotate-90" />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* SLM Fine-tuning Info */}
      <Card className="bg-card border-chart-4/20">
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2 text-chart-4">
            <Brain className="w-5 h-5" />
            SLM Fine-Tuning Pipeline (Microsoft Phi-3)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'Base Model', value: 'Phi-3-mini-4k', desc: 'Microsoft SLM' },
              { label: 'Training Data', value: '148K samples', desc: 'Manufacturing domain' },
              { label: 'Fine-tuning', value: 'LoRA / QLoRA', desc: 'Parameter efficient' },
              { label: 'Deploy Target', value: 'Azure ML + Edge', desc: 'Hybrid inference' },
            ].map((item) => (
              <div key={item.label} className="bg-chart-4/5 border border-chart-4/20 rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{item.label}</p>
                <p className="text-lg font-bold text-foreground mt-1">{item.value}</p>
                <p className="text-[11px] text-chart-4">{item.desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}