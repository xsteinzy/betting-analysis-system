
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Wallet, 
  DollarSign, 
  AlertTriangle, 
  TrendingUp, 
  PieChart as PieChartIcon,
  Calculator
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { BetEntry, BankrollAnalysis } from '@/lib/types';
import { getBets, getActiveBets, getTotalAtRisk, calculateKellySize, calculatePerformanceMetrics } from '@/lib/bet-data';
import { getSettings } from '@/lib/settings';

const COLORS = ['#60B5FF', '#FF9149', '#FF9898', '#FF90BB'];

export default function BankrollPage() {
  const [analysis, setAnalysis] = useState<BankrollAnalysis | null>(null);
  const [activeBets, setActiveBets] = useState<BetEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadBankrollData = () => {
      const settings = getSettings();
      const allBets = getBets();
      const activeEntries = getActiveBets();
      const completedBets = allBets.filter(bet => bet.status !== 'Pending');
      
      const totalAtRisk = getTotalAtRisk();
      const availableBankroll = settings.bankroll - totalAtRisk;
      const exposurePercentage = settings.bankroll > 0 ? (totalAtRisk / settings.bankroll) * 100 : 0;

      // Calculate Kelly Criterion recommendation
      let kellySize = 0;
      let actualWinRate = 52; // Default conservative estimate

      if (completedBets.length >= 20) {
        const metrics = calculatePerformanceMetrics();
        actualWinRate = metrics.winRate;
      }

      // Assume average odds of 2.0 (even money) for Kelly calculation
      const avgOdds = 2.0;
      kellySize = calculateKellySize(actualWinRate, avgOdds);

      // Apply risk tolerance multiplier
      let kellyMultiplier = 0.5; // Moderate default
      switch (settings.riskTolerance) {
        case 'Conservative':
          kellyMultiplier = 0.25;
          break;
        case 'Moderate':
          kellyMultiplier = 0.5;
          break;
        case 'Aggressive':
          kellyMultiplier = 1.0;
          break;
      }

      const recommendedBetSize = (settings.bankroll * kellySize * kellyMultiplier) || (settings.bankroll * 0.02);

      const analysisData: BankrollAnalysis = {
        currentBankroll: settings.bankroll,
        totalAtRisk,
        availableBankroll: Math.max(0, availableBankroll),
        exposurePercentage,
        recommendedBetSize: Math.max(10, Math.min(recommendedBetSize, settings.bankroll * 0.1)),
        kellyCriterion: kellySize
      };

      setAnalysis(analysisData);
      setActiveBets(activeEntries);
      setLoading(false);
    };

    loadBankrollData();
    
    // Listen for storage changes
    const handleStorageChange = () => loadBankrollData();
    window.addEventListener('storage', handleStorageChange);
    
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  if (loading || !analysis) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="animate-pulse">
            <div className="h-8 bg-muted rounded mb-4 w-64"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-32 bg-muted rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Data for sport allocation chart
  const sportAllocation = activeBets.reduce((acc, bet) => {
    const existing = acc.find(item => item.sport === bet.sport);
    if (existing) {
      existing.amount += bet.stake;
      existing.count += 1;
    } else {
      acc.push({
        sport: bet.sport,
        amount: bet.stake,
        count: 1
      });
    }
    return acc;
  }, [] as { sport: string; amount: number; count: number }[]);

  // Data for entry type allocation chart
  const entryTypeAllocation = activeBets.reduce((acc, bet) => {
    const existing = acc.find(item => item.entryType === bet.entryType);
    if (existing) {
      existing.amount += bet.stake;
      existing.count += 1;
    } else {
      acc.push({
        entryType: bet.entryType.replace('-pick', ''),
        amount: bet.stake,
        count: 1
      });
    }
    return acc;
  }, [] as { entryType: string; amount: number; count: number }[]);

  const riskLevel = analysis.exposurePercentage < 25 ? 'Low' : 
                   analysis.exposurePercentage < 50 ? 'Medium' : 'High';
  const riskColor = riskLevel === 'Low' ? 'text-green-500' : 
                    riskLevel === 'Medium' ? 'text-yellow-500' : 'text-red-500';

  const settings = getSettings();
  const completedBets = getBets().filter(bet => bet.status !== 'Pending');

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-foreground">Bankroll Management</h1>
          <p className="text-muted-foreground mt-2">
            Monitor your bankroll, exposure, and optimize your bet sizing strategy
          </p>
        </div>

        {/* Main Bankroll Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Bankroll</CardTitle>
              <Wallet className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${analysis.currentBankroll.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                Total available funds
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Amount at Risk</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">
                ${analysis.totalAtRisk.toFixed(2)}
              </div>
              <p className="text-xs text-muted-foreground">
                {activeBets.length} active bets
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Available Bankroll</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">
                ${analysis.availableBankroll.toFixed(2)}
              </div>
              <p className="text-xs text-muted-foreground">
                Remaining for new bets
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Exposure Analysis */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5" />
              <span>Bankroll Exposure</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Current Exposure</span>
              <div className="flex items-center space-x-2">
                <Badge variant={riskLevel === 'Low' ? 'default' : riskLevel === 'Medium' ? 'secondary' : 'destructive'}>
                  {riskLevel} Risk
                </Badge>
                <span className={`font-bold ${riskColor}`}>
                  {analysis.exposurePercentage.toFixed(1)}%
                </span>
              </div>
            </div>
            
            <Progress value={analysis.exposurePercentage} className="h-2" />
            
            <div className="grid grid-cols-3 gap-4 text-xs text-muted-foreground">
              <div>0% - Safe</div>
              <div className="text-center">25% - 50% Moderate</div>
              <div className="text-right">50%+ - High Risk</div>
            </div>

            <p className="text-sm text-muted-foreground">
              Keep exposure under 25% of bankroll for conservative management, 
              or under 50% for moderate risk tolerance.
            </p>
          </CardContent>
        </Card>

        {/* Recommended Bet Sizing */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calculator className="h-5 w-5" />
              <span>Recommended Bet Sizing</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Kelly Criterion Analysis</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Risk Tolerance:</span>
                    <Badge variant="outline">{settings.riskTolerance}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Sample Size:</span>
                    <span>{completedBets.length} completed bets</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Method:</span>
                    <span>
                      {completedBets.length >= 20 ? 'Actual Win Rate' : 'Conservative 52%'}
                    </span>
                  </div>
                  {analysis.kellyCriterion > 0 && (
                    <div className="flex justify-between">
                      <span>Kelly %:</span>
                      <span>{(analysis.kellyCriterion * 100).toFixed(1)}%</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h4 className="font-semibold mb-2">Recommended Bet Size</h4>
                <div className="text-3xl font-bold text-blue-500 mb-2">
                  ${analysis.recommendedBetSize.toFixed(2)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Based on {settings.riskTolerance.toLowerCase()} risk tolerance
                  {completedBets.length < 20 && ' and conservative estimates'}
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  {((analysis.recommendedBetSize / analysis.currentBankroll) * 100).toFixed(1)}% of current bankroll
                </p>
              </div>
            </div>

            {completedBets.length < 20 && (
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-start space-x-2">
                  <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-yellow-800 dark:text-yellow-200">
                      Limited Data Available
                    </p>
                    <p className="text-yellow-700 dark:text-yellow-300">
                      Complete at least 20 bets for personalized Kelly Criterion calculations based on your actual win rate.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Portfolio Allocation */}
        {activeBets.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {sportAllocation.length > 1 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <PieChartIcon className="h-5 w-5" />
                    <span>Allocation by Sport</span>
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Breakdown of active bets by sport
                  </p>
                </CardHeader>
                <CardContent>
                  <div style={{ width: '100%', height: '250px' }}>
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={sportAllocation}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="amount"
                        >
                          {sportAllocation.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip 
                          content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                              const data = payload[0].payload;
                              return (
                                <div className="bg-background border rounded-lg p-2 shadow-lg">
                                  <p className="font-semibold">{data.sport}</p>
                                  <p className="text-sm">Amount: ${data.amount.toFixed(2)}</p>
                                  <p className="text-sm">Bets: {data.count}</p>
                                </div>
                              );
                            }
                            return null;
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChartIcon className="h-5 w-5" />
                  <span>Allocation by Entry Type</span>
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Risk distribution across bet sizes
                </p>
              </CardHeader>
              <CardContent>
                <div style={{ width: '100%', height: '250px' }}>
                  <ResponsiveContainer>
                    <BarChart data={entryTypeAllocation} margin={{ top: 5, right: 20, bottom: 45, left: 20 }}>
                      <XAxis 
                        dataKey="entryType" 
                        tickLine={false}
                        tick={{ fontSize: 10 }}
                        label={{ 
                          value: 'Entry Type', 
                          position: 'insideBottom', 
                          offset: -15,
                          style: { textAnchor: 'middle', fontSize: 11 }
                        }}
                      />
                      <YAxis 
                        tickLine={false}
                        tick={{ fontSize: 10 }}
                        label={{ 
                          value: 'Amount ($)', 
                          angle: -90, 
                          position: 'insideLeft',
                          style: { textAnchor: 'middle', fontSize: 11 }
                        }}
                      />
                      <Tooltip 
                        content={({ active, payload, label }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="bg-background border rounded-lg p-2 shadow-lg">
                                <p className="font-semibold">{label}-pick</p>
                                <p className="text-sm">Amount: ${data.amount.toFixed(2)}</p>
                                <p className="text-sm">Bets: {data.count}</p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                      <Bar dataKey="amount" fill="#60B5FF" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
