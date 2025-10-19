
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, BookOpen, TrendingUp, Activity, DollarSign } from 'lucide-react';
import { BetEntry, PerformanceMetrics } from '@/lib/types';
import { getBets, calculatePerformanceMetrics } from '@/lib/bet-data';
import { BetForm } from '@/components/bet-tracker/bet-form';
import { ActiveBetsTable } from '@/components/bet-tracker/active-bets-table';
import { BetHistoryTable } from '@/components/bet-tracker/bet-history-table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

export default function BetTrackerPage() {
  const [bets, setBets] = useState<BetEntry[]>([]);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [showForm, setShowForm] = useState(false);

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

  const refreshData = () => {
    const allBets = getBets();
    setBets(allBets);
    setMetrics(calculatePerformanceMetrics());
  };

  const activeBets = bets.filter(bet => bet.status === 'Pending');
  const completedBets = bets.filter(bet => bet.status !== 'Pending');

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Bet Tracker</h1>
            <p className="text-muted-foreground mt-2">
              Track your bets and monitor your betting performance
            </p>
          </div>
          
          <Dialog open={showForm} onOpenChange={setShowForm}>
            <DialogTrigger asChild>
              <Button className="flex items-center space-x-2">
                <Plus className="h-4 w-4" />
                <span>Log New Bet</span>
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Log New Bet</DialogTitle>
              </DialogHeader>
              <BetForm onSubmit={() => {
                setShowForm(false);
                refreshData();
              }} />
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary Stats */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Bets</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.totalBets}</div>
                <p className="text-xs text-muted-foreground">
                  {completedBets.length} completed, {activeBets.length} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Bets</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.activeBets}</div>
                <p className="text-xs text-muted-foreground">
                  Awaiting results
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {completedBets.length > 0 ? `${metrics.winRate.toFixed(1)}%` : 'N/A'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {completedBets.filter(bet => bet.status === 'Won').length} wins / {completedBets.length} bets
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${
                  metrics.totalProfit >= 0 ? 'text-green-500' : 'text-red-500'
                }`}>
                  {metrics.totalProfit >= 0 ? '+' : ''}${metrics.totalProfit.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  ROI: {metrics.roi.toFixed(1)}%
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs for Active Bets and History */}
        <Tabs defaultValue="active" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="active">Active Bets ({activeBets.length})</TabsTrigger>
            <TabsTrigger value="history">Bet History ({completedBets.length})</TabsTrigger>
          </TabsList>
          
          <TabsContent value="active" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Active Bets</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Bets awaiting results
                </p>
              </CardHeader>
              <CardContent>
                <ActiveBetsTable bets={activeBets} onUpdate={refreshData} />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="history" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Bet History</CardTitle>
                <p className="text-sm text-muted-foreground">
                  All completed bets with filters and search
                </p>
              </CardHeader>
              <CardContent>
                <BetHistoryTable bets={completedBets} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
