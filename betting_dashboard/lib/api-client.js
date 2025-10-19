
/**
 * API Client for Betting Dashboard
 * Handles all communication with the Flask backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || data.error || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Health check
 */
export async function checkHealth() {
  return fetchAPI('/api/health');
}

/**
 * Get today's predictions
 * @param {Object} params - Query parameters
 * @param {string} params.sport - 'NBA', 'NFL', or 'both'
 * @param {string} params.date - Date in YYYY-MM-DD format
 */
export async function getPredictions(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/api/predictions${queryString ? `?${queryString}` : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get value bets
 * @param {Object} params - Query parameters
 * @param {string} params.sport - 'NBA', 'NFL', or 'both'
 * @param {number} params.min_confidence - Minimum confidence threshold
 * @param {number} params.min_ev - Minimum expected value percentage
 */
export async function getValueBets(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/api/value-bets${queryString ? `?${queryString}` : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get bets
 * @param {Object} params - Query parameters
 * @param {string} params.status - 'pending', 'win', 'loss', 'push', 'cancelled', or 'all'
 * @param {string} params.sport - 'NBA', 'NFL', or 'both'
 * @param {number} params.limit - Number of results
 * @param {number} params.offset - Pagination offset
 */
export async function getBets(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/api/bets${queryString ? `?${queryString}` : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Add a new bet
 * @param {Object} betData - Bet data
 * @param {string} betData.date - Date in YYYY-MM-DD format
 * @param {string} betData.entry_type - Entry type (e.g., '3-pick')
 * @param {Array} betData.props - Array of props
 * @param {number} betData.stake - Stake amount
 * @param {number} betData.odds - Odds multiplier
 * @param {string} betData.notes - Optional notes
 */
export async function addBet(betData) {
  return fetchAPI('/api/bets', {
    method: 'POST',
    body: JSON.stringify(betData),
  });
}

/**
 * Update a bet
 * @param {number} betId - Bet ID
 * @param {Object} updates - Fields to update
 * @param {string} updates.outcome - 'win', 'loss', 'push', or 'cancelled'
 * @param {number} updates.pnl - Profit/loss amount
 * @param {string} updates.notes - Optional notes
 */
export async function updateBet(betId, updates) {
  return fetchAPI(`/api/bets/${betId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
}

/**
 * Delete a bet
 * @param {number} betId - Bet ID
 */
export async function deleteBet(betId) {
  return fetchAPI(`/api/bets/${betId}`, {
    method: 'DELETE',
  });
}

/**
 * Get analytics data
 * @param {Object} params - Query parameters
 * @param {string} params.period - 'week', 'month', 'season', or 'all'
 */
export async function getAnalytics(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  const endpoint = `/api/analytics${queryString ? `?${queryString}` : ''}`;
  return fetchAPI(endpoint);
}

/**
 * Get backtest results
 */
export async function getBacktestResults() {
  return fetchAPI('/api/backtest-results');
}

/**
 * Transform API predictions to dashboard format
 */
export function transformPrediction(apiPrediction) {
  return {
    id: apiPrediction.id,
    sport: apiPrediction.sport,
    playerName: apiPrediction.player_name,
    position: apiPrediction.position,
    team: apiPrediction.team_name,
    teamAbbr: apiPrediction.team_abbr,
    opponent: apiPrediction.is_home ? apiPrediction.away_abbr : apiPrediction.home_abbr,
    propType: apiPrediction.prop_type,
    projection: parseFloat(apiPrediction.projected_value),
    confidence: apiPrediction.confidence >= 80 ? 'High' : apiPrediction.confidence >= 60 ? 'Medium' : 'Low',
    confidenceScore: apiPrediction.confidence,
    expectedValue: apiPrediction.expected_value || (apiPrediction.confidence - 50),
    date: apiPrediction.game_date,
    homeTeam: apiPrediction.home_team,
    awayTeam: apiPrediction.away_team,
    modelVersion: apiPrediction.model_version,
  };
}

/**
 * Transform API bet to dashboard format
 */
export function transformBet(apiBet) {
  return {
    id: apiBet.id,
    date: apiBet.date,
    entryType: apiBet.entry_type,
    props: apiBet.props,
    stake: parseFloat(apiBet.stake),
    odds: apiBet.odds,
    status: apiBet.outcome === 'pending' ? 'Pending' : 
            apiBet.outcome === 'win' ? 'Won' : 
            apiBet.outcome === 'loss' ? 'Lost' : 
            apiBet.outcome === 'push' ? 'Push' : 'Cancelled',
    payout: apiBet.pnl ? parseFloat(apiBet.stake) + parseFloat(apiBet.pnl) : null,
    profit: apiBet.pnl ? parseFloat(apiBet.pnl) : null,
    notes: apiBet.notes,
    createdAt: apiBet.created_at,
    resolvedAt: apiBet.updated_at !== apiBet.created_at ? apiBet.updated_at : null,
  };
}

export default {
  checkHealth,
  getPredictions,
  getValueBets,
  getBets,
  addBet,
  updateBet,
  deleteBet,
  getAnalytics,
  getBacktestResults,
  transformPrediction,
  transformBet,
};
