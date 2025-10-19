
export interface Projection {
  id: string;
  sport: 'NFL' | 'NBA';
  playerName: string;
  propType: string;
  line: number;
  projection: number;
  confidence: 'High' | 'Medium' | 'Low';
  expectedValue: number;
  date: string;
}

export interface Bet {
  id: string;
  playerName: string;
  sport: 'NFL' | 'NBA';
  propType: string;
  line: number;
  betAmount: number;
  result?: 'Win' | 'Loss' | 'Push' | 'Pending';
  actualValue?: number;
  expectedValue: number;
  confidence: 'High' | 'Medium' | 'Low';
  date: string;
}

// New comprehensive bet structure
export interface BetProp {
  id: string;
  playerName: string;
  propType: PropType;
  line: number;
  pick: 'Over' | 'Under';
}

export interface BetEntry {
  id: string;
  date: string;
  sport: 'NFL' | 'NBA';
  entryType: '2-pick' | '3-pick' | '4-pick' | '5-pick';
  props: BetProp[];
  stake: number;
  status: 'Pending' | 'Won' | 'Lost';
  payout?: number;
  profit?: number;
  createdAt: string;
  resolvedAt?: string;
}

export interface ValueAnalysis {
  projection: number;
  confidence: 'High' | 'Medium' | 'Low';
  expectedValue: number;
  recommendation: 'BET' | 'PASS';
  valueRating: 'Positive EV' | 'Negative EV';
}

export interface Settings {
  bankroll: number;
  riskTolerance: 'Conservative' | 'Moderate' | 'Aggressive';
  theme: 'light' | 'dark';
}

export interface BankrollAnalysis {
  currentBankroll: number;
  totalAtRisk: number;
  availableBankroll: number;
  exposurePercentage: number;
  recommendedBetSize: number;
  kellyCriterion: number;
}

export interface PerformanceMetrics {
  totalBets: number;
  activeBets: number;
  winRate: number;
  totalProfit: number;
  roi: number;
  longestWinStreak: number;
  longestLoseStreak: number;
  avgBetSize: number;
  totalStaked: number;
}

export type Sport = 'NFL' | 'NBA' | 'Both';

export const NFL_PROPS = [
  'Passing Yards',
  'Rushing Yards', 
  'Receiving Yards',
  'Passing Touchdowns',
  'Rushing Touchdowns',
  'Receiving Touchdowns',
  'Receptions',
  'Interceptions',
  'Completions',
  'Field Goals Made'
] as const;

export const NBA_PROPS = [
  'Points',
  'Rebounds',
  'Assists',
  '3-Pointers Made',
  'Steals',
  'Blocks',
  'Turnovers',
  'Double-Double',
  'Field Goals Made',
  'Free Throws Made'
] as const;

export type NFLProp = typeof NFL_PROPS[number];
export type NBAProp = typeof NBA_PROPS[number];
export type PropType = NFLProp | NBAProp;

export const ENTRY_MULTIPLIERS = {
  '2-pick': 3,
  '3-pick': 6,
  '4-pick': 10,
  '5-pick': 20
} as const;

export type DateRange = 'last7' | 'last30' | 'last90' | 'all' | 'custom';
