
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
