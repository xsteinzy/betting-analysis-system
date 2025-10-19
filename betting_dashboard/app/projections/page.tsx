
import { ProjectionsTable } from '@/components/projections/projections-table'
import { ProjectionsFilters } from '@/components/projections/projections-filters'

export default function ProjectionsPage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Sports Projections</h1>
        <p className="text-muted-foreground">
          AI-powered projections and expected value analysis for today's games
        </p>
      </div>

      <ProjectionsFilters />
      
      <ProjectionsTable />
    </div>
  )
}
