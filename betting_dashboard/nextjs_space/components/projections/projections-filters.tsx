
'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Calendar, Filter, Search, X } from 'lucide-react'
import { NFL_PROPS, NBA_PROPS } from '@/lib/types'

export function ProjectionsFilters() {
  const [filters, setFilters] = useState({
    sport: 'all',
    date: 'today',
    propType: 'all',
    confidence: 'all',
    search: ''
  })

  const activeFiltersCount = Object.values(filters).filter(value => value !== 'all' && value !== 'today' && value !== '').length

  const clearFilters = () => {
    setFilters({
      sport: 'all',
      date: 'today', 
      propType: 'all',
      confidence: 'all',
      search: ''
    })
  }

  return (
    <Card className="border-muted">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Filter className="h-5 w-5" />
            <CardTitle>Filters</CardTitle>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount} active
              </Badge>
            )}
          </div>
          {activeFiltersCount > 0 && (
            <Button variant="outline" size="sm" onClick={clearFilters}>
              <X className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Search players..." 
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              className="pl-10"
            />
          </div>

          {/* Sport Filter */}
          <Select value={filters.sport} onValueChange={(value) => setFilters({...filters, sport: value})}>
            <SelectTrigger>
              <SelectValue placeholder="All Sports" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Sports</SelectItem>
              <SelectItem value="NFL">NFL</SelectItem>
              <SelectItem value="NBA">NBA</SelectItem>
            </SelectContent>
          </Select>

          {/* Date Filter */}
          <Select value={filters.date} onValueChange={(value) => setFilters({...filters, date: value})}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="tomorrow">Tomorrow</SelectItem>
              <SelectItem value="week">This Week</SelectItem>
            </SelectContent>
          </Select>

          {/* Prop Type Filter */}
          <Select value={filters.propType} onValueChange={(value) => setFilters({...filters, propType: value})}>
            <SelectTrigger>
              <SelectValue placeholder="All Props" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Props</SelectItem>
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

          {/* Confidence Filter */}
          <Select value={filters.confidence} onValueChange={(value) => setFilters({...filters, confidence: value})}>
            <SelectTrigger>
              <SelectValue placeholder="All Confidence" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Confidence</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="Low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </CardContent>
    </Card>
  )
}
