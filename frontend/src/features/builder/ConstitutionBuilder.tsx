import { useState } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Editor, { useMonaco } from '@monaco-editor/react'
import { Button } from '@/components/ui/button'
import { Save, Play, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useTheme } from '@/components/theme-provider'
import { useValidateConstitution, usePublishConstitution } from '@/hooks/use-api'
import { useAppStore } from '@/store/useAppStore'

const DEFAULT_YAML = `apiVersion: nce/v1
kind: Constitution
metadata:
  id: production-policy
  version: 1.0.0
  scope: global
principles:
  - id: P1
    category: security
    statement: "No critical vulnerabilities allowed."
rules:
  - id: R1
    principle: P1
    condition: "action.type == 'deploy' and action.params.vulns > 0"
    action:
      type: block
`

export function ConstitutionBuilder() {
  const [code, setCode] = useState(DEFAULT_YAML)
  const { toast } = useToast()
  const { theme } = useTheme()
  const { mutate: validateConfig, isPending: isValidating, error: validateError, isError: isValidateError, isSuccess: isValidateSuccess } = useValidateConstitution()
  const { mutate: publishConfig, isPending: isPublishing } = usePublishConstitution()
  const { activeOrganization } = useAppStore()

  const handleSave = () => {
    publishConfig(
      {
        version: "1.0." + Date.now(),
        yaml_content: code,
        organization_id: activeOrganization?.id || "org-default"
      },
      {
        onSuccess: () => {
          toast({
            title: "Constitution Saved",
            description: "Policy updated successfully. It will be active immediately.",
            variant: "default",
          })
        },
        onError: (err: any) => {
          toast({
            title: "Save Failed",
            description: err.response?.data?.detail || "Failed to save constitution.",
            variant: "destructive",
          })
        }
      }
    )
  }

  const handleValidate = () => {
    validateConfig(code, {
      onSuccess: () => {
        toast({
          title: "Validation Passed",
          description: "The constitution syntax and DSL rules are valid.",
          variant: "default",
        })
      },
      onError: (err: any) => {
        toast({
          title: "Validation Failed",
          description: err.response?.data?.detail || "Syntax error or invalid structure.",
          variant: "destructive",
        })
      }
    })
  }

  return (
    <PageWrapper>
      <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Constitution Builder</h2>
            <p className="text-muted-foreground mt-2">
              Author and validate deterministic governance rules.
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleValidate} disabled={isValidating}>
              {isValidating ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
              Validate
            </Button>
            <Button onClick={handleSave} disabled={isPublishing}>
              {isPublishing ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
              Save Changes
            </Button>
          </div>
        </div>

        {isValidateError && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Validation Error</AlertTitle>
            <AlertDescription className="font-mono text-xs mt-2">
              {validateError?.response?.data?.detail || validateError?.message || "Unknown error occurred"}
            </AlertDescription>
          </Alert>
        )}

        {isValidateSuccess && (
          <Alert className="border-emerald-500/50 bg-emerald-500/10 text-emerald-500">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <AlertTitle>Valid Configuration</AlertTitle>
            <AlertDescription>
              Constitution parsed and AST constructed successfully.
            </AlertDescription>
          </Alert>
        )}

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="py-3 px-4 border-b border-border bg-muted/50">
            <div className="flex items-center gap-2">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <span className="text-xs font-mono text-muted-foreground ml-2">constitution.yaml</span>
            </div>
          </CardHeader>
          <CardContent className="p-0 flex-1 relative">
            <Editor
              height="100%"
              defaultLanguage="yaml"
              theme={theme === 'dark' ? 'vs-dark' : 'light'}
              value={code}
              onChange={(value) => setCode(value || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                fontFamily: 'var(--font-mono), monospace',
                padding: { top: 16, bottom: 16 },
                scrollBeyondLastLine: false,
                smoothScrolling: true,
                cursorBlinking: "smooth",
                cursorSmoothCaretAnimation: "on",
              }}
            />
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  )
}
