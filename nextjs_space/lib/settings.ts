
import { Settings } from './types';

const DEFAULT_SETTINGS: Settings = {
  bankroll: 1000,
  riskTolerance: 'Moderate',
  theme: 'dark'
};

export function getSettings(): Settings {
  if (typeof window === 'undefined') return DEFAULT_SETTINGS;
  
  try {
    const stored = localStorage.getItem('betting-settings');
    if (stored) {
      return { ...DEFAULT_SETTINGS, ...JSON.parse(stored) };
    }
  } catch (error) {
    console.error('Error loading settings:', error);
  }
  
  return DEFAULT_SETTINGS;
}

export function saveSettings(settings: Partial<Settings>) {
  if (typeof window === 'undefined') return;
  
  try {
    const current = getSettings();
    const updated = { ...current, ...settings };
    localStorage.setItem('betting-settings', JSON.stringify(updated));
  } catch (error) {
    console.error('Error saving settings:', error);
  }
}
