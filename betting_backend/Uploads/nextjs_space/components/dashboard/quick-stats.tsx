
'use client'

import { Card, CardContent } from '@/components/ui/card'
import { TrendingUp, Target, DollarSign, Percent } from 'lucide-react'
import { motion } from 'framer-motion'

const stats = [
  {
    title: "Active Projections",
    value: "42",
    change: "+12 today",
    icon: TrendingUp,
    color: "text-blue-500",
    bgColor: "bg-blue-500/10"
  },
  {
    title: "Positive EV Opportunities", 
    value: "18",
    change: "72% win rate",
    icon: Target,
    color: "text-green-500",
    bgColor: "bg-green-500/10"
  },
  {
    title: "Avg Expected Value",
    value: "+$2.40",
    change: "+15% from last week",
    icon: DollarSign,
    color: "text-purple-500", 
    bgColor: "bg-purple-500/10"
  },
  {
    title: "Model Accuracy",
    value: "84%",
    change: "Last 30 days",
    icon: Percent,
    color: "text-orange-500",
    bgColor: "bg-orange-500/10"
  }
]

export function QuickStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="border-muted hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                    <p className="text-3xl font-bold text-foreground">{stat.value}</p>
                    <p className="text-xs text-muted-foreground mt-1">{stat.change}</p>
                  </div>
                  <div className={`p-3 rounded-full ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )
      })}
    </div>
  )
}
