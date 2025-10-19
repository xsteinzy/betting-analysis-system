
'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { useTheme } from 'next-themes'
import { getSettings, saveSettings } from '@/lib/settings'
import { Settings } from '@/lib/types'
import { Save, Moon, Sun, DollarSign, TrendingUp } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export function SettingsForm() {
  const [settings, setSettings] = useState<Settings>({
    bankroll: 1000,
    riskTolerance: 'Moderate',
    theme: 'dark'
  })
  const [isSaving, setIsSaving] = useState(false)
  const [mounted, setMounted] = useState(false)
  const { theme, setTheme } = useTheme()
  const { toast } = useToast()

  useEffect(() => {
    setMounted(true)
    const loadedSettings = getSettings()
    setSettings(loadedSettings)
  }, [])

  if (!mounted) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse space-y-6">
          <div className="h-32 bg-muted rounded-lg"></div>
          <div className="h-32 bg-muted rounded-lg"></div>
          <div className="h-32 bg-muted rounded-lg"></div>
          <div className="h-32 bg-muted rounded-lg"></div>
        </div>
      </div>
    )
  }

  const handleSave = async () => {
    setIsSaving(true)
    
    // Save settings to localStorage
    saveSettings(settings)
    
    // Apply theme
    setTheme(settings.theme)
    
    // Simulate save delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    setIsSaving(false)
    toast({
      title: "Settings saved",
      description: "Your preferences have been updated successfully.",
    })
  }

  const handleThemeToggle = (checked: boolean) => {
    const newTheme = checked ? 'dark' : 'light'
    setSettings({ ...settings, theme: newTheme })
    setTheme(newTheme)
  }

  return (
    <div className="space-y-6">
      {/* Theme Settings */}
      <Card className="border-muted">
        <CardHeader>
          <div className="flex items-center space-x-2">
            {theme === 'dark' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            <CardTitle>Appearance</CardTitle>
          </div>
          <CardDescription>
            Customize how the dashboard looks and feels
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label className="text-base">Dark Mode</Label>
              <div className="text-sm text-muted-foreground">
                Toggle between light and dark theme
              </div>
            </div>
            <Switch 
              checked={settings.theme === 'dark'}
              onCheckedChange={handleThemeToggle}
            />
          </div>
        </CardContent>
      </Card>

      {/* Bankroll Settings */}
      <Card className="border-muted">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <CardTitle>Bankroll Management</CardTitle>
          </div>
          <CardDescription>
            Set your bankroll amount for bet sizing calculations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="bankroll">Bankroll Amount ($)</Label>
            <Input
              id="bankroll"
              type="number"
              min="100"
              step="50"
              value={settings.bankroll}
              onChange={(e) => setSettings({...settings, bankroll: parseFloat(e.target.value) || 0})}
              placeholder="1000"
            />
            <div className="text-sm text-muted-foreground">
              This is used to calculate optimal bet sizes based on your risk tolerance
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Tolerance Settings */}
      <Card className="border-muted">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <CardTitle>Risk Management</CardTitle>
          </div>
          <CardDescription>
            Choose your risk tolerance for bet sizing recommendations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Risk Tolerance</Label>
            <Select 
              value={settings.riskTolerance} 
              onValueChange={(value: 'Conservative' | 'Moderate' | 'Aggressive') => 
                setSettings({...settings, riskTolerance: value})
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Conservative">Conservative (1-2% bankroll)</SelectItem>
                <SelectItem value="Moderate">Moderate (2-3% bankroll)</SelectItem>
                <SelectItem value="Aggressive">Aggressive (3-5% bankroll)</SelectItem>
              </SelectContent>
            </Select>
            <div className="text-sm text-muted-foreground">
              {settings.riskTolerance === 'Conservative' && 'Recommended for beginners. Lower risk, steady growth.'}
              {settings.riskTolerance === 'Moderate' && 'Balanced approach. Good for most bettors.'}
              {settings.riskTolerance === 'Aggressive' && 'Higher risk, higher potential returns. For experienced bettors.'}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Current Settings Summary */}
      <Card className="border-muted">
        <CardHeader>
          <CardTitle>Settings Summary</CardTitle>
          <CardDescription>Review your current configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="p-3 rounded-lg bg-muted/30 border border-muted">
              <div className="font-medium text-foreground">Theme</div>
              <div className="text-muted-foreground capitalize">{settings.theme}</div>
            </div>
            <div className="p-3 rounded-lg bg-muted/30 border border-muted">
              <div className="font-medium text-foreground">Bankroll</div>
              <div className="text-muted-foreground">${settings.bankroll?.toLocaleString() || '0'}</div>
            </div>
            <div className="p-3 rounded-lg bg-muted/30 border border-muted">
              <div className="font-medium text-foreground">Risk Level</div>
              <div className="text-muted-foreground">{settings.riskTolerance}</div>
            </div>
          </div>
          
          <Separator />
          
          <Button onClick={handleSave} disabled={isSaving} className="w-full">
            {isSaving ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Saving...</span>
              </div>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
