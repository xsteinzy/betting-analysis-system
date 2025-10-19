
'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Search, Calculator } from 'lucide-react'
import { NFL_PROPS, NBA_PROPS } from '@/lib/types'
import { getValueAnalysis } from '@/lib/mock-data'
import { ValueAnalysis } from '@/lib/types'

interface ValueFinderFormProps {
  onAnalysisComplete?: (analysis: ValueAnalysis) => void
}

export function ValueFinderForm({ onAnalysisComplete }: ValueFinderFormProps) {
  const [formData, setFormData] = useState({
    playerName: '',
    propType: '',
    lineValue: ''
  })
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.playerName || !formData.propType || !formData.lineValue) return

    setIsLoading(true)
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const analysis = getValueAnalysis(
      formData.playerName,
      formData.propType,
      parseFloat(formData.lineValue)
    )
    
    onAnalysisComplete?.(analysis)
    setIsLoading(false)
  }

  return (
    <Card className="border-muted">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Search className="h-5 w-5" />
          <CardTitle>Analyze Bet Value</CardTitle>
        </div>
        <CardDescription>
          Enter player and prop details to get model analysis and recommendations
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Player Name */}
          <div className="space-y-2">
            <Label htmlFor="playerName">Player Name</Label>
            <Input
              id="playerName"
              placeholder="e.g., LeBron James"
              value={formData.playerName}
              onChange={(e) => setFormData({...formData, playerName: e.target.value})}
            />
          </div>

          {/* Prop Type */}
          <div className="space-y-2">
            <Label htmlFor="propType">Prop Type</Label>
            <Select value={formData.propType} onValueChange={(value) => setFormData({...formData, propType: value})}>
              <SelectTrigger>
                <SelectValue placeholder="Select prop type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem disabled value="nfl-header" className="font-semibold text-foreground">NFL Props</SelectItem>
                {NFL_PROPS.map((prop) => (
                  <SelectItem key={prop} value={prop}>{prop}</SelectItem>
                ))}
                <SelectItem disabled value="nba-header" className="font-semibold text-foreground">NBA Props</SelectItem>
                {NBA_PROPS.map((prop) => (
                  <SelectItem key={prop} value={prop}>{prop}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Line Value */}
          <div className="space-y-2">
            <Label htmlFor="lineValue">Line Value</Label>
            <Input
              id="lineValue"
              type="number"
              step="0.1"
              placeholder="e.g., 25.5"
              value={formData.lineValue}
              onChange={(e) => setFormData({...formData, lineValue: e.target.value})}
            />
          </div>

          <Button 
            type="submit" 
            className="w-full" 
            disabled={!formData.playerName || !formData.propType || !formData.lineValue || isLoading}
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Analyzing...</span>
              </div>
            ) : (
              <>
                <Calculator className="h-4 w-4 mr-2" />
                Compare Value
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
