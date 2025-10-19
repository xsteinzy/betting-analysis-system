
import { ComingSoon } from '@/components/coming-soon'
import { BookOpen } from 'lucide-react'

export default function BetTrackerPage() {
  return (
    <ComingSoon
      icon={BookOpen}
      title="Bet Tracker"
      description="Track your bets, monitor performance, and analyze your betting history with detailed statistics and insights."
      features={[
        "Track active and completed bets",
        "Performance analytics and ROI tracking",
        "Detailed bet history and filtering",
        "Profit/loss statements and reporting",
        "Bankroll management tools",
        "Win rate and streak analysis"
      ]}
    />
  )
}
