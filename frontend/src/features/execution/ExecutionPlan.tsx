import { useCallback, useState } from 'react'
import { PageWrapper } from '@/components/layout/PageWrapper'
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Node,
  Edge
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { CheckCircle2, AlertCircle, Play, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useEvaluatePlan } from '@/hooks/use-api'
import { useAppStore } from '@/store/useAppStore'
import { useToast } from '@/hooks/use-toast'
import { ExecutionPlan as ExecutionPlanType } from '@/api/types'
import Editor from '@monaco-editor/react'
import { useTheme } from '@/components/theme-provider'
import dagre from 'dagre'

const DEFAULT_JSON = `{
  "id": "custom-agent-plan",
  "nodes": [
    { "id": "1", "action": { "type": "build", "params": { "image": "frontend:v2" } } },
    { "id": "2", "action": { "type": "test", "params": { "suite": "unit" } } },
    { "id": "3", "action": { "type": "scan", "params": { "tool": "trivy" } } },
    { "id": "4", "action": { "type": "deploy", "params": { "env": "production" } } }
  ],
  "edges": [
    { "source": "1", "target": "2" },
    { "source": "1", "target": "3" },
    { "source": "2", "target": "4" },
    { "source": "3", "target": "4" }
  ]
}`

const dagreGraph = new dagre.graphlib.Graph()
dagreGraph.setDefaultEdgeLabel(() => ({}))

const nodeWidth = 150
const nodeHeight = 60

const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const isHorizontal = direction === 'LR'
  dagreGraph.setGraph({ rankdir: direction })

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    const newNode = {
      ...node,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    }
    return newNode
  })

  return { nodes: newNodes, edges }
}

function parsePlanToReactFlow(plan: ExecutionPlanType): { initialNodes: Node[], initialEdges: Edge[] } {
  const rfNodes: Node[] = plan.nodes.map(n => ({
    id: n.id,
    type: 'default',
    data: { label: <div className="font-semibold text-sm capitalize">{n.action?.type || n.id}</div> },
    position: { x: 0, y: 0 },
    className: 'bg-card border-border shadow-sm rounded-lg py-2 px-4 w-32'
  }))

  const rfEdges: Edge[] = plan.edges.map(e => ({
    id: `e${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    animated: false,
    markerEnd: { type: MarkerType.ArrowClosed, color: 'hsl(var(--muted-foreground))' },
    style: { stroke: 'hsl(var(--muted-foreground))' }
  }))

  const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(rfNodes, rfEdges)

  return { initialNodes: layoutedNodes, initialEdges: layoutedEdges }
}

export function ExecutionPlan() {
  const { customPlanJson, setCustomPlanJson, addPlanResult, addAudit } = useAppStore()
  const [jsonInput, setJsonInput] = useState(customPlanJson || DEFAULT_JSON)

  // Keep local state synced to store when it changes
  const handleJsonChange = (value: string | undefined) => {
    const val = value || ''
    setJsonInput(val)
    setCustomPlanJson(val)
  }

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const { mutate: evaluatePlan, isPending } = useEvaluatePlan()
  const { toast } = useToast()
  const { theme } = useTheme()

  const handleGenerateAndEvaluate = () => {
    let plan: ExecutionPlanType
    try {
      plan = JSON.parse(jsonInput) as ExecutionPlanType
    } catch (e) {
      toast({
        title: "Invalid JSON",
        description: "Please check your plan syntax.",
        variant: "destructive"
      })
      return
    }

    const { initialNodes, initialEdges } = parsePlanToReactFlow(plan)

    // Set nodes to pending state visually before execution
    setNodes(initialNodes)
    setEdges(initialEdges)

    evaluatePlan(plan, {
      onSuccess: (result) => {
        addPlanResult(result)

        if (result.node_results) {
          Object.values(result.node_results).forEach(audit => {
            addAudit(audit)
          })
        }

        setNodes((nds) => nds.map(node => {
          const audit = result.node_results?.[node.id]
          if (!audit) return node

          const isBlocked = audit.result.action === 'block'
          return {
            ...node,
            data: {
              label: (
                <div className="flex flex-col items-center">
                  <span className="font-semibold text-sm">{node.data.label.props?.children || node.id}</span>
                  {isBlocked ? (
                    <Badge variant="destructive" className="mt-1 text-[10px]"><AlertCircle className="w-3 h-3 mr-1" /> BLOCKED</Badge>
                  ) : (
                    <Badge variant="secondary" className="mt-1 text-[10px] bg-emerald-500/10 text-emerald-500"><CheckCircle2 className="w-3 h-3 mr-1" /> PASS</Badge>
                  )}
                </div>
              )
            },
            className: isBlocked
              ? 'bg-destructive/10 border-destructive shadow-sm rounded-lg py-2 px-4 w-32 ring-2 ring-destructive ring-offset-2 ring-offset-background'
              : 'bg-card border-border shadow-sm rounded-lg py-2 px-4 w-32'
          }
        }))

        setEdges((eds) => eds.map(edge => {
          const targetAudit = result.node_results?.[edge.target]
          const sourceAudit = result.node_results?.[edge.source]

          if (targetAudit?.result.action === 'block' || sourceAudit?.result.action === 'block') {
            return {
              ...edge,
              animated: true,
              style: { stroke: 'hsl(var(--destructive))', strokeWidth: 2 },
              markerEnd: { type: MarkerType.ArrowClosed, color: 'hsl(var(--destructive))' }
            }
          }
          return { ...edge, animated: true }
        }))

        toast({
          title: result.is_valid ? "Plan Validated" : "Plan Blocked",
          description: result.is_valid ? "All nodes passed governance checks." : `Blocked at node: ${result.failed_node_id}`,
          variant: result.is_valid ? "default" : "destructive"
        })
      },
      onError: (err: any) => {
        toast({
          title: "Execution Error",
          description: err.response?.data?.detail || "Failed to evaluate plan.",
          variant: "destructive"
        })
      }
    })
  }

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  )

  return (
    <PageWrapper>
      <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Execution Plan Graph</h2>
            <p className="text-muted-foreground mt-2">
              Dynamically generate and topologically validate AI action DAGs via the FastAPI backend.
            </p>
          </div>
          <Button onClick={handleGenerateAndEvaluate} disabled={isPending}>
            {isPending ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
            Generate & Evaluate
          </Button>
        </div>

        <div className="flex-1 flex gap-4 overflow-hidden">
          {/* Left Pane: Chatbox / JSON Editor */}
          <Card className="w-1/3 flex flex-col overflow-hidden">
            <CardHeader className="py-3 px-4 border-b border-border bg-muted/50">
              <span className="text-xs font-mono text-muted-foreground">Custom Plan Input (JSON)</span>
            </CardHeader>
            <CardContent className="p-0 flex-1 relative">
              <Editor
                height="100%"
                defaultLanguage="json"
                theme={theme === 'dark' ? 'vs-dark' : 'light'}
                value={jsonInput}
                onChange={handleJsonChange}
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

          {/* Right Pane: React Flow DAG */}
          <Card className="w-2/3 flex flex-col overflow-hidden">
            <CardHeader className="py-4 border-b border-border bg-muted/30">
              <CardTitle className="text-sm font-medium">DAG Visualization</CardTitle>
            </CardHeader>
            <CardContent className="p-0 flex-1 relative">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
                colorMode="system"
                className="bg-background"
              >
                <Controls className="bg-card border-border fill-foreground" />
                <MiniMap className="bg-card border-border" maskColor="hsl(var(--muted)/0.5)" />
                <Background gap={12} size={1} color="hsl(var(--muted-foreground)/0.2)" />
              </ReactFlow>
            </CardContent>
          </Card>
        </div>
      </div>
    </PageWrapper>
  )
}
