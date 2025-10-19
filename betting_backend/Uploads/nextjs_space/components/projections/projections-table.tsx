
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { mockProjections } from '@/lib/mock-data'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export function ProjectionsTable() {
  const { toast } = useToast()

  const handleBetAction = (projection: any, action: 'BET' | 'PASS') => {
    toast({
      title: action === 'BET' ? "Bet Placed" : "Bet Skipped",
      description: `${action === 'BET' ? 'Placed bet on' : 'Skipped'} ${projection.playerName} ${projection.propType}`,
    })
  }

  return (
    <Card className="border-muted">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Active Projections</CardTitle>
          <Badge variant="outline" className="text-xs">
            {mockProjections.length} Total
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-border bg-muted/20">
              <tr>
                <th className="text-left p-4 text-sm font-medium text-muted-foreground">Player</th>
                <th className="text-left p-4 text-sm font-medium text-muted-foreground">Sport</th>
                <th className="text-left p-4 text-sm font-medium text-muted-foreground">Prop</th>
                <th className="text-center p-4 text-sm font-medium text-muted-foreground">Line</th>
                <th className="text-center p-4 text-sm font-medium text-muted-foreground">Projection</th>
                <th className="text-center p-4 text-sm font-medium text-muted-foreground">Confidence</th>
                <th className="text-center p-4 text-sm font-medium text-muted-foreground">Expected Value</th>
                <th className="text-center p-4 text-sm font-medium text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody>
              {mockProjections.map((projection, index) => (
                <tr key={projection.id} className={`border-b border-border hover:bg-muted/30 transition-colors ${index % 2 === 0 ? 'bg-background' : 'bg-muted/10'}`}>
                  <td className="p-4">
                    <div className="font-medium text-foreground">{projection.playerName}</div>
                  </td>
                  <td className="p-4">
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        projection.sport === 'NFL' 
                          ? 'border-red-500 text-red-500 bg-red-500/10' 
                          : 'border-orange-500 text-orange-500 bg-orange-500/10'
                      }`}
                    >
                      {projection.sport}
                    </Badge>
                  </td>
                  <td className="p-4">
                    <div className="text-sm text-foreground">{projection.propType}</div>
                  </td>
                  <td className="p-4 text-center">
                    <div className="font-mono text-sm text-foreground">{projection.line}</div>
                  </td>
                  <td className="p-4 text-center">
                    <div className="font-mono text-sm font-medium text-foreground">{projection.projection}</div>
                  </td>
                  <td className="p-4 text-center">
                    <Badge 
                      variant="outline"
                      className={`text-xs ${
                        projection.confidence === 'High' 
                          ? 'border-green-500 text-green-500 bg-green-500/10' 
                          : projection.confidence === 'Medium'
                          ? 'border-yellow-500 text-yellow-500 bg-yellow-500/10'
                          : 'border-red-500 text-red-500 bg-red-500/10'
                      }`}
                    >
                      {projection.confidence}
                    </Badge>
                  </td>
                  <td className="p-4 text-center">
                    <div className={`flex items-center justify-center space-x-1 font-mono text-sm font-bold ${
                      projection.expectedValue > 0 
                        ? 'text-green-500' 
                        : projection.expectedValue < 0 
                        ? 'text-red-500' 
                        : 'text-muted-foreground'
                    }`}>
                      {projection.expectedValue > 0 ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : projection.expectedValue < 0 ? (
                        <TrendingDown className="h-3 w-3" />
                      ) : (
                        <Minus className="h-3 w-3" />
                      )}
                      <span>
                        {projection.expectedValue > 0 ? '+' : ''}{projection.expectedValue}
                      </span>
                    </div>
                  </td>
                  <td className="p-4 text-center">
                    <Button 
                      size="sm"
                      variant={projection.expectedValue > 0 ? "default" : "outline"}
                      className={projection.expectedValue > 0 ? "bg-green-600 hover:bg-green-700 text-white" : ""}
                      onClick={() => handleBetAction(projection, projection.expectedValue > 0 ? 'BET' : 'PASS')}
                    >
                      {projection.expectedValue > 0 ? 'BET' : 'PASS'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}
