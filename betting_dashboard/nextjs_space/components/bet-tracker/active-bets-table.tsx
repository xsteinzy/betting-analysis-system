
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent } from '@/components/ui/card';
import { CheckCircle, XCircle, Calendar, Trophy, DollarSign } from 'lucide-react';
import { BetEntry, ENTRY_MULTIPLIERS } from '@/lib/types';
import { updateBetStatus } from '@/lib/bet-data';
import { format } from 'date-fns';
import { toast } from '@/components/ui/use-toast';

interface ActiveBetsTableProps {
  bets: BetEntry[];
  onUpdate: () => void;
}

export function ActiveBetsTable({ bets, onUpdate }: ActiveBetsTableProps) {
  const [updating, setUpdating] = useState<string | null>(null);

  const handleStatusUpdate = async (betId: string, status: 'Won' | 'Lost') => {
    setUpdating(betId);
    try {
      updateBetStatus(betId, status);
      toast({
        title: `Bet ${status}`,
        description: `Bet has been marked as ${status.toLowerCase()}`,
      });
      onUpdate();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update bet status",
        variant: "destructive"
      });
    } finally {
      setUpdating(null);
    }
  };

  if (bets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Trophy className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Active Bets</h3>
        <p className="text-muted-foreground">
          You don't have any active bets. Log a new bet to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Mobile View */}
      <div className="block md:hidden space-y-4">
        {bets.map((bet) => {
          const multiplier = ENTRY_MULTIPLIERS[bet.entryType];
          const potentialPayout = bet.stake * multiplier;
          const potentialProfit = potentialPayout - bet.stake;

          return (
            <Card key={bet.id}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">{bet.sport}</Badge>
                    <Badge variant="secondary">{bet.entryType}</Badge>
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

                <div className="flex items-center justify-between mb-4">
                  <div className="text-sm">
                    <div className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      <span>Stake: ${bet.stake.toFixed(2)}</span>
                    </div>
                    <div className="text-green-600 font-medium">
                      Potential: +${potentialProfit.toFixed(2)}
                    </div>
                  </div>
                </div>

                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    variant="default"
                    className="flex-1"
                    onClick={() => handleStatusUpdate(bet.id, 'Won')}
                    disabled={updating === bet.id}
                  >
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Mark Won
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    className="flex-1"
                    onClick={() => handleStatusUpdate(bet.id, 'Lost')}
                    disabled={updating === bet.id}
                  >
                    <XCircle className="h-4 w-4 mr-1" />
                    Mark Lost
                  </Button>
                </div>
              </CardContent>
            </Card>
          );
        })}
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
              <TableHead>Stake</TableHead>
              <TableHead>Potential Payout</TableHead>
              <TableHead>Potential Profit</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {bets.map((bet) => {
              const multiplier = ENTRY_MULTIPLIERS[bet.entryType];
              const potentialPayout = bet.stake * multiplier;
              const potentialProfit = potentialPayout - bet.stake;

              return (
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
                  <TableCell>${bet.stake.toFixed(2)}</TableCell>
                  <TableCell>${potentialPayout.toFixed(2)}</TableCell>
                  <TableCell className="text-green-600 font-medium">
                    +${potentialProfit.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="default"
                        onClick={() => handleStatusUpdate(bet.id, 'Won')}
                        disabled={updating === bet.id}
                      >
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Won
                      </Button>
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleStatusUpdate(bet.id, 'Lost')}
                        disabled={updating === bet.id}
                      >
                        <XCircle className="h-4 w-4 mr-1" />
                        Lost
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
