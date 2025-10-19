
'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

const performanceData = [
  { date: 'Oct 1', roi: 5.2, bets: 12 },
  { date: 'Oct 2', roi: 8.1, bets: 15 },
  { date: 'Oct 3', roi: 6.8, bets: 9 },
  { date: 'Oct 4', roi: 12.4, bets: 18 },
  { date: 'Oct 5', roi: 9.7, bets: 14 },
  { date: 'Oct 6', roi: 15.2, bets: 16 },
  { date: 'Oct 7', roi: 11.8, bets: 13 },
  { date: 'Oct 8', roi: 18.5, bets: 20 },
  { date: 'Oct 9', roi: 14.2, bets: 17 },
  { date: 'Oct 10', roi: 21.3, bets: 22 },
  { date: 'Oct 11', roi: 19.8, bets: 19 }
]

export function PerformanceChart() {
  return (
    <Card className="border-muted">
      <CardHeader>
        <CardTitle className="text-xl">Performance Overview</CardTitle>
        <CardDescription>ROI and betting volume over the last 10 days</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={performanceData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 20,
              }}
            >
              <defs>
                <linearGradient id="roiGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="date" 
                tickLine={false}
                tick={{ fontSize: 10 }}
                axisLine={false}
                className="text-muted-foreground"
              />
              <YAxis 
                tickLine={false}
                tick={{ fontSize: 10 }}
                axisLine={false}
                className="text-muted-foreground"
                label={{ 
                  value: 'ROI (%)', 
                  angle: -90, 
                  position: 'insideLeft', 
                  style: { textAnchor: 'middle', fontSize: 11 } 
                }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'hsl(var(--background))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  fontSize: '11px'
                }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Area
                type="monotone"
                dataKey="roi"
                stroke="#10b981"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#roiGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-border">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">+14.2%</div>
            <div className="text-xs text-muted-foreground">Avg ROI</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-foreground">175</div>
            <div className="text-xs text-muted-foreground">Total Bets</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-500">72%</div>
            <div className="text-xs text-muted-foreground">Win Rate</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
