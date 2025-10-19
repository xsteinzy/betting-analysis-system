
import { ComingSoon } from '@/components/coming-soon'
import { BarChart3 } from 'lucide-react'

export default function AnalyticsPage() {
  return (
    <ComingSoon
      icon={BarChart3}
      title="Performance Analytics"
      description="Deep dive into your betting performance with advanced analytics, charts, and insights to optimize your strategy."
      features={[
        "Advanced performance metrics and KPIs",
        "Interactive charts and visualizations",
        "Sport and prop type breakdowns", 
        "Market efficiency analysis",
        "Historical trend analysis",
        "Custom reporting and insights"
      ]}
    />
  )
}
