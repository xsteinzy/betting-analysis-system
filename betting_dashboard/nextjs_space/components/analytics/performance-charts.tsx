
'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BetEntry } from '@/lib/types';
import { format, parseISO, startOfMonth } from 'date-fns';

interface PerformanceChartsProps {
  bets: BetEntry[];
}

const COLORS = ['#60B5FF', '#FF9149', '#FF9898', '#FF90BB', '#FF6363', '#80D8C3', '#A19AD3', '#72BF78'];

export function PerformanceCharts({ bets }: PerformanceChartsProps) {
  const { 
    cumulativePnLData, 
    winRateByEntryData, 
    winRateByPropData, 
    profitBySportData, 
    monthlyPerformanceData 
  } = useMemo(() => {
    // Cumulative P&L over time
    const sortedBets = [...bets]
      .filter(bet => bet.resolvedAt)
      .sort((a, b) => new Date(a.resolvedAt!).getTime() - new Date(b.resolvedAt!).getTime());
    
    let cumulativeProfit = 0;
    const cumulativePnLData = sortedBets.map((bet, index) => {
      cumulativeProfit += bet.profit || 0;
      return {
        date: format(new Date(bet.resolvedAt!), 'MMM dd'),
        profit: parseFloat(cumulativeProfit.toFixed(2)),
        betNumber: index + 1
      };
    });

    // Win rate by entry size
    const entryTypes = ['2-pick', '3-pick', '4-pick', '5-pick'];
    const winRateByEntryData = entryTypes.map(entryType => {
      const entryBets = bets.filter(bet => bet.entryType === entryType);
      const wins = entryBets.filter(bet => bet.status === 'Won').length;
      const winRate = entryBets.length > 0 ? (wins / entryBets.length) * 100 : 0;
      
      return {
        entryType: entryType.replace('-pick', ''),
        winRate: parseFloat(winRate.toFixed(1)),
        totalBets: entryBets.length,
        wins
      };
    }).filter(data => data.totalBets > 0);

    // Win rate by prop type
    const propTypeStats = new Map();
    bets.forEach(bet => {
      bet.props.forEach(prop => {
        const key = prop.propType;
        if (!propTypeStats.has(key)) {
          propTypeStats.set(key, { total: 0, wins: 0 });
        }
        const stats = propTypeStats.get(key);
        stats.total++;
        if (bet.status === 'Won') stats.wins++;
      });
    });

    const winRateByPropData = Array.from(propTypeStats.entries())
      .map(([propType, stats]) => ({
        propType: propType.length > 12 ? propType.substring(0, 12) + '...' : propType,
        winRate: parseFloat(((stats.wins / stats.total) * 100).toFixed(1)),
        totalBets: stats.total,
        wins: stats.wins
      }))
      .filter(data => data.totalBets >= 3)
      .sort((a, b) => b.winRate - a.winRate)
      .slice(0, 8);

    // Profit by sport
    const nflBets = bets.filter(bet => bet.sport === 'NFL');
    const nbaBets = bets.filter(bet => bet.sport === 'NBA');
    
    const nflProfit = nflBets.reduce((sum, bet) => sum + (bet.profit || 0), 0);
    const nbaProfit = nbaBets.reduce((sum, bet) => sum + (bet.profit || 0), 0);

    const profitBySportData = [
      { sport: 'NFL', profit: parseFloat(nflProfit.toFixed(2)), bets: nflBets.length },
      { sport: 'NBA', profit: parseFloat(nbaProfit.toFixed(2)), bets: nbaBets.length }
    ].filter(data => data.bets > 0);

    // Monthly performance trend
    const monthlyStats = new Map();
    bets.forEach(bet => {
      if (!bet.resolvedAt) return;
      const monthKey = format(startOfMonth(new Date(bet.resolvedAt)), 'yyyy-MM');
      const monthLabel = format(startOfMonth(new Date(bet.resolvedAt)), 'MMM yyyy');
      
      if (!monthlyStats.has(monthKey)) {
        monthlyStats.set(monthKey, {
          month: monthLabel,
          profit: 0,
          bets: 0,
          wins: 0
        });
      }
      
      const stats = monthlyStats.get(monthKey);
      stats.profit += bet.profit || 0;
      stats.bets++;
      if (bet.status === 'Won') stats.wins++;
    });

    const monthlyPerformanceData = Array.from(monthlyStats.values())
      .map(stats => ({
        ...stats,
        profit: parseFloat(stats.profit.toFixed(2)),
        winRate: parseFloat(((stats.wins / stats.bets) * 100).toFixed(1))
      }))
      .sort((a, b) => a.month.localeCompare(b.month));

    return {
      cumulativePnLData,
      winRateByEntryData,
      winRateByPropData,
      profitBySportData,
      monthlyPerformanceData
    };
  }, [bets]);

  if (bets.length === 0) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2, 3, 4].map(i => (
          <Card key={i}>
            <CardHeader>
              <CardTitle className="text-lg">Chart Placeholder</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No data available
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cumulative P&L Chart */}
      {cumulativePnLData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Cumulative P&L Over Time</CardTitle>
            <p className="text-sm text-muted-foreground">
              Your profit/loss progression over {cumulativePnLData.length} completed bets
            </p>
          </CardHeader>
          <CardContent>
            <div style={{ width: '100%', height: '300px' }}>
              <ResponsiveContainer>
                <LineChart data={cumulativePnLData} margin={{ top: 5, right: 20, bottom: 15, left: 20 }}>
                  <XAxis 
                    dataKey="date" 
                    tickLine={false} 
                    tick={{ fontSize: 10 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    tickLine={false}
                    tick={{ fontSize: 10 }}
                    label={{ 
                      value: 'Profit ($)', 
                      angle: -90, 
                      position: 'insideLeft',
                      style: { textAnchor: 'middle', fontSize: 11 }
                    }}
                  />
                  <Tooltip 
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        return (
                          <div className="bg-background border rounded-lg p-2 shadow-lg">
                            <p className="font-semibold">{label}</p>
                            <p className={`text-sm ${(Number(payload[0]?.value) || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              P&L: ${(Number(payload[0]?.value) || 0) >= 0 ? '+' : ''}${Number(payload[0]?.value) || 0}
                            </p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="profit" 
                    stroke="#60B5FF" 
                    strokeWidth={2}
                    dot={{ fill: '#60B5FF', strokeWidth: 0, r: 3 }}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Win Rate by Entry Size */}
        {winRateByEntryData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Win Rate by Entry Size</CardTitle>
              <p className="text-sm text-muted-foreground">
                Performance breakdown by bet complexity
              </p>
            </CardHeader>
            <CardContent>
              <div style={{ width: '100%', height: '280px' }}>
                <ResponsiveContainer>
                  <BarChart data={winRateByEntryData} margin={{ top: 5, right: 20, bottom: 45, left: 20 }}>
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
                        value: 'Win Rate (%)', 
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
                              <p className="text-sm">Win Rate: {payload[0].value}%</p>
                              <p className="text-sm">Wins: {data.wins}/{data.totalBets}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="winRate" fill="#60B5FF" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Profit by Sport */}
        {profitBySportData.length > 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Profit by Sport</CardTitle>
              <p className="text-sm text-muted-foreground">
                Performance comparison between sports
              </p>
            </CardHeader>
            <CardContent>
              <div style={{ width: '100%', height: '280px' }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={profitBySportData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="profit"
                    >
                      {profitBySportData.map((entry, index) => (
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
                              <p className={`text-sm ${data.profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                Profit: ${data.profit >= 0 ? '+' : ''}${data.profit}
                              </p>
                              <p className="text-sm">Bets: {data.bets}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Legend 
                      verticalAlign="top"
                      wrapperStyle={{ fontSize: 11 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Win Rate by Prop Type */}
        {winRateByPropData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Win Rate by Prop Type</CardTitle>
              <p className="text-sm text-muted-foreground">
                Top performing prop categories (min. 3 bets)
              </p>
            </CardHeader>
            <CardContent>
              <div style={{ width: '100%', height: '280px' }}>
                <ResponsiveContainer>
                  <BarChart 
                    data={winRateByPropData} 
                    layout="horizontal"
                    margin={{ top: 5, right: 20, bottom: 15, left: 80 }}
                  >
                    <XAxis 
                      type="number"
                      tickLine={false}
                      tick={{ fontSize: 10 }}
                      label={{ 
                        value: 'Win Rate (%)', 
                        position: 'insideBottom', 
                        offset: -10,
                        style: { textAnchor: 'middle', fontSize: 11 }
                      }}
                    />
                    <YAxis 
                      type="category"
                      dataKey="propType"
                      tickLine={false}
                      tick={{ fontSize: 10 }}
                      width={75}
                    />
                    <Tooltip 
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-background border rounded-lg p-2 shadow-lg">
                              <p className="font-semibold">{label}</p>
                              <p className="text-sm">Win Rate: {payload[0].value}%</p>
                              <p className="text-sm">Record: {data.wins}/{data.totalBets}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Bar dataKey="winRate" fill="#FF9149" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Monthly Performance */}
        {monthlyPerformanceData.length > 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Monthly Performance Trend</CardTitle>
              <p className="text-sm text-muted-foreground">
                Profit/loss by month over time
              </p>
            </CardHeader>
            <CardContent>
              <div style={{ width: '100%', height: '280px' }}>
                <ResponsiveContainer>
                  <LineChart data={monthlyPerformanceData} margin={{ top: 5, right: 20, bottom: 45, left: 20 }}>
                    <XAxis 
                      dataKey="month" 
                      tickLine={false}
                      tick={{ fontSize: 10 }}
                      height={60}
                      label={{ 
                        value: 'Month', 
                        position: 'insideBottom', 
                        offset: -5,
                        style: { textAnchor: 'middle', fontSize: 11 }
                      }}
                    />
                    <YAxis 
                      tickLine={false}
                      tick={{ fontSize: 10 }}
                      label={{ 
                        value: 'Profit ($)', 
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
                              <p className="font-semibold">{label}</p>
                              <p className={`text-sm ${data.profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                Profit: ${data.profit >= 0 ? '+' : ''}${data.profit}
                              </p>
                              <p className="text-sm">Win Rate: {data.winRate}%</p>
                              <p className="text-sm">Bets: {data.bets}</p>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="profit" 
                      stroke="#72BF78" 
                      strokeWidth={2}
                      dot={{ fill: '#72BF78', strokeWidth: 0, r: 3 }}
                      activeDot={{ r: 5 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
