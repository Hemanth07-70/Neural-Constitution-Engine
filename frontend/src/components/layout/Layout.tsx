import { Outlet, Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LayoutDashboard, FileCode2, Network, ShieldCheck, Settings, Box, Activity, BookOpen, Terminal } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { CommandPalette } from '@/components/layout/CommandPalette'
import { useAppStore } from '@/store/useAppStore'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { ChevronsUpDown, LogOut, Settings as SettingsIcon } from 'lucide-react'

const NAV_ITEMS = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/app' },
  { label: 'Constitution Builder', icon: FileCode2, path: '/app/builder' },
  { label: 'Action Simulator', icon: Terminal, path: '/app/simulator' },
  { label: 'Execution Plans', icon: Network, path: '/app/execution' },
  { label: 'Audit Center', icon: ShieldCheck, path: '/app/audit' },
  { label: 'Plugin Registry', icon: Box, path: '/app/plugins' },
  { label: 'AI Providers', icon: Activity, path: '/app/providers' },
  { label: 'Architecture Specs', icon: BookOpen, path: '/app/docs' },
  { label: 'System Health', icon: Activity, path: '/app/health' },
  { label: 'Settings', icon: Settings, path: '/app/settings' },
]

export function Layout() {
  const location = useLocation()
  const { user, activeOrganization, setActiveOrganization, logout } = useAppStore()

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-card flex flex-col hidden md:flex">
        <div className="h-16 flex items-center px-6 border-b border-border">
          <div className="font-bold text-lg tracking-tight flex items-center gap-2">
            <div className="w-6 h-6 bg-primary rounded-md flex items-center justify-center">
              <span className="text-primary-foreground text-xs font-bold">N</span>
            </div>
            NCE Platform
          </div>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors relative",
                  isActive
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                )}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-nav"
                    className="absolute inset-0 bg-secondary rounded-md"
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  />
                )}
                <item.icon className="w-4 h-4 relative z-10" />
                <span className="relative z-10">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <DropdownMenu>
            <DropdownMenuTrigger className="flex items-center gap-3 w-full hover:bg-secondary/50 p-2 rounded-md transition-colors text-left outline-none">
              <Avatar className="h-9 w-9">
                <AvatarFallback>{user?.full_name?.substring(0,2).toUpperCase() || 'U'}</AvatarFallback>
              </Avatar>
              <div className="flex flex-col flex-1 truncate">
                <span className="text-sm font-medium">{user?.full_name || 'User'}</span>
                <span className="text-xs text-muted-foreground truncate">{activeOrganization?.name || 'No Org'}</span>
              </div>
              <ChevronsUpDown className="w-4 h-4 text-muted-foreground ml-auto" />
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="start" side="top">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/app/settings" className="flex w-full cursor-pointer"><SettingsIcon className="w-4 h-4 mr-2"/> Settings</Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={logout} className="text-destructive focus:bg-destructive/10 cursor-pointer">
                <LogOut className="w-4 h-4 mr-2"/> Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 flex items-center justify-between px-8 border-b border-border bg-background/80 backdrop-blur-sm z-10 sticky top-0">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            {/* Breadcrumbs or Command Hint */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-secondary/50 rounded-md border border-border">
              <span className="text-xs font-medium">Search</span>
              <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                <span className="text-xs">⌘</span>K
              </kbd>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {user?.organizations && user.organizations.length > 1 && (
              <DropdownMenu>
                <DropdownMenuTrigger className="flex items-center gap-2 text-sm font-medium px-3 py-1.5 border border-border rounded-md hover:bg-secondary/50 outline-none transition-colors">
                  <Box className="w-4 h-4" />
                  {activeOrganization?.name}
                  <ChevronsUpDown className="w-3 h-3 text-muted-foreground" />
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>Organizations</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  {user.organizations.map((org) => (
                    <DropdownMenuItem
                      key={org.id}
                      onClick={() => setActiveOrganization(org.id)}
                      className={org.id === activeOrganization?.id ? 'bg-secondary/50 font-medium' : ''}
                    >
                      {org.name}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            <ThemeToggle />
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8 relative">
          <Outlet />
        </div>
      </main>

      <CommandPalette />
    </div>
  )
}
