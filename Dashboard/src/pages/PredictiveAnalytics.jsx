import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { predictMaintenance } from '@/api/mlClient';
import { Brain, TrendingUp, AlertTriangle, Target, Loader2, Gauge, Activity, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const FEATURES = [
  'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
  'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
  'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
  'Predictive_Maintenance_Score', 'Error_Rate_%', 'Year', 'Month', 'Day', 'Hour'
];

const predictiveData = [
  /* ... same as before ... */
  { machine: 'CNC-01', failure_prob: 12, days_to_maintenance: 45 },
  { machine: 'Robot-A2', failure_prob: 67, days_to_maintenance: 8 },
  { machine: 'Conv-B1', failure_prob: 5, days_to_maintenance: 90 },
  { machine: 'Press-03', failure_prob: 34, days_to_maintenance: 22 },
  { machine: 'Welder-C1', failure_prob: 89, days_to_maintenance: 3 },
  { machine: 'Inspect-D', failure_prob: 18, days_to_maintenance: 55 },
];

const qualityMetrics = [
  { name: 'Yield', value: 96.8, fill: 'hsl(160, 84%, 44%)' },
  { name: 'FPY', value: 93.2, fill: 'hsl(187, 92%, 50%)' },
  { name: 'Scrap Rate', value: 2.1, fill: 'hsl(43, 96%, 58%)' },
];

export default function PredictiveAnalytics() {
  const [aiInsight, setAiInsight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mlLoading, setMlLoading] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [mlData, setMlData] = useState({
    Operation_Mode: 1,
    Temperature_C: 75.5,
    Vibration_Hz: 45.2,
    Power_Consumption_kW: 120.4,
    Network_Latency_ms: 12.5,
    'Packet_Loss_%': 0.1,
    'Quality_Control_Defect_Rate_%': 1.2,
    Production_Speed_units_per_hr: 500,
    Predictive_Maintenance_Score: 85,
    'Error_Rate_%': 0.5,
    Year: new Date().getFullYear(),
    Month: new Date().getMonth() + 1,
    Day: new Date().getDate(),
    Hour: new Date().getHours(),
  });

  const { data: machines = [] } = useQuery({
    queryKey: ['machines'],
    queryFn: () => base44.entities.Machine.list(),
    initialData: [],
  });

  const handlePredict = async () => {
    setMlLoading(true);
    try {
      const result = await predictMaintenance(mlData);
      setPredictionResult(result.prediction);
      toast.success(`Success: Maintenance Risk Is ${result.prediction}`);
    } catch (error) {
      toast.error('Failed to get prediction from ML pipeline');
    } finally {
      setMlLoading(false);
    }
  };

  const runAnalysis = async () => {
    setLoading(true);
    const machineData = machines.map(m => ({
      name: m.name,
      status: m.status,
      oee: m.oee_score,
      temp: m.temperature,
      vibration: m.vibration,
      power: m.power_consumption,
    }));

    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Analyze this machine fleet data: ${JSON.stringify(machineData)}`,
      response_json_schema: {
        type: "object",
        properties: {
          at_risk_machines: { type: "array", items: { type: "object", properties: { name: { type: "string" }, risk_level: { type: "string" }, reasoning: { type: "string" } } } },
          maintenance_recommendations: { type: "array", items: { type: "string" } },
          efficiency_suggestions: { type: "array", items: { type: "string" } },
          anomaly_patterns: { type: "array", items: { type: "string" } },
          overall_health_score: { type: "number" },
        }
      }
    });
    setAiInsight(result);
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Predictive Analytics</h1>
          <p className="text-sm text-muted-foreground mt-1">Integrated ML pipeline & AI-powered optimization</p>
        </div>
        <Button onClick={runAnalysis} disabled={loading} className="bg-primary text-primary-foreground">
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Brain className="w-4 h-4 mr-2" />}
          Run AI Analysis
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="bg-card border-border">
          <CardHeader><CardTitle className="text-sm uppercase tracking-wider">Failure Probability (%)</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={predictiveData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222, 30%, 16%)" />
                <XAxis type="number" tick={{ fontSize: 11, fill: 'hsl(215, 20%, 55%)' }} />
                <YAxis dataKey="machine" type="category" tick={{ fontSize: 11, fill: 'hsl(215, 20%, 55%)' }} width={80} />
                <Tooltip contentStyle={{ background: 'hsl(222, 44%, 8%)', border: '1px solid hsl(222, 30%, 16%)' }} />
                <Bar dataKey="failure_prob" fill="hsl(0, 72%, 56%)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Live ML Pipeline Ingestion */}
        <Card className="bg-card border-accent/20 border">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-semibold uppercase tracking-wider flex items-center gap-2 text-accent">
              <Activity className="w-4 h-4" />
              Machine Learning Pipeline Inference
            </CardTitle>
            <Badge variant="outline" className="text-[10px] text-accent border-accent/30">Live Production Model</Badge>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 mb-4">
              <div className="space-y-1.5">
                <label className="text-[10px] text-muted-foreground uppercase">Temperature (°C)</label>
                <div className="relative">
                  <Gauge className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  <Input 
                    type="number" 
                    value={mlData.Temperature_C} 
                    onChange={e => setMlData({...mlData, Temperature_C: e.target.value})}
                    className="pl-8 text-xs bg-secondary/50 border-border h-8"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] text-muted-foreground uppercase">Vibration (Hz)</label>
                <div className="relative">
                  <Activity className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  <Input 
                    type="number" 
                    value={mlData.Vibration_Hz} 
                    onChange={e => setMlData({...mlData, Vibration_Hz: e.target.value})}
                    className="pl-8 text-xs bg-secondary/50 border-border h-8"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] text-muted-foreground uppercase">Power (kW)</label>
                <div className="relative">
                  <Zap className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  <Input 
                    type="number" 
                    value={mlData.Power_Consumption_kW} 
                    onChange={e => setMlData({...mlData, Power_Consumption_kW: e.target.value})}
                    className="pl-8 text-xs bg-secondary/50 border-border h-8"
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-[10px] text-muted-foreground uppercase">Error Rate (%)</label>
                <div className="relative">
                  <AlertTriangle className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
                  <Input 
                    type="number" 
                    value={mlData['Error_Rate_%']} 
                    onChange={e => setMlData({...mlData, 'Error_Rate_%': e.target.value})}
                    className="pl-8 text-xs bg-secondary/50 border-border h-8"
                  />
                </div>
              </div>
            </div>
            
            <div className="p-3 bg-accent/5 rounded-lg border border-accent/20 flex items-center justify-between">
              <div>
                <p className="text-[10px] text-accent font-bold uppercase tracking-widest">Maintenance Risk</p>
                <p className={cn(
                  "text-xl font-bold mt-1",
                  predictionResult === 'High' ? 'text-destructive' : 
                  predictionResult === 'Medium' ? 'text-chart-3' : 
                  predictionResult === 'Low' ? 'text-accent' : 'text-muted-foreground'
                )}>
                  {predictionResult || "Waiting..."}
                </p>
              </div>
              <Button 
                size="sm" 
                onClick={handlePredict} 
                disabled={mlLoading}
                className="bg-accent text-accent-foreground hover:bg-accent/90"
              >
                {mlLoading && <Loader2 className="w-3 h-3 mr-2 animate-spin" />}
                Run Inference
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {aiInsight && (
        <Card className="bg-card border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-primary">
              <Brain className="w-5 h-5" />
              Advanced Fleet Optimization
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2"><Target className="w-4 h-4 text-accent" /> Recommendations</h4>
              <ul className="space-y-2">
                {aiInsight.maintenance_recommendations?.map((rec, i) => (
                  <li key={i} className="text-sm text-muted-foreground">• {rec}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2"><TrendingUp className="w-4 h-4 text-primary" /> Efficiency Suggestion</h4>
              <ul className="space-y-2">
                {aiInsight.efficiency_suggestions?.map((sug, i) => (
                  <li key={i} className="text-sm text-muted-foreground">• {sug}</li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}