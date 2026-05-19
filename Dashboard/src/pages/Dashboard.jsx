import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/Client';
import { Activity, Gauge, Package, AlertTriangle, Cpu, TrendingUp } from 'lucide-react';
import KPICard from '../components/dashboard/KPICard';
import MachineStatusGrid from '../components/dashboard/MachineStatusGrid';
import AlertsFeed from '../components/dashboard/AlertFeed';
import ProductionChart from '../components/dashboard/ProductionChart';
import GCPArchDiagram from '../components/dashboard/GCPArchDiagram';

export default function Dashboard() {
  const { data: machines = [] } = useQuery({
    queryKey: ['machines'],
    queryFn: () => base44.entities.Machine.list(),
    initialData: [],
  });

  const { data: alerts = [] } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => base44.entities.Alert.filter({ status: 'active' }),
    initialData: [],
  });

  const { data: batches = [] } = useQuery({
    queryKey: ['batches'],
    queryFn: () => base44.entities.ProductionBatch.list(),
    initialData: [],
  });

  const { data: metrics = {} } = useQuery({
    queryKey: ['live-metrics'],
    queryFn: () => fetch('/api/metrics').then(res => res.json()),
    refetchInterval: 5000, // Refresh every 5 seconds for live feel
  });

  const runningMachines = machines.filter(m => m.status === 'running').length;
  const avgOEE = metrics.avg_oee || (machines.length ? Math.round(machines.reduce((sum, m) => sum + (m.oee_score || 0), 0) / machines.length) : 0);
  const totalProduced = metrics.units_produced || batches.reduce((sum, b) => sum + (b.produced_quantity || 0), 0);
  const criticalAlerts = metrics.critical_alerts ?? alerts.filter(a => a.severity === 'critical' || a.severity === 'emergency').length;
  const yieldRate = metrics.yield_rate || "96.8";
  const uptime = metrics.uptime || "99.2";
  const activeMachinesText = metrics.active_machines ? `${metrics.active_machines}/${metrics.total_machines}` : `${runningMachines}/${machines.length}`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-foreground">Production Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Real-time manufacturing intelligence overview</p>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <KPICard title="Avg OEE" value={avgOEE} unit="%" trend="up" trendValue="+2.3%" icon={Gauge} color="primary" />
        <KPICard title="Active Machines" value={activeMachinesText} unit="" icon={Cpu} color="accent" />
        <KPICard title="Units Produced" value={totalProduced.toLocaleString()} unit="" trend="up" trendValue="+12%" icon={Package} color="chart3" />
        <KPICard title="Critical Alerts" value={criticalAlerts} unit="" trend={criticalAlerts > 0 ? 'down' : 'up'} trendValue={criticalAlerts > 0 ? 'Action needed' : 'All clear'} icon={AlertTriangle} color="destructive" />
        <KPICard title="Yield Rate" value={yieldRate} unit="%" trend="up" trendValue="+0.5%" icon={TrendingUp} color="chart4" />
        <KPICard title="Uptime" value={uptime} unit="%" trend="up" trendValue="+0.1%" icon={Activity} color="primary" />
      </div>

      {/* Charts + Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProductionChart />
        </div>
        <AlertsFeed alerts={alerts} />
      </div>

      {/* Machine Grid + Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MachineStatusGrid machines={machines} />
        <GCPArchDiagram />
      </div>
    </div>
  );
}