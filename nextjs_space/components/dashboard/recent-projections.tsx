
'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'
import { mockProjections } from '@/lib/mock-data'
import Link from 'next/link'

export function RecentProjections() {
  const recentProjections = mockProjections.slice(0, 5)

  return (
    <Card className="border-muted">
      <CardHeader>
        <CardTitle className="text-xl">Recent Projections</CardTitle>
        <CardDescription>Latest model predictions with high confidence</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {recentProjections.map((projection) => (
          <div key={projection.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-muted">
            <div className="space-y-1">
              <div className="font-medium text-sm">{projection.playerName}</div>
              <div className="text-xs text-muted-foreground">{projection.propType}</div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-xs">
                  {projection.sport}
                </Badge>
                <Badge 
                  variant="outline"
                  className={`text-xs ${
                    projection.confidence === 'High' 
                      ? 'border-green-500 text-green-500' 
                      : projection.confidence === 'Medium'
                      ? 'border-yellow-500 text-yellow-500'
                      : 'border-red-500 text-red-500'
                  }`}
                >
                  {projection.confidence}
                </Badge>
              </div>
            </div>
            <div className="text-right">
              <div className={`font-bold ${projection.expectedValue > 0 ? 'text-green-500' : 'text-red-500'}`}>
                {projection.expectedValue > 0 ? '+' : ''}{projection.expectedValue}
              </div>
              <div className="text-xs text-muted-foreground">EV</div>
            </div>
          </div>
        ))}
        
        <Link href="/projections">
          <Button className="w-full" variant="outline">
            View All Projections
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}
