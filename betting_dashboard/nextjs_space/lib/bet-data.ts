
import { BetEntry, ENTRY_MULTIPLIERS, PerformanceMetrics } from './types';

const BETS_STORAGE_KEY = 'betting-bets';

export function getBets(): BetEntry[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const stored = localStorage.getItem(BETS_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Error loading bets:', error);
  }
  
  return [];
}

export function saveBets(bets: BetEntry[]): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(BETS_STORAGE_KEY, JSON.stringify(bets));
  } catch (error) {
    console.error('Error saving bets:', error);
  }
}

export function addBet(bet: Omit<BetEntry, 'id' | 'createdAt'>): BetEntry {
  const newBet: BetEntry = {
    ...bet,
    id: crypto.randomUUID(),
    createdAt: new Date().toISOString(),
  };

  const bets = getBets();
  bets.push(newBet);
  saveBets(bets);
  
  return newBet;
}

export function updateBetStatus(betId: string, status: 'Won' | 'Lost'): void {
  const bets = getBets();
  const betIndex = bets.findIndex(bet => bet.id === betId);
  
  if (betIndex === -1) return;
  
  const bet = bets[betIndex];
  bet.status = status;
  bet.resolvedAt = new Date().toISOString();
  
  const multiplier = ENTRY_MULTIPLIERS[bet.entryType];
  
  if (status === 'Won') {
    bet.payout = bet.stake * multiplier;
    bet.profit = bet.payout - bet.stake;
  } else {
    bet.payout = 0;
    bet.profit = -bet.stake;
  }
  
  saveBets(bets);
}

export function getActiveBets(): BetEntry[] {
  return getBets().filter(bet => bet.status === 'Pending');
}

export function getCompletedBets(): BetEntry[] {
  return getBets().filter(bet => bet.status !== 'Pending');
}

export function calculatePerformanceMetrics(): PerformanceMetrics {
  const allBets = getBets();
  const completedBets = getCompletedBets();
  const activeBets = getActiveBets();
  
  const wonBets = completedBets.filter(bet => bet.status === 'Won');
  const totalProfit = completedBets.reduce((sum, bet) => sum + (bet.profit || 0), 0);
  const totalStaked = completedBets.reduce((sum, bet) => sum + bet.stake, 0);
  
  let longestWinStreak = 0;
  let longestLoseStreak = 0;
  let currentWinStreak = 0;
  let currentLoseStreak = 0;
  
  // Calculate streaks
  completedBets
    .sort((a, b) => new Date(a.resolvedAt || a.createdAt).getTime() - new Date(b.resolvedAt || b.createdAt).getTime())
    .forEach(bet => {
      if (bet.status === 'Won') {
        currentWinStreak++;
        currentLoseStreak = 0;
        longestWinStreak = Math.max(longestWinStreak, currentWinStreak);
      } else if (bet.status === 'Lost') {
        currentLoseStreak++;
        currentWinStreak = 0;
        longestLoseStreak = Math.max(longestLoseStreak, currentLoseStreak);
      }
    });

  return {
    totalBets: allBets.length,
    activeBets: activeBets.length,
    winRate: completedBets.length > 0 ? (wonBets.length / completedBets.length) * 100 : 0,
    totalProfit,
    roi: totalStaked > 0 ? (totalProfit / totalStaked) * 100 : 0,
    longestWinStreak,
    longestLoseStreak,
    avgBetSize: completedBets.length > 0 ? totalStaked / completedBets.length : 0,
    totalStaked,
  };
}

export function getTotalAtRisk(): number {
  const activeBets = getActiveBets();
  return activeBets.reduce((sum, bet) => sum + bet.stake, 0);
}

export function calculateKellySize(winRate: number, avgOdds: number): number {
  // Kelly Criterion: f = (bp - q) / b
  // where b = odds-1, p = win probability, q = lose probability
  const b = avgOdds - 1;
  const p = winRate / 100;
  const q = 1 - p;
  
  return Math.max(0, (b * p - q) / b);
}
