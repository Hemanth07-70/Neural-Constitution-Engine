import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { Toaster } from '@/components/ui/toaster'

import { Layout } from '@/components/layout/Layout'
import { LandingPage } from '@/features/landing/LandingPage'
import { Dashboard } from '@/features/dashboard/Dashboard'
import { ConstitutionBuilder } from '@/features/builder/ConstitutionBuilder'
import { ExecutionPlan } from '@/features/execution/ExecutionPlan'
import { AuditCenter } from '@/features/audit/AuditCenter'
import { SettingsPage } from '@/features/settings/SettingsPage'
import { PluginMarketplace } from '@/features/plugins/PluginMarketplace'
import { AuthPage } from '@/features/auth/AuthPage'
import { HealthPage } from '@/features/health/HealthPage'
import { Providers } from '@/features/providers/Providers'
import { DocsPage } from '@/features/docs/DocsPage'

import { ActionSimulator } from '@/features/simulator/ActionSimulator'

function AnimatedRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/docs" element={<DocsPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/app" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="builder" element={<ConstitutionBuilder />} />
          <Route path="simulator" element={<ActionSimulator />} />
          <Route path="execution" element={<ExecutionPlan />} />
          <Route path="audit" element={<AuditCenter />} />
          <Route path="plugins" element={<PluginMarketplace />} />
          <Route path="providers" element={<Providers />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="health" element={<HealthPage />} />
          <Route path="docs" element={<DocsPage />} />
        </Route>
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return (
    <Router>
      <AnimatedRoutes />
      <Toaster />
    </Router>
  )
}

export default App
