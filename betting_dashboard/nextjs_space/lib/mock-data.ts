
import { Projection, Bet } from './types';

export const mockProjections: Projection[] = [
  {
    id: '1',
    sport: 'NBA',
    playerName: 'LeBron James',
    propType: 'Points',
    line: 25.5,
    projection: 28.3,
    confidence: 'High',
    expectedValue: 2.8,
    date: '2024-10-11'
  },
  {
    id: '2',
    sport: 'NBA',
    playerName: 'Stephen Curry',
    propType: '3-Pointers Made',
    line: 4.5,
    projection: 5.2,
    confidence: 'Medium',
    expectedValue: 1.7,
    date: '2024-10-11'
  },
  {
    id: '3',
    sport: 'NFL',
    playerName: 'Josh Allen',
    propType: 'Passing Yards',
    line: 275.5,
    projection: 290.8,
    confidence: 'High',
    expectedValue: 3.2,
    date: '2024-10-11'
  },
  {
    id: '4',
    sport: 'NFL',
    playerName: 'Derrick Henry',
    propType: 'Rushing Yards',
    line: 85.5,
    projection: 78.2,
    confidence: 'Medium',
    expectedValue: -1.5,
    date: '2024-10-11'
  },
  {
    id: '5',
    sport: 'NBA',
    playerName: 'Luka Doncic',
    propType: 'Assists',
    line: 8.5,
    projection: 9.8,
    confidence: 'High',
    expectedValue: 2.1,
    date: '2024-10-11'
  },
  {
    id: '6',
    sport: 'NFL',
    playerName: 'Travis Kelce',
    propType: 'Receiving Yards',
    line: 65.5,
    projection: 72.4,
    confidence: 'Medium',
    expectedValue: 1.9,
    date: '2024-10-11'
  }
];

export const mockBets: Bet[] = [
  {
    id: '1',
    playerName: 'LeBron James',
    sport: 'NBA',
    propType: 'Points Over 25.5',
    line: 25.5,
    betAmount: 100,
    result: 'Win',
    actualValue: 31,
    expectedValue: 2.8,
    confidence: 'High',
    date: '2024-10-10'
  },
  {
    id: '2', 
    playerName: 'Josh Allen',
    sport: 'NFL',
    propType: 'Passing Yards Over 275.5',
    line: 275.5,
    betAmount: 150,
    result: 'Pending',
    expectedValue: 3.2,
    confidence: 'High',
    date: '2024-10-11'
  }
];

export function getValueAnalysis(playerName: string, propType: string, line: number) {
  // Mock analysis - in production this would call the actual model
  const mockProjection = line + (Math.random() - 0.5) * 10;
  const expectedValue = mockProjection - line;
  const confidence = Math.abs(expectedValue) > 2 ? 'High' : Math.abs(expectedValue) > 1 ? 'Medium' : 'Low';
  
  return {
    projection: Math.round(mockProjection * 10) / 10,
    confidence: confidence as 'High' | 'Medium' | 'Low',
    expectedValue: Math.round(expectedValue * 10) / 10,
    recommendation: expectedValue > 0 ? 'BET' : 'PASS' as 'BET' | 'PASS',
    valueRating: expectedValue > 0 ? 'Positive EV' : 'Negative EV' as 'Positive EV' | 'Negative EV'
  };
}
