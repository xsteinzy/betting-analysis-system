
import { DashboardOverview } from '@/components/dashboard/dashboard-overview'
import { QuickStats } from '@/components/dashboard/quick-stats'
import { RecentProjections } from '@/components/dashboard/recent-projections'
import { PerformanceChart } from '@/components/dashboard/performance-chart'

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Betting Analysis Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to your comprehensive sports betting analysis platform. Track projections, find value, and optimize your betting strategy.
        </p>
      </div>

      <QuickStats />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <PerformanceChart />
        </div>
        <div>
          <RecentProjections />
        </div>
      </div>

      <DashboardOverview />
    </div>
  )
}
