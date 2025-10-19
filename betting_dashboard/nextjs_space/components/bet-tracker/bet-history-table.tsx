
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { Calendar, Filter, Search, Trophy } from 'lucide-react';
import { BetEntry, DateRange } from '@/lib/types';
import { format, isAfter, isBefore, subDays } from 'date-fns';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';

interface BetHistoryTableProps {
  bets: BetEntry[];
}

export function BetHistoryTable({ bets }: BetHistoryTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSport, setSelectedSport] = useState<string>('all');
  const [selectedEntryType, setSelectedEntryType] = useState<string>('all');
  const [selectedOutcome, setSelectedOutcome] = useState<string>('all');
  const [dateRange, setDateRange] = useState<DateRange>('all');
  const [customStartDate, setCustomStartDate] = useState<Date>();
  const [customEndDate, setCustomEndDate] = useState<Date>();

  const filterBets = () => {
    return bets.filter((bet) => {
      // Search filter
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = !searchTerm || 
        bet.props.some(prop => 
          prop.playerName.toLowerCase().includes(searchLower) ||
          prop.propType.toLowerCase().includes(searchLower)
        );

      // Sport filter
      const matchesSport = selectedSport === 'all' || bet.sport === selectedSport;

      // Entry type filter
      const matchesEntryType = selectedEntryType === 'all' || bet.entryType === selectedEntryType;

      // Outcome filter
      const matchesOutcome = selectedOutcome === 'all' || bet.status === selectedOutcome;

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
        case 'custom':
          if (customStartDate && customEndDate) {
            matchesDateRange = isAfter(betDate, customStartDate) && isBefore(betDate, customEndDate);
          }
          break;
        case 'all':
        default:
          matchesDateRange = true;
      }

      return matchesSearch && matchesSport && matchesEntryType && matchesOutcome && matchesDateRange;
    });
  };

  const filteredBets = filterBets();

  if (bets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Trophy className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Bet History</h3>
        <p className="text-muted-foreground">
          You don't have any completed bets yet. Your betting history will appear here.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search players, props..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>

        <Select value={selectedSport} onValueChange={setSelectedSport}>
          <SelectTrigger>
            <SelectValue placeholder="All Sports" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Sports</SelectItem>
            <SelectItem value="NFL">NFL</SelectItem>
            <SelectItem value="NBA">NBA</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedEntryType} onValueChange={setSelectedEntryType}>
          <SelectTrigger>
            <SelectValue placeholder="All Entry Types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Entry Types</SelectItem>
            <SelectItem value="2-pick">2-Pick</SelectItem>
            <SelectItem value="3-pick">3-Pick</SelectItem>
            <SelectItem value="4-pick">4-Pick</SelectItem>
            <SelectItem value="5-pick">5-Pick</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedOutcome} onValueChange={setSelectedOutcome}>
          <SelectTrigger>
            <SelectValue placeholder="All Outcomes" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Outcomes</SelectItem>
            <SelectItem value="Won">Won</SelectItem>
            <SelectItem value="Lost">Lost</SelectItem>
          </SelectContent>
        </Select>

        <Select value={dateRange} onValueChange={(value: DateRange) => setDateRange(value)}>
          <SelectTrigger>
            <SelectValue placeholder="Date Range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="last7">Last 7 Days</SelectItem>
            <SelectItem value="last30">Last 30 Days</SelectItem>
            <SelectItem value="last90">Last 90 Days</SelectItem>
            <SelectItem value="all">All Time</SelectItem>
            <SelectItem value="custom">Custom Range</SelectItem>
          </SelectContent>
        </Select>

        {dateRange === 'custom' && (
          <div className="flex space-x-2">
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "flex-1 justify-start text-left font-normal",
                    !customStartDate && "text-muted-foreground"
                  )}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {customStartDate ? format(customStartDate, "MMM dd") : "Start"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <CalendarComponent
                  mode="single"
                  selected={customStartDate}
                  onSelect={setCustomStartDate}
                  initialFocus
                />
              </PopoverContent>
            </Popover>

            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "flex-1 justify-start text-left font-normal",
                    !customEndDate && "text-muted-foreground"
                  )}
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  {customEndDate ? format(customEndDate, "MMM dd") : "End"}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="start">
                <CalendarComponent
                  mode="single"
                  selected={customEndDate}
                  onSelect={setCustomEndDate}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filteredBets.length} of {bets.length} bets
        </p>
      </div>

      {filteredBets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Filter className="h-8 w-8 text-muted-foreground mb-2" />
          <p className="text-muted-foreground">No bets match your current filters</p>
        </div>
      ) : (
        <>
          {/* Mobile View */}
          <div className="block md:hidden space-y-4">
            {filteredBets.map((bet) => (
              <Card key={bet.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline">{bet.sport}</Badge>
                      <Badge variant="secondary">{bet.entryType}</Badge>
                      <Badge 
                        variant={bet.status === 'Won' ? 'default' : 'destructive'}
                        className={bet.status === 'Won' ? 'bg-green-500 hover:bg-green-600' : ''}
                      >
                        {bet.status}
                      </Badge>
                    </div>
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Calendar className="h-4 w-4 mr-1" />
                      {format(new Date(bet.date), 'MMM dd')}
                    </div>
                  </div>

                  <div className="space-y-2 mb-4">
                    {bet.props.map((prop, index) => (
                      <div key={prop.id} className="text-sm">
                        <span className="font-medium">{prop.playerName}</span>
                        <span className="text-muted-foreground">
                          {' '}{prop.pick} {prop.line} {prop.propType}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-sm">
                      <div>Stake: ${bet.stake.toFixed(2)}</div>
                      {bet.payout !== undefined && (
                        <div>Payout: ${bet.payout.toFixed(2)}</div>
                      )}
                    </div>
                    <div className={`font-medium ${
                      (bet.profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {(bet.profit || 0) >= 0 ? '+' : ''}${(bet.profit || 0).toFixed(2)}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Desktop View */}
          <div className="hidden md:block">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Sport</TableHead>
                  <TableHead>Entry Type</TableHead>
                  <TableHead>Props</TableHead>
                  <TableHead>Outcome</TableHead>
                  <TableHead>Stake</TableHead>
                  <TableHead>Payout</TableHead>
                  <TableHead>Profit/Loss</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBets.map((bet) => (
                  <TableRow key={bet.id}>
                    <TableCell>{format(new Date(bet.date), 'MMM dd, yyyy')}</TableCell>
                    <TableCell>
                      <Badge variant="outline">{bet.sport}</Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{bet.entryType}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <div className="space-y-1">
                        {bet.props.map((prop, index) => (
                          <div key={prop.id} className="text-sm">
                            <span className="font-medium">{prop.playerName}</span>
                            <span className="text-muted-foreground">
                              {' '}{prop.pick} {prop.line} {prop.propType}
                            </span>
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant={bet.status === 'Won' ? 'default' : 'destructive'}
                        className={bet.status === 'Won' ? 'bg-green-500 hover:bg-green-600' : ''}
                      >
                        {bet.status}
                      </Badge>
                    </TableCell>
                    <TableCell>${bet.stake.toFixed(2)}</TableCell>
                    <TableCell>
                      {bet.payout !== undefined ? `$${bet.payout.toFixed(2)}` : 'N/A'}
                    </TableCell>
                    <TableCell className={`font-medium ${
                      (bet.profit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {(bet.profit || 0) >= 0 ? '+' : ''}${(bet.profit || 0).toFixed(2)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </>
      )}
    </div>
  );
}
