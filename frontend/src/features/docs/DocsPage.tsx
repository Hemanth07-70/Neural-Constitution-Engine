import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Cpu,
  Layers,
  Zap,
  ArrowRight,
  Lock,
  GitMerge,
  CheckCircle2,
  BookOpen,
  ArrowLeft,
  Terminal,
  Server,
  Network
} from 'lucide-react';

export const DocsPage: React.FC = () => {
  const [activeSection, setActiveSection] = useState('kernel');

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Top Navbar */}
      <header className="h-16 border-b border-neutral-800/80 bg-neutral-900/80 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <Link to="/" className="flex items-center gap-2 text-neutral-300 hover:text-white transition-colors text-sm font-medium">
            <ArrowLeft className="w-4 h-4" /> Back to Home
          </Link>
          <div className="h-4 w-px bg-neutral-800" />
          <div className="flex items-center gap-2 font-bold text-lg text-white">
            <div className="w-7 h-7 bg-gradient-to-tr from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center text-white text-xs font-black shadow-sm">
              NCE
            </div>
            <span>Architecture & Specs</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button asChild variant="outline" size="sm" className="border-neutral-700 text-neutral-200 hover:bg-neutral-800 hover:text-white rounded-xl text-xs">
            <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer" className="flex items-center gap-1.5">
              <Terminal className="w-3.5 h-3.5 text-indigo-400" /> OpenAPI Specs
            </a>
          </Button>
          <Button asChild size="sm" className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs shadow-sm">
            <Link to="/app" className="flex items-center gap-1.5">
              Launch Dashboard <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </Button>
        </div>
      </header>

      {/* Hero Banner */}
      <div className="border-b border-neutral-800/60 bg-gradient-to-b from-indigo-950/30 via-neutral-950 to-neutral-950 px-8 py-12">
        <div className="max-w-6xl mx-auto space-y-4">
          <Badge variant="outline" className="bg-indigo-500/10 text-indigo-300 border-indigo-500/30 text-xs px-3 py-1 rounded-full inline-flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5" /> System Design & Governance Specification
          </Badge>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white">
            System Architecture & Pipeline Blueprint
          </h1>
          <p className="text-neutral-300 max-w-3xl text-base md:text-lg leading-relaxed">
            The Neural Constitution Engine (NCE) enforces deterministic, fail-closed security invariants across multi-agent AI frameworks. Understand how proposals move from HTTP schemas down to the core execution kernel.
          </p>
        </div>
      </div>

      {/* Main Architecture Content */}
      <div className="max-w-6xl mx-auto px-8 py-10 w-full flex-1 space-y-10">
        {/* Navigation Tabs */}
        <Tabs value={activeSection} onValueChange={setActiveSection} className="w-full">
          <TabsList className="bg-neutral-900 border border-neutral-800 p-1.5 rounded-2xl flex flex-wrap h-auto w-full justify-start gap-1">
            <TabsTrigger value="kernel" className="rounded-xl text-xs md:text-sm font-medium py-2.5 px-4 text-neutral-300 hover:text-white hover:bg-neutral-800/80 data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
              <ShieldCheck className="w-4 h-4 mr-2" /> 1. Governance Kernel
            </TabsTrigger>
            <TabsTrigger value="pipeline" className="rounded-xl text-xs md:text-sm font-medium py-2.5 px-4 text-neutral-300 hover:text-white hover:bg-neutral-800/80 data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
              <Cpu className="w-4 h-4 mr-2" /> 2. Evaluation Pipeline
            </TabsTrigger>
            <TabsTrigger value="dag" className="rounded-xl text-xs md:text-sm font-medium py-2.5 px-4 text-neutral-300 hover:text-white hover:bg-neutral-800/80 data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
              <GitMerge className="w-4 h-4 mr-2" /> 3. DAG Execution Planner
            </TabsTrigger>
            <TabsTrigger value="langgraph" className="rounded-xl text-xs md:text-sm font-medium py-2.5 px-4 text-neutral-300 hover:text-white hover:bg-neutral-800/80 data-[state=active]:bg-indigo-600 data-[state=active]:text-white">
              <Network className="w-4 h-4 mr-2" /> 4. LangGraph Integration
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Section 1: Governance Kernel */}
        {activeSection === 'kernel' && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="bg-neutral-900/80 border-neutral-800 backdrop-blur-sm">
                <CardHeader className="pb-2">
                  <Lock className="w-5 h-5 text-indigo-400 mb-2" />
                  <CardTitle className="text-base text-white font-bold">Fail-Closed Guarantee</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-neutral-300 leading-relaxed">
                  If any rule evaluation throws an unhandled exception or encounters ambiguous state, the Engine defaults immediately to <code className="text-rose-400 bg-rose-500/10 px-1 py-0.5 rounded font-mono">BLOCK</code>.
                </CardContent>
              </Card>

              <Card className="bg-neutral-900/80 border-neutral-800 backdrop-blur-sm">
                <CardHeader className="pb-2">
                  <Zap className="w-5 h-5 text-amber-400 mb-2" />
                  <CardTitle className="text-base text-white font-bold">Zero-RCE AST Parser</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-neutral-300 leading-relaxed">
                  Constitution rules are evaluated via custom Abstract Syntax Trees without using unsafe python <code className="text-amber-400 bg-amber-500/10 px-1 py-0.5 rounded font-mono">eval()</code> or dynamic execution.
                </CardContent>
              </Card>

              <Card className="bg-neutral-900/80 border-neutral-800 backdrop-blur-sm">
                <CardHeader className="pb-2">
                  <Layers className="w-5 h-5 text-emerald-400 mb-2" />
                  <CardTitle className="text-base text-white font-bold">Strict Layer Separation</CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-neutral-300 leading-relaxed">
                  The Governance Kernel remains completely oblivious to HTTP, Docker, ORMs, and user database models for mathematical purity.
                </CardContent>
              </Card>
            </div>

            {/* Architectural Flow Diagram Card */}
            <Card className="bg-neutral-900/60 border-neutral-800 p-6 rounded-2xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Server className="w-5 h-5 text-indigo-400" /> Kernel Architecture Stack
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                <div className="bg-neutral-950 border border-neutral-800 p-4 rounded-xl space-y-2">
                  <div className="text-xs font-mono text-indigo-400 uppercase tracking-wider font-semibold">Layer 1</div>
                  <div className="font-bold text-sm text-white">HTTP REST Schema</div>
                  <p className="text-[11px] text-neutral-300">FastAPI, Pydantic, OAuth2 JWT Auth</p>
                </div>
                <div className="bg-neutral-950 border border-neutral-800 p-4 rounded-xl space-y-2">
                  <div className="text-xs font-mono text-purple-400 uppercase tracking-wider font-semibold">Layer 2</div>
                  <div className="font-bold text-sm text-white">Application Service</div>
                  <p className="text-[11px] text-neutral-300">EngineCache, PostgreSQL, Audit Logs</p>
                </div>
                <div className="bg-neutral-950 border border-neutral-800 p-4 rounded-xl space-y-2">
                  <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider font-semibold">Layer 3</div>
                  <div className="font-bold text-sm text-white">SDK Adapter</div>
                  <p className="text-[11px] text-neutral-300">DecisionRequest & AuditRecord Schemas</p>
                </div>
                <div className="bg-neutral-950 border border-indigo-500/40 bg-indigo-950/30 p-4 rounded-xl space-y-2">
                  <div className="text-xs font-mono text-indigo-300 uppercase tracking-wider font-semibold">Layer 4</div>
                  <div className="font-bold text-sm text-white">Governance Kernel</div>
                  <p className="text-[11px] text-indigo-200">Deterministic Engine & Matchers</p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Section 2: Evaluation Pipeline */}
        {activeSection === 'pipeline' && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <Card className="bg-neutral-900/60 border-neutral-800 p-6 rounded-2xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-400" /> 6-Step Decision Evaluation Lifecycle
              </h3>

              <div className="space-y-4">
                {[
                  { step: '1. Ingest & Contextualize', desc: 'Accepts incoming DecisionRequest containing actor identity, action type, parameters, and environment context.' },
                  { step: '2. Normalize Data', desc: 'Converts request parameters into standard JSON-safe AST properties and resolves active Constitution rules.' },
                  { step: '3. Rule Matching', desc: 'Executes rule conditions sequentially against action properties using deterministic comparison operators.' },
                  { step: '4. Precedence Resolution', desc: 'Applies conflict-resolution policies (e.g. Most-Restrictive-Wins, Severity Priority) if multiple rules match.' },
                  { step: '5. Decision Synthesis', desc: 'Produces final verdict action (ALLOW, BLOCK, REWRITE, REQUIRES_APPROVAL) and risk assessment.' },
                  { step: '6. Tamper-Evident Audit Trail', desc: 'Calculates cryptographic SHA-256 hash of decision payload and persists append-only record to PostgreSQL.' },
                ].map((item, index) => (
                  <div key={index} className="flex items-start gap-4 p-4 rounded-xl bg-neutral-950 border border-neutral-800">
                    <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xs shrink-0 mt-0.5">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-bold text-sm text-white mb-1">{item.step}</h4>
                      <p className="text-xs text-neutral-300 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Section 3: DAG Execution Planner */}
        {activeSection === 'dag' && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <Card className="bg-neutral-900/60 border-neutral-800 p-6 rounded-2xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <GitMerge className="w-5 h-5 text-purple-400" /> Execution Plan DAG Validation
              </h3>

              <p className="text-sm text-neutral-200 leading-relaxed">
                Multi-step agent execution plans are parsed into Directed Acyclic Graphs (DAGs). The Engine performs topological sorting to detect execution cycles and evaluate node dependencies before executing any operations.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-neutral-950 p-5 rounded-xl border border-neutral-800 space-y-3">
                  <div className="flex items-center gap-2 text-sm font-bold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" /> Topological Ordering
                  </div>
                  <p className="text-xs text-neutral-300 leading-relaxed">
                    Ensures dependent child nodes (e.g. Code Deployment) cannot execute until parent precondition nodes (e.g. Security Scan) produce an <code className="text-emerald-400 bg-emerald-500/10 px-1 rounded font-mono">ALLOW</code> verdict.
                  </p>
                </div>

                <div className="bg-neutral-950 p-5 rounded-xl border border-neutral-800 space-y-3">
                  <div className="flex items-center gap-2 text-sm font-bold text-purple-400">
                    <ShieldCheck className="w-4 h-4" /> Cycle Detection
                  </div>
                  <p className="text-xs text-neutral-300 leading-relaxed">
                    Kahn algorithm verification rejects recursive looping graphs before execution begins, avoiding infinite token burn or runaway agent loops.
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Section 4: LangGraph Integration */}
        {activeSection === 'langgraph' && (
          <div className="space-y-8 animate-in fade-in duration-300">
            <Card className="bg-neutral-900/60 border-neutral-800 p-6 rounded-2xl space-y-6">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Network className="w-5 h-5 text-indigo-400" /> LangGraph GovernedGraph Integration
              </h3>

              <p className="text-sm text-neutral-200 leading-relaxed">
                The <code className="text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded font-mono">GovernedGraph</code> adapter seamlessly wraps LangGraph <code className="text-white bg-neutral-800 px-1.5 py-0.5 rounded font-mono">StateGraph</code> instances, automatically injecting governance middleware to validate node inputs without altering agent business logic.
              </p>

              <div className="bg-neutral-950 p-4 rounded-xl border border-neutral-800 font-mono text-xs text-neutral-200 overflow-x-auto">
                <div className="text-neutral-400 mb-2"># Python LangGraph Governance Wrapper Example</div>
                <pre className="text-neutral-100">
{`from langgraph.graph import StateGraph
from backend.integrations.langgraph.governed_graph import GovernedGraph
from backend.integrations.langgraph.config import GovernedGraphConfig

# 1. Define standard LangGraph graph
graph = StateGraph(AgentState)
graph.add_node("RunSecurityScan", run_security_scan)

# 2. Wrap with NCE GovernedGraph
config = GovernedGraphConfig(organization_id=org_id, strict_mode=True)
governed = GovernedGraph(graph, eval_service, config)

# 3. Compile governed agent workflow
app = governed.compile()`}
                </pre>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocsPage;
