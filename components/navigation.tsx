"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { ImageIcon, VideoIcon, AudioLines, Shield } from "lucide-react"

export function Navigation() {
  const pathname = usePathname()

  const links = [
    {
      href: "/",
      label: "Dashboard",
      icon: Shield,
    },
    {
      href: "/detect/image",
      label: "Image",
      icon: ImageIcon,
    },
    {
      href: "/detect/video",
      label: "Video",
      icon: VideoIcon,
    },
    {
      href: "/detect/audio",
      label: "Audio",
      icon: AudioLines,
    },
  ]

  return (
    <nav className="border-b border-border bg-card/80 backdrop-blur-md relative">
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <Shield className="h-7 w-7 text-primary transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                KYROS
              </span>
              <div className="text-xs text-muted-foreground -mt-1">Authenticity Verification</div>
            </div>
          </Link>

          <div className="flex items-center gap-1">
            {links.map((link) => {
              const Icon = link.icon
              const isActive = pathname === link.href

              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all relative",
                    isActive
                      ? "bg-primary/10 text-primary border border-primary/20"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50",
                  )}
                >
                  {isActive && <div className="absolute inset-0 bg-primary/5 rounded-lg blur-sm" />}
                  <Icon className="h-4 w-4 relative z-10" />
                  <span className="relative z-10">{link.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
