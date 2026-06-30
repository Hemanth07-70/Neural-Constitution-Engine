import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ArrowRight, ShieldCheck, Zap, Lock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PageWrapper } from '@/components/layout/PageWrapper'

export function LandingPage() {
  return (
    <PageWrapper className="min-h-screen bg-background relative overflow-hidden flex flex-col">
      {/* Background Gradients */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[40%] -right-[10%] w-[70%] h-[70%] rounded-full bg-primary/20 blur-[120px]" />
        <div className="absolute -bottom-[20%] -left-[10%] w-[60%] h-[60%] rounded-full bg-blue-500/10 blur-[120px]" />
      </div>

      {/* Header */}
      <header className="h-20 flex items-center justify-between px-8 z-10">
        <div className="font-bold text-xl flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-md flex items-center justify-center">
            <span className="text-primary-foreground text-sm font-bold">N</span>
          </div>
          NCE
        </div>
        <div className="flex items-center gap-4">
          <Link to="/docs" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Documentation
          </Link>
          <Button asChild variant="ghost">
            <Link to="/login">Sign In</Link>
          </Button>
          <Button asChild>
            <Link to="/app">Dashboard</Link>
          </Button>
        </div>
      </header>

      {/* Hero */}
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 z-10 mt-[-4rem]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/50 border border-border text-sm mb-8"
        >
          <span className="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
          Neural Constitution Engine v1.0 is now live
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-5xl md:text-7xl font-extrabold tracking-tight max-w-4xl bg-clip-text text-transparent bg-gradient-to-br from-foreground to-foreground/60"
        >
          Govern Autonomous AI with Absolute Certainty.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl"
        >
          Define declarative policies, validate execution graphs, and ensure
          your AI agents never take a destructive action again.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-10 flex items-center gap-4"
        >
          <Button asChild size="lg" className="h-12 px-8 text-base group">
            <Link to="/app">
              Start Building
              <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="h-12 px-8 text-base">
            <Link to="/docs">View Architecture</Link>
          </Button>
        </motion.div>

        {/* Feature Grid */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-24 max-w-5xl w-full"
        >
          <div className="glass-panel p-6 rounded-xl flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Microsecond Latency</h3>
            <p className="text-sm text-muted-foreground">
              Pure-Python execution engine evaluating policies in under 10µs.
            </p>
          </div>
          <div className="glass-panel p-6 rounded-xl flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <ShieldCheck className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Deterministic DAGs</h3>
            <p className="text-sm text-muted-foreground">
              Built-in topological validation guarantees safe execution order.
            </p>
          </div>
          <div className="glass-panel p-6 rounded-xl flex flex-col items-center text-center">
            <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <Lock className="w-6 h-6 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Zero RCE Risk</h3>
            <p className="text-sm text-muted-foreground">
              Custom AST parser ensures policies cannot execute malicious code.
            </p>
          </div>
        </motion.div>
      </main>
    </PageWrapper>
  )
}
