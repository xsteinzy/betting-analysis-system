
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  TrendingUp, 
  Search, 
  BookOpen, 
  BarChart3, 
  ArrowRight, 
  Zap,
  Target,
  Calendar,
  Trophy
} from 'lucide-react'

const dashboardCards = [
  {
    title: "Today's Projections",
    description: "View AI-powered projections for today's games",
    icon: TrendingUp,
    href: "/projections",
    badge: "6 Active",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10"
  },
  {
    title: "Value Finder",
    description: "Analyze specific player props for betting value",
    icon: Search,
    href: "/value-finder", 
    badge: "Live Analysis",
    color: "text-green-500",
    bgColor: "bg-green-500/10"
  },
  {
    title: "Bet Tracker",
    description: "Track your bets and monitor performance",
    icon: BookOpen,
    href: "/bet-tracker",
    badge: "Coming Soon",
    color: "text-purple-500",
    bgColor: "bg-purple-500/10"
  },
  {
    title: "Performance Analytics",
    description: "Deep dive into your betting performance data",
    icon: BarChart3,
    href: "/analytics",
    badge: "Coming Soon", 
    color: "text-orange-500",
    bgColor: "bg-orange-500/10"
  }
]

const sportsOverview = [
  {
    sport: "NFL",
    games: 8,
    projections: 24,
    valueOppurtunities: 12,
    icon: Trophy,
    color: "text-red-500"
  },
  {
    sport: "NBA",
    games: 6,
    projections: 18,
    valueOppurtunities: 8,
    icon: Target,
    color: "text-orange-500"
  }
]

export function DashboardOverview() {
  return (
    <div className="space-y-8">
      {/* Main Action Cards */}
      <div>
        <h2 className="text-2xl font-semibold mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {dashboardCards.map((card) => {
            const Icon = card.icon
            return (
              <Card key={card.title} className="group hover:shadow-lg transition-all duration-200 border-muted">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className={`p-2 rounded-lg ${card.bgColor}`}>
                      <Icon className={`h-5 w-5 ${card.color}`} />
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {card.badge}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{card.title}</CardTitle>
                  <CardDescription className="text-sm">
                    {card.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <Link href={card.href}>
                    <Button 
                      className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors"
                      variant="outline"
                    >
                      Get Started
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Sports Overview */}
      <div>
        <h2 className="text-2xl font-semibold mb-6">Sports Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {sportsOverview.map((sport) => {
            const Icon = sport.icon
            return (
              <Card key={sport.sport} className="border-muted">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-muted">
                        <Icon className={`h-6 w-6 ${sport.color}`} />
                      </div>
                      <div>
                        <CardTitle className="text-xl">{sport.sport}</CardTitle>
                        <CardDescription>Active Games & Projections</CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-foreground">{sport.games}</div>
                      <div className="text-xs text-muted-foreground">Games Today</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-foreground">{sport.projections}</div>
                      <div className="text-xs text-muted-foreground">Projections</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-green-500">{sport.valueOppurtunities}</div>
                      <div className="text-xs text-muted-foreground">Value Ops</div>
                    </div>
                  </div>
                  <Link href="/projections">
                    <Button className="w-full" variant="outline">
                      View {sport.sport} Projections
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Today's Highlights */}
      <Card className="border-muted">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-yellow-500" />
            <CardTitle>Today's Highlights</CardTitle>
          </div>
          <CardDescription>Key insights and opportunities for today</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm font-medium">High Value Opportunity</span>
              </div>
              <div className="text-sm text-muted-foreground">LeBron James Points Over 25.5 showing +2.8 EV</div>
            </div>
            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                <span className="text-sm font-medium">Model Confidence</span>
              </div>
              <div className="text-sm text-muted-foreground">18 high-confidence projections available</div>
            </div>
            <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
              <div className="flex items-center space-x-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                <span className="text-sm font-medium">Market Edge</span>
              </div>
              <div className="text-sm text-muted-foreground">Finding +EV in 67% of analyzed props</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
