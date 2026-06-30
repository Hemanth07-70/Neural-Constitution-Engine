import { PageWrapper } from '@/components/layout/PageWrapper'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ShieldCheck, ShieldAlert, Activity, GitCommit, Search } from 'lucide-react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from 'recharts'
import { Badge } from '@/components/ui/badge'


import { useAppStore } from '@/store/useAppStore'
import { apiClient } from '@/api/client'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export function Dashboard() {
  const audits = useAppStore(state => state.audits)
  const setAudits = useAppStore(state => state.setAudits)
  const activeOrganization = useAppStore(state => state.activeOrganization)

  useEffect(() => {
    if (activeOrganization) {
      apiClient.get('/audits').then(res => {
        setAudits(res.data)
      }).catch(console.error)
    }
  }, [activeOrganization, setAudits])

  const blocked = audits.filter(a => a.result.action === 'block').length
  const allowed = audits.length - blocked

  // Generate dynamic chart data based on audits
  const generateChartData = () => {
    // Basic mock base since we don't have historical DB data
    const base = [
      { name: '00:00', total: 120, blocked: 10 },
      { name: '04:00', total: 210, blocked: 5 },
      { name: '08:00', total: 800, blocked: 120 },
      { name: '12:00', total: 1200, blocked: 80 },
      { name: '16:00', total: 950, blocked: 45 },
      { name: '20:00', total: 400, blocked: 12 },
    ]

    // Add current session
    base.push({
      name: 'Now',
      total: 180 + audits.length,
      blocked: 8 + blocked
    })

    return base
  }

  const chartData = generateChartData()
  return (
    <PageWrapper>
      <div className="flex flex-col gap-8">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-2">
            Overview of autonomous agent evaluations and policy enforcements.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Total Evaluations</CardTitle>
              <Activity className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{14291 + audits.length}</div>
              <p className="text-xs text-muted-foreground">+20.1% from last month</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Safe Executions</CardTitle>
              <ShieldCheck className="w-4 h-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{13901 + allowed}</div>
              <p className="text-xs text-muted-foreground">High compliance rate</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Blocked Actions</CardTitle>
              <ShieldAlert className="w-4 h-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{390 + blocked}</div>
              <p className="text-xs text-muted-foreground">Violations intercepted</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Active Policies</CardTitle>
              <GitCommit className="w-4 h-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">Across 3 environments</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Evaluation Volume</CardTitle>
              <CardDescription>
                System throughput and blocked anomalies over the last 24 hours.
              </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <div className="h-[300px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorBlocked" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid hsl(var(--border))', backgroundColor: 'hsl(var(--background))' }} />
                    <Area type="monotone" dataKey="total" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#colorTotal)" />
                    <Area type="monotone" dataKey="blocked" stroke="hsl(var(--destructive))" fillOpacity={1} fill="url(#colorBlocked)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Recent Intercepts</CardTitle>
              <CardDescription>
                Actions blocked by the Engine in real-time.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {audits.length === 0 ? (
                  <div className="text-sm text-muted-foreground text-center py-8">
                    <Search className="w-8 h-8 mx-auto mb-3 opacity-20" />
                    No recent intercepts in this session.
                  </div>
                ) : (
                  audits.slice(0, 5).map((audit) => (
                    <div key={audit.id} className="flex items-center">
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center mr-4 ${
                        audit.result.action === 'block' ? 'bg-destructive/10' : 'bg-emerald-500/10'
                      }`}>
                        {audit.result.action === 'block' ? (
                          <ShieldAlert className="w-4 h-4 text-destructive" />
                        ) : (
                          <ShieldCheck className="w-4 h-4 text-emerald-500" />
                        )}
                      </div>
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-medium leading-none truncate max-w-[180px]">
                          {audit.result.determining_rule_id || "Implicit Allow"}
                        </p>
                        <p className="text-sm text-muted-foreground">{audit.request.actor.id}</p>
                      </div>
                      <div className="ml-auto font-medium">
                        {audit.result.action === 'block' ? (
                          <Badge variant="destructive" className="ml-auto">BLOCKED</Badge>
                        ) : (
                          <Badge variant="secondary" className="ml-auto bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20">ALLOWED</Badge>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageWrapper>
  )
}
