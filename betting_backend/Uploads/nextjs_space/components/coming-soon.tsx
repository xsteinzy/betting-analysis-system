
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { LucideIcon } from 'lucide-react'
import { CheckCircle, Clock } from 'lucide-react'

interface ComingSoonProps {
  icon: LucideIcon
  title: string
  description: string
  features: string[]
}

export function ComingSoon({ icon: Icon, title, description, features }: ComingSoonProps) {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="p-4 rounded-full bg-primary/10 border border-primary/20">
              <Icon className="h-12 w-12 text-primary" />
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center justify-center space-x-2">
              <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
              <Badge variant="secondary" className="text-xs">
                <Clock className="h-3 w-3 mr-1" />
                Coming Soon
              </Badge>
            </div>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {description}
            </p>
          </div>
        </div>

        <Card className="border-muted">
          <CardHeader>
            <CardTitle className="text-xl">Planned Features</CardTitle>
            <CardDescription>
              Here's what we're building for you in this section
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 border border-muted">
                  <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                  <span className="text-sm text-foreground">{feature}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-muted bg-gradient-to-r from-primary/5 to-secondary/5">
          <CardContent className="p-8 text-center">
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Want to be notified when it's ready?</h3>
              <p className="text-muted-foreground">
                We're working hard to bring you these features. Check back soon for updates!
              </p>
              <div className="flex justify-center">
                <Badge variant="outline" className="text-xs px-4 py-2">
                  <Clock className="h-3 w-3 mr-1" />
                  In Development
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
