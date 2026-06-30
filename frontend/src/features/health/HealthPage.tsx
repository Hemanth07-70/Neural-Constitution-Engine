import { useHealth } from '@/hooks/use-api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Activity, Server, Cpu } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

export function HealthPage() {
  const { data, isLoading, error, isRefetching } = useHealth()

  if (error) {
    return (
      <div className="p-8">
        <h2 className="text-3xl font-bold tracking-tight mb-6">System Health</h2>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Connection Error</AlertTitle>
          <AlertDescription>
            Could not connect to the Neural Constitution Engine backend. Ensure the FastAPI server is running.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="p-8 flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">System Health</h2>
          <p className="text-muted-foreground mt-2">
            Real-time status of the Neural Constitution Engine backend.
          </p>
        </div>
        {isRefetching && <Badge variant="outline" className="animate-pulse">Polling...</Badge>}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Engine Status</CardTitle>
            <Activity className="w-4 h-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-24" /> : (
              <div className="text-2xl font-bold capitalize">{data?.health.status}</div>
            )}
            <p className="text-xs text-muted-foreground mt-1">API is responding</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">Engine Version</CardTitle>
            <Server className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-16" /> : (
              <div className="text-2xl font-bold">v{data?.version.version}</div>
            )}
            <p className="text-xs text-muted-foreground mt-1">Core Engine Build</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">API Schema</CardTitle>
            <Cpu className="w-4 h-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {isLoading ? <Skeleton className="h-8 w-16" /> : (
              <div className="text-2xl font-bold">{data?.version.api_version}</div>
            )}
            <p className="text-xs text-muted-foreground mt-1">Supported DSL Version</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
