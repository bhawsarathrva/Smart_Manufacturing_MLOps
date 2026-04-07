import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { base44 } from '@/api/base44Client';
import { Activity, Gauge, Package, AlertTriangle, Cpu, TrendingUp } from 'lucide-react';
import KPICard from '../components/dashboard/KPICard';
import MachineStatusGrid from '../components/dashboard/MachineStatusGrid';
import AlertsFeed from '../components/dashboard/AlertsFeed';
import ProductionChart from '../components/dashboard/ProductionChart';
import AzureArchDiagram from '../components/dashboard/AzureArchDiagram';

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

  const runningMachines = machines.filter(m => m.status === 'running').length;
  const avgOEE = machines.length ? Math.round(machines.reduce((sum, m) => sum + (m.oee_score || 0), 0) / machines.length) : 0;
  const totalProduced = batches.reduce((sum, b) => sum + (b.produced_quantity || 0), 0);
  const criticalAlerts = alerts.filter(a => a.severity === 'critical' || a.severity === 'emergency').length;

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
        <KPICard title="Active Machines" value={`${runningMachines}/${machines.length}`} unit="" icon={Cpu} color="accent" />
        <KPICard title="Units Produced" value={totalProduced.toLocaleString()} unit="" trend="up" trendValue="+12%" icon={Package} color="chart3" />
        <KPICard title="Critical Alerts" value={criticalAlerts} unit="" trend={criticalAlerts > 0 ? 'down' : 'up'} trendValue={criticalAlerts > 0 ? 'Action needed' : 'All clear'} icon={AlertTriangle} color="destructive" />
        <KPICard title="Yield Rate" value="96.8" unit="%" trend="up" trendValue="+0.5%" icon={TrendingUp} color="chart4" />
        <KPICard title="Uptime" value="99.2" unit="%" trend="up" trendValue="+0.1%" icon={Activity} color="primary" />
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
        <AzureArchDiagram />
      </div>
    </div>
  );
}