
'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Target, TrendingUp, TrendingDown, AlertCircle, CheckCircle } from 'lucide-react'
import { ValueAnalysis } from '@/lib/types'
import { useToast } from '@/hooks/use-toast'

// Mock initial analysis for demonstration
const mockAnalysis: ValueAnalysis = {
  projection: 28.3,
  confidence: 'High',
  expectedValue: 2.8,
  recommendation: 'BET',
  valueRating: 'Positive EV'
}

export function ValueFinderResults() {
  const [analysis, setAnalysis] = useState<ValueAnalysis | null>(mockAnalysis)
  const [isVisible, setIsVisible] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    // Show results after a short delay for better UX
    const timer = setTimeout(() => setIsVisible(true), 300)
    return () => clearTimeout(timer)
  }, [])

  const handleBetAction = (recommendation: string) => {
    toast({
      title: recommendation === 'BET' ? "Bet Placed" : "Bet Skipped",
      description: `${recommendation === 'BET' ? 'Successfully placed bet on' : 'Skipped betting on'} LeBron James Points`,
    })
  }

  if (!analysis) {
    return (
      <Card className="border-muted">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Target className="h-5 w-5" />
            <CardTitle>Analysis Results</CardTitle>
          </div>
          <CardDescription>
            Results will appear here after you analyze a prop bet
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-40 text-muted-foreground">
            <div className="text-center space-y-2">
              <Target className="h-8 w-8 mx-auto opacity-50" />
              <p className="text-sm">No analysis yet</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const confidenceScore = analysis.confidence === 'High' ? 85 : analysis.confidence === 'Medium' ? 65 : 40

  return (
    <Card className={`border-muted transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Target className="h-5 w-5" />
          <CardTitle>Analysis Results</CardTitle>
        </div>
        <CardDescription>
          Model projection and betting recommendation for LeBron James Points
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Model Projection */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Model Projection</span>
            <span className="text-2xl font-bold text-foreground">{analysis.projection}</span>
          </div>
          <div className="text-xs text-muted-foreground">
            Line: 25.5 | Projection: {analysis.projection} | Difference: {(analysis.projection - 25.5).toFixed(1)}
          </div>
        </div>

        {/* Confidence Score */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Confidence Score</span>
            <Badge 
              variant="outline"
              className={`${
                analysis.confidence === 'High' 
                  ? 'border-green-500 text-green-500 bg-green-500/10' 
                  : analysis.confidence === 'Medium'
                  ? 'border-yellow-500 text-yellow-500 bg-yellow-500/10'
                  : 'border-red-500 text-red-500 bg-red-500/10'
              }`}
            >
              {analysis.confidence}
            </Badge>
          </div>
          <Progress 
            value={confidenceScore} 
            className="h-2"
          />
          <div className="text-xs text-muted-foreground">
            Model is {confidenceScore}% confident in this projection
          </div>
        </div>

        {/* Expected Value */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Expected Value</span>
            <div className={`flex items-center space-x-1 text-xl font-bold ${
              analysis.expectedValue > 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {analysis.expectedValue > 0 ? (
                <TrendingUp className="h-5 w-5" />
              ) : (
                <TrendingDown className="h-5 w-5" />
              )}
              <span>{analysis.expectedValue > 0 ? '+' : ''}{analysis.expectedValue}</span>
            </div>
          </div>
          <Badge 
            variant="outline"
            className={`${
              analysis.valueRating === 'Positive EV' 
                ? 'border-green-500 text-green-500 bg-green-500/10' 
                : 'border-red-500 text-red-500 bg-red-500/10'
            }`}
          >
            {analysis.valueRating}
          </Badge>
        </div>

        {/* Recommendation */}
        <div className="p-4 rounded-lg border border-border bg-muted/20">
          <div className="flex items-center space-x-3 mb-2">
            {analysis.recommendation === 'BET' ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
            <span className="font-medium text-foreground">Recommendation</span>
          </div>
          <div className="space-y-2">
            <div className={`text-lg font-bold ${
              analysis.recommendation === 'BET' ? 'text-green-500' : 'text-red-500'
            }`}>
              {analysis.recommendation}
            </div>
            <p className="text-sm text-muted-foreground">
              {analysis.recommendation === 'BET' 
                ? 'This bet shows positive expected value. Consider placing this wager based on our model analysis.'
                : 'This bet shows negative expected value. We recommend avoiding this wager.'}
            </p>
          </div>
        </div>

        {/* Action Button */}
        <Button 
          className={`w-full ${
            analysis.recommendation === 'BET' 
              ? 'bg-green-600 hover:bg-green-700 text-white' 
              : 'bg-red-600 hover:bg-red-700 text-white'
          }`}
          onClick={() => handleBetAction(analysis.recommendation)}
        >
          {analysis.recommendation === 'BET' ? 'Place Bet' : 'Skip This Bet'}
        </Button>
      </CardContent>
    </Card>
  )
}
