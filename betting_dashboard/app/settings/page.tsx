
import { SettingsForm } from '@/components/settings/settings-form'

export default function SettingsPage() {
  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your preferences, bankroll, and account settings
        </p>
      </div>

      <div className="max-w-2xl">
        <SettingsForm />
      </div>
    </div>
  )
}
