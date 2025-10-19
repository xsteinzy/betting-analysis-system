
import { ValueFinderForm } from '@/components/value-finder/value-finder-form'
import { ValueFinderResults } from '@/components/value-finder/value-finder-results'

export default function ValueFinderPage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Value Finder</h1>
        <p className="text-muted-foreground">
          Analyze specific player props to find betting value and get model recommendations
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ValueFinderForm />
        <ValueFinderResults />
      </div>
    </div>
  )
}
