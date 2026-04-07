import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { Box, CheckCircle, Clock, AlertCircle, Archive, Loader2, Search, Filter } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const statusConfig = {
  training: { icon: Loader2, color: 'text-chart-3', bg: 'bg-chart-3/10 border-chart-3/20', spin: true },
  validating: { icon: Clock, color: 'text-chart-4', bg: 'bg-chart-4/10 border-chart-4/20' },
  deployed: { icon: CheckCircle, color: 'text-accent', bg: 'bg-accent/10 border-accent/20' },
  archived: { icon: Archive, color: 'text-muted-foreground', bg: 'bg-muted border-border' },
  failed: { icon: AlertCircle, color: 'text-destructive', bg: 'bg-destructive/10 border-destructive/20' },
};

export default function ModelRegistry() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [selectedModel, setSelectedModel] = useState(null);

  const { data: models = [] } = useQuery({
    queryKey: ['ml-models'],
    queryFn: () => base44.entities.MLModel.list(),
    initialData: [],
  });

  const filtered = models.filter(m => {
    const matchSearch = m.name?.toLowerCase().includes(search.toLowerCase());
    const matchType = typeFilter === 'all' || m.type === typeFilter;
    return matchSearch && matchType;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Model Registry</h1>
        <p className="text-sm text-muted-foreground mt-1">ML/AI model lifecycle management and monitoring</p>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search models..." className="pl-10" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-48">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="anomaly_detection">Anomaly Detection</SelectItem>
            <SelectItem value="predictive_maintenance">Predictive Maintenance</SelectItem>
            <SelectItem value="quality_inspection">Quality Inspection</SelectItem>
            <SelectItem value="defect_detection">Defect Detection</SelectItem>
            <SelectItem value="yield_prediction">Yield Prediction</SelectItem>
            <SelectItem value="slm_fine_tuned">SLM Fine-tuned</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Model Cards */}
        <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((model) => {
            const status = statusConfig[model.status] || statusConfig.archived;
            const StatusIcon = status.icon;
            return (
              <Card
                key={model.id}
                className={cn(
                  "bg-card border-border cursor-pointer transition-all hover:border-primary/30",
                  selectedModel?.id === model.id && "border-primary/30"
                )}
                onClick={() => setSelectedModel(model)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="font-semibold text-sm text-foreground">{model.name}</p>
                      <p className="text-xs text-muted-foreground font-mono">v{model.version || '1.0'}</p>
                    </div>
                    <Badge className={cn("text-[10px] border", status.bg, status.color)}>
                      <StatusIcon className={cn("w-3 h-3 mr-1", status.spin && "animate-spin")} />
                      {model.status}
                    </Badge>
                  </div>
                  <Badge variant="outline" className="text-[10px] mb-3">{model.type?.replace(/_/g, ' ')}</Badge>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <div>
                      <p className="text-[10px] text-muted-foreground">Accuracy</p>
                      <p className="text-sm font-bold text-foreground">{model.accuracy || '--'}%</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground">F1 Score</p>
                      <p className="text-sm font-bold text-foreground">{model.f1_score || '--'}</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground">Inference</p>
                      <p className="text-sm font-bold text-foreground">{model.inference_time_ms || '--'}ms</p>
                    </div>
                    <div>
                      <p className="text-[10px] text-muted-foreground">Framework</p>
                      <p className="text-sm font-bold text-foreground">{model.framework || '--'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
          {filtered.length === 0 && (
            <div className="col-span-full bg-card border border-border rounded-xl p-12 text-center text-muted-foreground">
              <Box className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p>No models found</p>
            </div>
          )}
        </div>

        {/* Model Detail Panel */}
        <div>
          {selectedModel ? (
            <Card className="bg-card border-border sticky top-6">
              <CardHeader>
                <CardTitle className="text-base">{selectedModel.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {[
                    { label: 'Version', value: selectedModel.version || '1.0' },
                    { label: 'Type', value: selectedModel.type?.replace(/_/g, ' ') },
                    { label: 'Framework', value: selectedModel.framework },
                    { label: 'Status', value: selectedModel.status },
                    { label: 'Accuracy', value: `${selectedModel.accuracy || '--'}%` },
                    { label: 'Precision', value: selectedModel.precision_score || '--' },
                    { label: 'Recall', value: selectedModel.recall_score || '--' },
                    { label: 'F1 Score', value: selectedModel.f1_score || '--' },
                    { label: 'Inference Time', value: `${selectedModel.inference_time_ms || '--'}ms` },
                    { label: 'Training Size', value: selectedModel.training_data_size?.toLocaleString() || '--' },
                  ].map(({ label, value }) => (
                    <div key={label} className="flex justify-between text-sm">
                      <span className="text-muted-foreground">{label}</span>
                      <span className="font-medium text-foreground">{value}</span>
                    </div>
                  ))}
                </div>
                {selectedModel.description && (
                  <div className="pt-3 border-t border-border">
                    <p className="text-xs text-muted-foreground">{selectedModel.description}</p>
                  </div>
                )}
                {selectedModel.azure_endpoint && (
                  <div className="pt-3 border-t border-border">
                    <p className="text-[10px] text-muted-foreground">Azure Endpoint</p>
                    <p className="text-xs font-mono text-primary break-all">{selectedModel.azure_endpoint}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card className="bg-card border-border">
              <CardContent className="flex items-center justify-center h-64 text-muted-foreground text-sm">
                <div className="text-center">
                  <Box className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p>Select a model to view details</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}