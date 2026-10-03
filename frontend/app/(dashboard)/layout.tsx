'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  LayoutDashboard,
  Brain,
  FileText,
  LineChart,
  History,
  User,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Search,
  Bell,
  Sun,
  Moon,
  Zap,
  X,
  Keyboard,
} from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // Layout UI states
  const [isCollapsed, setIsCollapsed] = React.useState(false);
  const [searchOpen, setSearchOpen] = React.useState(false);
  const [notifOpen, setNotifOpen] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState('');

  React.useEffect(() => {
    setMounted(true);

    // Keyboard shortcut listeners (Ctrl + K)
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navItems = [
    { label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
    { label: 'Practice Studio', icon: Brain, href: '/practice' },
    { label: 'Resume Intelligence', icon: FileText, href: '/resume' },
    { label: 'Performance', icon: LineChart, href: '/performance' },
    { label: 'Journey Logs', icon: History, href: '/journey' },
    { label: 'Profile', icon: User, href: '/profile' },
    { label: 'Settings', icon: Settings, href: '/settings' },
  ];

  const notifications = [
    { id: 1, title: 'Interview Evaluated', desc: 'Your Software Engineer mock score was calculated at 8.7/10.', type: 'success', time: '10m ago' },
    { id: 2, title: 'Resume Analyzed', desc: 'Identified 3 missing skills for senior tracks.', type: 'info', time: '2h ago' },
    { id: 3, title: 'Weekly Streaks Updated', desc: 'Congratulations! You reached a 5-day practice streak.', type: 'streak', time: '1d ago' },
  ];

  return (
    <div className="flex h-screen bg-canvas overflow-hidden text-text-primary transition-colors duration-300">
      
      {/* 1. SIDEBAR */}
      <motion.aside
        animate={{ width: isCollapsed ? 88 : 288 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="hidden md:flex flex-col justify-between h-full bg-sidebar border-r border-border-custom relative select-none shrink-0"
      >
        <div>
          {/* Logo Brand Header */}
          <div className="flex items-center gap-3 h-20 px-6 border-b border-border-custom">
            <div className="h-9 w-9 rounded-xl bg-accent-primary flex items-center justify-center text-white shrink-0">
              <Sparkles className="h-5 w-5" />
            </div>
            {!isCollapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-xl font-bold tracking-tight text-text-primary"
              >
                Inferexa
              </motion.span>
            )}
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all relative group cursor-pointer ${
                    isActive
                      ? 'bg-accent-primary/10 text-accent-primary font-semibold'
                      : 'text-text-secondary hover:text-text-primary hover:bg-surface-secondary'
                  }`}
                >
                  <item.icon className="h-5 w-5 shrink-0" />
                  {!isCollapsed && <span>{item.label}</span>}
                  
                  {/* Tooltip on Collapsed Side */}
                  {isCollapsed && (
                    <div className="absolute left-16 bg-surface-elevated border border-border-custom text-text-primary text-xs font-semibold px-2.5 py-1.5 rounded-lg opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50 shadow-md whitespace-nowrap">
                      {item.label}
                    </div>
                  )}

                  {/* Active Indicator vertical line */}
                  {isActive && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute left-1 top-3 bottom-3 w-1 bg-accent-primary rounded-full"
                    />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer User Section */}
        <div className="p-4 border-t border-border-custom space-y-4 bg-sidebar">
          {/* Streak Status */}
          <div className={`flex items-center gap-3 px-3 py-2 rounded-xl bg-accent-secondary/5 border border-accent-secondary/10 text-accent-secondary text-sm ${isCollapsed ? 'justify-center' : ''}`}>
            <Zap className="h-4.5 w-4.5 shrink-0" />
            {!isCollapsed && (
              <div className="text-left">
                <span className="font-semibold block text-xs">5 Day Streak</span>
                <span className="text-[10px] text-text-muted">Target: 7 Days</span>
              </div>
            )}
          </div>

          {/* User profile capsule */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-10 w-10 rounded-full bg-accent-primary/20 flex items-center justify-center font-bold text-accent-primary">
                S
              </div>
              {!isCollapsed && (
                <div className="text-left">
                  <span className="text-sm font-semibold text-text-primary block leading-tight">Supriya B.</span>
                  <span className="text-[11px] text-text-muted block">DevOps Trainee</span>
                </div>
              )}
            </div>

            {!isCollapsed && (
              <button
                onClick={() => router.push('/')}
                className="p-1.5 text-text-muted hover:text-danger rounded-lg hover:bg-surface-secondary cursor-pointer transition-colors"
                title="Log Out"
              >
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Toggle sidebar drawer size */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="absolute top-1/2 -right-3 h-6 w-6 rounded-full bg-surface-primary border border-border-custom flex items-center justify-center text-text-muted hover:text-text-primary cursor-pointer shadow-sm hover:scale-105 transition-transform"
          >
            {isCollapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
          </button>
        </div>
      </motion.aside>

      {/* 2. MAIN APPLICATION WORKSPACE */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* TOP NAVBAR */}
        <header className="h-20 border-b border-border-custom flex items-center justify-between px-6 bg-surface-primary/40 backdrop-blur-md shrink-0">
          
          {/* Spotlight Search Toggle */}
          <button
            onClick={() => setSearchOpen(true)}
            className="flex items-center gap-3 px-4 py-2.5 rounded-xl bg-surface-secondary hover:bg-surface-elevated border border-border-custom hover:border-border-hover text-sm text-text-muted cursor-pointer transition-all w-72 text-left"
          >
            <Search className="h-4 w-4" />
            <span className="flex-1">Spotlight Search...</span>
            <span className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-surface-primary border border-border-custom text-[10px] font-mono font-medium">
              <Keyboard className="h-3 w-3 mr-0.5" /> K
            </span>
          </button>

          {/* Navbar actions */}
          <div className="flex items-center gap-3.5">
            {mounted && (
              <button
                onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
                className="p-2.5 rounded-xl border border-border-custom hover:bg-surface-secondary text-text-secondary hover:text-text-primary cursor-pointer transition-colors"
              >
                {resolvedTheme === 'dark' ? <Sun className="h-4.5 w-4.5" /> : <Moon className="h-4.5 w-4.5" />}
              </button>
            )}

            <button
              onClick={() => setNotifOpen(true)}
              className="p-2.5 rounded-xl border border-border-custom hover:bg-surface-secondary text-text-secondary hover:text-text-primary relative cursor-pointer transition-colors"
            >
              <Bell className="h-4.5 w-4.5" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-accent-primary" />
            </button>

            <Link href="/profile" className="h-9 w-9 rounded-full bg-accent-primary/20 flex items-center justify-center font-bold text-accent-primary text-sm hover:scale-105 transition-transform">
              S
            </Link>
          </div>
        </header>

        {/* PAGE SCREEN CONTENT */}
        <main className="flex-1 overflow-y-auto p-6 bg-canvas relative">
          {children}
        </main>
      </div>

      {/* 3. SPOTLIGHT DIALOG MODAL */}
      <AnimatePresence>
        {searchOpen && (
          <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 px-4 bg-black/60 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-lg glass-panel rounded-[26px] overflow-hidden shadow-2xl border border-border-hover"
            >
              <div className="flex items-center gap-3 px-4 py-4 border-b border-border-custom bg-surface-primary">
                <Search className="h-5 w-5 text-text-muted" />
                <input
                  type="text"
                  placeholder="Type a command, page, or search query..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 bg-transparent text-text-primary outline-hidden placeholder-text-muted text-base"
                  autoFocus
                />
                <button
                  onClick={() => setSearchOpen(false)}
                  className="p-1 hover:bg-surface-secondary rounded-lg text-text-muted hover:text-text-primary cursor-pointer"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Spotlight categories list */}
              <div className="p-2 max-h-80 overflow-y-auto text-left">
                <span className="px-3 py-1.5 text-[10px] font-bold text-text-muted uppercase block">Navigation Shortcuts</span>
                <div className="space-y-0.5">
                  {navItems.map((item) => (
                    <button
                      key={item.href}
                      onClick={() => {
                        setSearchOpen(false);
                        router.push(item.href);
                      }}
                      className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-surface-secondary text-sm text-text-secondary hover:text-text-primary cursor-pointer transition-colors"
                    >
                      <span className="flex items-center gap-2">
                        <item.icon className="h-4 w-4" /> {item.label}
                      </span>
                      <span className="text-[10px] text-text-muted font-mono">Go to</span>
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* 4. NOTIFICATION DRAWER */}
      <AnimatePresence>
        {notifOpen && (
          <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-xs">
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="w-full max-w-[380px] h-full bg-sidebar border-l border-border-custom p-6 shadow-2xl flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between pb-4 border-b border-border-custom mb-6">
                  <h3 className="text-lg font-bold text-text-primary">Notifications</h3>
                  <button
                    onClick={() => setNotifOpen(false)}
                    className="p-1 hover:bg-surface-secondary rounded-lg text-text-muted hover:text-text-primary cursor-pointer"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>

                <div className="space-y-4 text-left">
                  {notifications.map((n) => (
                    <div key={n.id} className="p-4 rounded-2xl bg-surface-primary border border-border-custom space-y-1 shadow-xs hover:border-border-hover transition-colors">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-semibold text-text-primary">{n.title}</span>
                        <span className="text-[10px] text-text-muted">{n.time}</span>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">{n.desc}</p>
                    </div>
                  ))}
                </div>
              </div>

              <Button variant="secondary" className="w-full mt-4" onClick={() => setNotifOpen(false)}>
                Dismiss All
              </Button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
