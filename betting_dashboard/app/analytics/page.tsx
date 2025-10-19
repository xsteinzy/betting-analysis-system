
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  DollarSign, 
  Percent, 
  Calendar,
  Filter,
  Trophy
} from 'lucide-react';
import { BetEntry, DateRange, PerformanceMetrics } from '@/lib/types';
import { getBets, calculatePerformanceMetrics } from '@/lib/bet-data';
import { PerformanceCharts } from '@/components/analytics/performance-charts';
import { format, isAfter, subDays } from 'date-fns';

export default function AnalyticsPage() {
  const [bets, setBets] = useState<BetEntry[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [selectedSport, setSelectedSport] = useState<string>('all');
  const [selectedEntryType, setSelectedEntryType] = useState<string>('all');
  const [dateRange, setDateRange] = useState<DateRange>('all');

  useEffect(() => {
    const loadData = () => {
      const allBets = getBets();
      setBets(allBets);
      setMetrics(calculatePerformanceMetrics());
    };

    loadData();
    
    // Listen for storage changes
    const handleStorageChange = () => loadData();
    window.addEventListener('storage', handleStorageChange);
    
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const filteredBets = bets.filter((bet) => {
    if (bet.status === 'Pending') return false;
    
    // Sport filter
    const matchesSport = selectedSport === 'all' || bet.sport === selectedSport;

    // Entry type filter
    const matchesEntryType = selectedEntryType === 'all' || bet.entryType === selectedEntryType;

    // Date range filter
    const betDate = new Date(bet.resolvedAt || bet.createdAt);
    let matchesDateRange = true;

    switch (dateRange) {
      case 'last7':
        matchesDateRange = isAfter(betDate, subDays(new Date(), 7));
        break;
      case 'last30':
        matchesDateRange = isAfter(betDate, subDays(new Date(), 30));
        break;
      case 'last90':
        matchesDateRange = isAfter(betDate, subDays(new Date(), 90));
        break;
      case 'all':
      default:
        matchesDateRange = true;
    }

    return matchesSport && matchesEntryType && matchesDateRange;
  });

  const completedBets = bets.filter(bet => bet.status !== 'Pending');

  if (completedBets.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Performance Analytics</h1>
            <p className="text-muted-foreground mt-2">
              Analyze your betting performance with detailed metrics and charts
            </p>
          </div>

          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Trophy className="h-16 w-16 text-muted-foreground mb-6" />
            <h3 className="text-xl font-semibold mb-4">No Betting Data Yet</h3>
            <p className="text-muted-foreground mb-6 max-w-md">
              Start logging your bets in the Bet Tracker to see detailed performance analytics, 
              charts, and insights about your betting strategy.
            </p>
            <Badge variant="outline" className="text-sm">
              Complete at least a few bets to unlock analytics
            </Badge>
          </div>
        </div>
      </div>
    );
  }

  const filteredMetrics = {
    totalBets: filteredBets.length,
    activeBets: 0,
    winRate: filteredBets.length > 0 ? (filteredBets.filter(bet => bet.status === 'Won').length / filteredBets.length) * 100 : 0,
    totalProfit: filteredBets.reduce((sum, bet) => sum + (bet.profit || 0), 0),
    roi: filteredBets.reduce((sum, bet) => sum + bet.stake, 0) > 0 ? 
      (filteredBets.reduce((sum, bet) => sum + (bet.profit || 0), 0) / filteredBets.reduce((sum, bet) => sum + bet.stake, 0)) * 100 : 0,
    longestWinStreak: 0,
    longestLoseStreak: 0,
    avgBetSize: filteredBets.length > 0 ? filteredBets.reduce((sum, bet) => sum + bet.stake, 0) / filteredBets.length : 0,
    totalStaked: filteredBets.reduce((sum, bet) => sum + bet.stake, 0),
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Performance Analytics</h1>
            <p className="text-muted-foreground mt-2">
              Deep dive into your betting performance with advanced analytics
            </p>
          </div>
        </div>

        {/* Filters */}
        <Card className="mb-8">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4 mb-4">
              <Filter className="h-5 w-5 text-muted-foreground" />
              <h3 className="font-semibold">Filters</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select value={dateRange} onValueChange={(value: DateRange) => setDateRange(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Date Range" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="last7">Last 7 Days</SelectItem>
                  <SelectItem value="last30">Last 30 Days</SelectItem>
                  <SelectItem value="last90">Last 90 Days</SelectItem>
                  <SelectItem value="all">All Time</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedSport} onValueChange={setSelectedSport}>
                <SelectTrigger>
                  <SelectValue placeholder="Sport" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Sports</SelectItem>
                  <SelectItem value="NFL">NFL</SelectItem>
                  <SelectItem value="NBA">NBA</SelectItem>
                </SelectContent>
              </Select>

              <Select value={selectedEntryType} onValueChange={setSelectedEntryType}>
                <SelectTrigger>
                  <SelectValue placeholder="Entry Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Entry Types</SelectItem>
                  <SelectItem value="2-pick">2-Pick</SelectItem>
                  <SelectItem value="3-pick">3-Pick</SelectItem>
                  <SelectItem value="4-pick">4-Pick</SelectItem>
                  <SelectItem value="5-pick">5-Pick</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Bets Placed</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredMetrics.totalBets}</div>
              <p className="text-xs text-muted-foreground">
                Completed bets in selected period
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Win Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {filteredMetrics.winRate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {filteredBets.filter(bet => bet.status === 'Won').length} wins / {filteredBets.length} bets
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Profit/Loss</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${
                filteredMetrics.totalProfit >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {filteredMetrics.totalProfit >= 0 ? '+' : ''}${filteredMetrics.totalProfit.toFixed(2)}
              </div>
              <p className="text-xs text-muted-foreground">
                Total: ${filteredMetrics.totalStaked.toFixed(2)} staked
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ROI</CardTitle>
              <Percent className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${
                filteredMetrics.roi >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {filteredMetrics.roi >= 0 ? '+' : ''}{filteredMetrics.roi.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Return on investment
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <PerformanceCharts bets={filteredBets} />
      </div>
    </div>
  );
}
