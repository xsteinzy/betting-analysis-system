
'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { 
  BarChart3, 
  TrendingUp, 
  Search, 
  BookOpen, 
  PieChart, 
  Settings,
  Menu,
  X,
  Gamepad2,
  Wallet,
  TestTube
} from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from '@/components/ui/badge'
import { Sport } from '@/lib/types'

const navigation = [
  { name: 'Home', href: '/', icon: BarChart3 },
  { name: 'Projections', href: '/projections', icon: TrendingUp },
  { name: 'Value Finder', href: '/value-finder', icon: Search },
  { name: 'Bet Tracker', href: '/bet-tracker', icon: BookOpen },
  { name: 'Analytics', href: '/analytics', icon: PieChart },
  { name: 'Bankroll', href: '/bankroll', icon: Wallet },
  { name: 'Backtesting', href: '/backtesting', icon: TestTube },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [selectedSport, setSelectedSport] = useState<Sport>('Both')
  const pathname = usePathname()

  return (
    <nav className="fixed top-0 w-full z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary">
                <Gamepad2 className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="font-bold text-xl text-foreground">BetAnalytics</span>
            </Link>
            
            <div className="hidden lg:ml-10 lg:flex lg:space-x-1">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </div>

          <div className="hidden lg:flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-muted-foreground">Sport:</span>
              <Select value={selectedSport} onValueChange={(value: Sport) => setSelectedSport(value)}>
                <SelectTrigger className="w-24">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Both">Both</SelectItem>
                  <SelectItem value="NFL">NFL</SelectItem>
                  <SelectItem value="NBA">NBA</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Badge variant="outline" className="text-xs">
              Live Data
            </Badge>
          </div>

          <div className="lg:hidden">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2"
            >
              {mobileMenuOpen ? (
                <X className="h-6 w-6" />
              ) : (
                <Menu className="h-6 w-6" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-background border-b border-border max-h-96 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-md text-base font-medium',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  )}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              )
            })}
            
            <div className="px-3 py-2">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-muted-foreground">Sport:</span>
                <Select value={selectedSport} onValueChange={(value: Sport) => setSelectedSport(value)}>
                  <SelectTrigger className="w-24">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Both">Both</SelectItem>
                    <SelectItem value="NFL">NFL</SelectItem>
                    <SelectItem value="NBA">NBA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  )
}
