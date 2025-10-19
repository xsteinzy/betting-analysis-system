
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Plus, X } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { BetProp, ENTRY_MULTIPLIERS, NBA_PROPS, NFL_PROPS, PropType } from '@/lib/types';
import { addBet } from '@/lib/bet-data';
import { toast } from '@/components/ui/use-toast';

interface BetFormProps {
  onSubmit: () => void;
}

export function BetForm({ onSubmit }: BetFormProps) {
  const [date, setDate] = useState<Date>(new Date());
  const [sport, setSport] = useState<'NFL' | 'NBA' | ''>('');
  const [entryType, setEntryType] = useState<'2-pick' | '3-pick' | '4-pick' | '5-pick' | ''>('');
  const [props, setProps] = useState<BetProp[]>([]);
  const [stake, setStake] = useState('');
  const [status, setStatus] = useState<'Pending' | 'Won' | 'Lost'>('Pending');

  const requiredPropCount = entryType ? parseInt(entryType.charAt(0)) : 0;
  const multiplier = entryType ? ENTRY_MULTIPLIERS[entryType] : 0;
  const potentialPayout = stake ? parseFloat(stake) * multiplier : 0;
  const potentialProfit = potentialPayout ? potentialPayout - parseFloat(stake || '0') : 0;

  const availableProps = sport === 'NBA' ? NBA_PROPS : sport === 'NFL' ? NFL_PROPS : [];

  const addProp = () => {
    if (props.length < 5) {
      setProps([...props, {
        id: crypto.randomUUID(),
        playerName: '',
        propType: availableProps[0] as PropType,
        line: 0,
        pick: 'Over'
      }]);
    }
  };

  const removeProp = (id: string) => {
    setProps(props.filter(prop => prop.id !== id));
  };

  const updateProp = (id: string, field: keyof BetProp, value: any) => {
    setProps(props.map(prop => 
      prop.id === id ? { ...prop, [field]: value } : prop
    ));
  };

  const isValid = () => {
    return (
      date &&
      sport &&
      entryType &&
      props.length === requiredPropCount &&
      props.every(prop => prop.playerName.trim() && prop.line > 0) &&
      stake &&
      parseFloat(stake) > 0 &&
      status
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isValid()) {
      toast({
        title: "Invalid Form",
        description: "Please fill in all required fields",
        variant: "destructive"
      });
      return;
    }

    try {
      addBet({
        date: format(date, 'yyyy-MM-dd'),
        sport: sport as 'NFL' | 'NBA',
        entryType: entryType as '2-pick' | '3-pick' | '4-pick' | '5-pick',
        props,
        stake: parseFloat(stake),
        status,
        ...(status === 'Won' ? { 
          payout: potentialPayout, 
          profit: potentialProfit 
        } : status === 'Lost' ? { 
          payout: 0, 
          profit: -parseFloat(stake) 
        } : {})
      });

      toast({
        title: "Bet Logged",
        description: "Your bet has been successfully logged",
      });

      onSubmit();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to log bet",
        variant: "destructive"
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="date">Date</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !date && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {date ? format(date, "PPP") : "Pick a date"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={date}
                onSelect={(date) => date && setDate(date)}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>

        <div className="space-y-2">
          <Label htmlFor="sport">Sport</Label>
          <Select value={sport} onValueChange={(value: 'NFL' | 'NBA') => {
            setSport(value);
            setProps([]); // Reset props when sport changes
          }}>
            <SelectTrigger>
              <SelectValue placeholder="Select sport" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="NFL">NFL</SelectItem>
              <SelectItem value="NBA">NBA</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="entryType">Entry Type</Label>
          <Select value={entryType} onValueChange={(value: '2-pick' | '3-pick' | '4-pick' | '5-pick') => {
            setEntryType(value);
            const newCount = parseInt(value.charAt(0));
            if (props.length > newCount) {
              setProps(props.slice(0, newCount));
            }
          }}>
            <SelectTrigger>
              <SelectValue placeholder="Select entry type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2-pick">2-Pick (3x payout)</SelectItem>
              <SelectItem value="3-pick">3-Pick (6x payout)</SelectItem>
              <SelectItem value="4-pick">4-Pick (10x payout)</SelectItem>
              <SelectItem value="5-pick">5-Pick (20x payout)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select value={status} onValueChange={(value: 'Pending' | 'Won' | 'Lost') => setStatus(value)}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Pending">Pending</SelectItem>
              <SelectItem value="Won">Won</SelectItem>
              <SelectItem value="Lost">Lost</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Props Section */}
      {sport && entryType && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Props ({props.length}/{requiredPropCount})</CardTitle>
              {props.length < requiredPropCount && (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addProp}
                  className="flex items-center space-x-1"
                >
                  <Plus className="h-4 w-4" />
                  <span>Add Prop</span>
                </Button>
              )}
            </div>
            {props.length !== requiredPropCount && (
              <p className="text-sm text-muted-foreground">
                {entryType} requires exactly {requiredPropCount} props
              </p>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {props.map((prop, index) => (
              <div key={prop.id} className="p-4 border rounded-lg space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant="secondary">Prop {index + 1}</Badge>
                  {props.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeProp(prop.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label>Player Name</Label>
                    <Input
                      placeholder="Player name"
                      value={prop.playerName}
                      onChange={(e) => updateProp(prop.id, 'playerName', e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Prop Type</Label>
                    <Select
                      value={prop.propType}
                      onValueChange={(value) => updateProp(prop.id, 'propType', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {availableProps.map((propType) => (
                          <SelectItem key={propType} value={propType}>
                            {propType}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label>Line Value</Label>
                    <Input
                      type="number"
                      step="0.5"
                      placeholder="0"
                      value={prop.line || ''}
                      onChange={(e) => updateProp(prop.id, 'line', parseFloat(e.target.value) || 0)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Pick</Label>
                    <Select
                      value={prop.pick}
                      onValueChange={(value: 'Over' | 'Under') => updateProp(prop.id, 'pick', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Over">Over</SelectItem>
                        <SelectItem value="Under">Under</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Stake and Payout */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="stake">Stake Amount ($)</Label>
          <Input
            id="stake"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            value={stake}
            onChange={(e) => setStake(e.target.value)}
          />
        </div>

        {entryType && stake && (
          <>
            <div className="space-y-2">
              <Label>Potential Payout</Label>
              <div className="h-10 px-3 py-2 border rounded-md bg-muted flex items-center">
                ${potentialPayout.toFixed(2)}
              </div>
            </div>

            <div className="space-y-2">
              <Label>Potential Profit</Label>
              <div className={`h-10 px-3 py-2 border rounded-md flex items-center font-medium ${
                potentialProfit > 0 ? 'text-green-600 bg-green-50' : 'text-muted-foreground bg-muted'
              }`}>
                +${potentialProfit.toFixed(2)}
              </div>
            </div>
          </>
        )}
      </div>

      <div className="flex justify-end space-x-3">
        <Button type="submit" disabled={!isValid()}>
          Log Bet
        </Button>
      </div>
    </form>
  );
}
