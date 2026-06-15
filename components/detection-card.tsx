import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { type LucideIcon, ArrowRight } from "lucide-react"

interface DetectionCardProps {
  title: string
  description: string
  icon: LucideIcon
  href: string
  color: string
}

export function DetectionCard({ title, description, icon: Icon, href, color }: DetectionCardProps) {
  return (
    <Card className="bg-card border-border hover:border-primary/50 transition-colors group">
      <CardHeader>
        <div className={`h-12 w-12 rounded-lg ${color} flex items-center justify-center mb-4`}>
          <Icon className="h-6 w-6" />
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-muted-foreground">{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Button asChild className="w-full group-hover:bg-primary group-hover:text-primary-foreground">
          <Link href={href}>
            Start Detection
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  )
}
