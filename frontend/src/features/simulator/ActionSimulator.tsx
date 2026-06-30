import { useState } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import Editor from '@monaco-editor/react'
import { Button } from '@/components/ui/button'
import { Play, RefreshCw } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useTheme } from '@/components/theme-provider'
import { useEvaluate } from '@/hooks/use-api'
import { DecisionRequest } from '@/api/types'

const DEFAULT_JSON = `{
  "api_version": "nce/v1",
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "actor": { "id": "ai-agent-1", "type": "agent" },
  "action": { "type": "db.read", "params": { "query": "SELECT * FROM users" } },
  "context": {
      "constitution_id": "company-core",
      "constitution_version": "1.0",
      "environment": { "name": "production", "timestamp": "2026-06-30T12:00:00Z" },
      "correlation_id": "123e4567-e89b-12d3-a456-426614174001"
  },
  "submitted_at": "2026-06-30T12:00:00Z"
}`

export function ActionSimulator() {
  const [inputCode, setInputCode] = useState(DEFAULT_JSON)
  const [outputCode, setOutputCode] = useState('// Result will appear here...')
  const { toast } = useToast()
  const { theme } = useTheme()
  const { mutate: evaluateAction, isPending } = useEvaluate()

  const handleSimulate = () => {
    try {
      const requestPayload = JSON.parse(inputCode) as DecisionRequest
      setOutputCode('// Simulating...')

      evaluateAction(requestPayload, {
        onSuccess: (data) => {
          setOutputCode(JSON.stringify(data, null, 2))
          toast({
            title: "Evaluation Complete",
            description: `Verdict: ${data.result.action.toUpperCase()}`,
            variant: data.result.action === 'allow' ? 'default' : 'destructive',
          })
        },
        onError: (err: any) => {
          setOutputCode(JSON.stringify(err.response?.data || err.message, null, 2))
          toast({
            title: "Evaluation Error",
            description: "Failed to evaluate the action. Check your payload schema.",
            variant: "destructive",
          })
        }
      })
    } catch (e: any) {
      toast({
        title: "Invalid JSON",
        description: "Please ensure your input is valid JSON.",
        variant: "destructive",
      })
    }
  }

  return (
    <PageWrapper>
      <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Action Simulator</h2>
            <p className="text-muted-foreground mt-2">
              Test raw JSON decision requests directly against the Governance Kernel.
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleSimulate} disabled={isPending}>
              {isPending ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Simulate Action
            </Button>
          </div>
        </div>

        <div className="flex-1 flex gap-4 overflow-hidden">
          {/* Input Pane */}
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border bg-muted/50">
              <span className="text-xs font-mono text-muted-foreground">Request Payload (JSON)</span>
            </CardHeader>
            <CardContent className="p-0 flex-1 relative">
              <Editor
                height="100%"
                defaultLanguage="json"
                theme={theme === 'dark' ? 'vs-dark' : 'light'}
                value={inputCode}
                onChange={(value) => setInputCode(value || '')}
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: 'var(--font-mono), monospace',
                  padding: { top: 16, bottom: 16 },
                  scrollBeyondLastLine: false,
                }}
              />
            </CardContent>
          </Card>

          {/* Output Pane */}
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border bg-muted/50">
              <span className="text-xs font-mono text-muted-foreground">Evaluation Result (JSON)</span>
            </CardHeader>
            <CardContent className="p-0 flex-1 relative">
              <Editor
                height="100%"
                defaultLanguage="json"
                theme={theme === 'dark' ? 'vs-dark' : 'light'}
                value={outputCode}
                options={{
                  readOnly: true,
                  minimap: { enabled: false },
                  fontSize: 14,
                  fontFamily: 'var(--font-mono), monospace',
                  padding: { top: 16, bottom: 16 },
                  scrollBeyondLastLine: false,
                }}
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </PageWrapper>
  )
}
