import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Puzzle,
  Zap,
  Search,
  CheckCircle2,
  Download,
  Layers,
  Sparkles,
  Code2
} from 'lucide-react';

interface PluginItem {
  id: string;
  name: string;
  category: 'rules' | 'evaluators' | 'telemetry' | 'hooks';
  version: string;
  author: string;
  description: string;
  capabilities: string[];
  installed: boolean;
  active: boolean;
  downloads: string;
  rating: string;
  badge?: string;
}

const PLUGINS: PluginItem[] = [
  {
    id: 'rego-opa-engine',
    name: 'Rego / OPA Rule Evaluator',
    category: 'rules',
    version: 'v1.4.0',
    author: 'NCE Core Team',
    description: 'Compiles and evaluates governance rules written in Open Policy Agent Rego domain language.',
    capabilities: ['Rego Compiler', 'Fail-Closed Guard', 'Custom Matcher'],
    installed: true,
    active: true,
    downloads: '14.2k',
    rating: '4.9',
    badge: 'Official'
  },
  {
    id: 'langgraph-sync',
    name: 'LangGraph State Synchronizer',
    category: 'hooks',
    version: 'v2.1.0',
    author: 'NCE Core Team',
    description: 'Intercepts state transitions in LangGraph compiled workflows to apply automated governance checks.',
    capabilities: ['State Reducer', 'Middleware Hook', 'Graph Wrapping'],
    installed: true,
    active: true,
    downloads: '28.5k',
    rating: '5.0',
    badge: 'Core'
  },
  {
    id: 'claude-semantic-eval',
    name: 'Claude Semantic Risk Evaluator',
    category: 'evaluators',
    version: 'v0.9.2',
    author: 'Anthropic Labs',
    description: 'Evaluates non-deterministic fuzzy principles using Claude 3.5 Sonnet to produce risk scores.',
    capabilities: ['LLM Scoring', 'Fuzzy Principle Matching', 'Risk Mapping'],
    installed: true,
    active: true,
    downloads: '9.8k',
    rating: '4.8',
    badge: 'Popular'
  },
  {
    id: 'otel-trace-exporter',
    name: 'OpenTelemetry Spans Exporter',
    category: 'telemetry',
    version: 'v1.1.5',
    author: 'CNCF Community',
    description: 'Exports detailed execution pipeline traces and audit spans to Prometheus, Jaeger, or Grafana.',
    capabilities: ['OTel Collector', 'Trace Context Propagation', 'Latency Metrics'],
    installed: true,
    active: true,
    downloads: '18.1k',
    rating: '4.9',
    badge: 'Enterprise'
  },
  {
    id: 'datadog-audit-sync',
    name: 'Datadog Audit Event Streamer',
    category: 'telemetry',
    version: 'v1.0.3',
    author: 'Datadog Integrations',
    description: 'Streams tamper-evident audit records directly to Datadog security monitoring dashboards.',
    capabilities: ['Real-time Streaming', 'Security Alerts', 'Log Normalization'],
    installed: false,
    active: false,
    downloads: '6.4k',
    rating: '4.7'
  },
  {
    id: 'custom-webhook-dispatcher',
    name: 'Webhook Postcondition Dispatcher',
    category: 'hooks',
    version: 'v1.2.0',
    author: 'Community',
    description: 'Triggers arbitrary external HTTP webhooks upon completion of execution plan nodes.',
    capabilities: ['HTTP Webhooks', 'Retry Matrix', 'HMAC Signatures'],
    installed: false,
    active: false,
    downloads: '4.1k',
    rating: '4.6'
  },
  {
    id: 'temporal-workflow-binding',
    name: 'Temporal.io Durable Execution Binding',
    category: 'hooks',
    version: 'v0.8.0',
    author: 'Temporal Orchestrations',
    description: 'Maps NCE execution plans into durable Temporal workflows for distributed state management.',
    capabilities: ['Durable State', 'Activity Scheduling', 'Automatic Retries'],
    installed: false,
    active: false,
    downloads: '3.9k',
    rating: '4.8'
  }
];

export const PluginMarketplace: React.FC = () => {
  const [plugins, setPlugins] = useState<PluginItem[]>(PLUGINS);
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState('all');

  const toggleInstall = (id: string) => {
    setPlugins(prev => prev.map(p => {
      if (p.id === id) {
        const nextInstalled = !p.installed;
        return { ...p, installed: nextInstalled, active: nextInstalled };
      }
      return p;
    }));
  };

  const toggleActive = (id: string) => {
    setPlugins(prev => prev.map(p => {
      if (p.id === id && p.installed) {
        return { ...p, active: !p.active };
      }
      return p;
    }));
  };

  const filteredPlugins = plugins.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
                          p.description.toLowerCase().includes(search.toLowerCase()) ||
                          p.capabilities.some(c => c.toLowerCase().includes(search.toLowerCase()));
    const matchesTab = activeTab === 'all' || p.category === activeTab;
    return matchesSearch && matchesTab;
  });

  const totalInstalled = plugins.filter(p => p.installed).length;
  const totalActive = plugins.filter(p => p.active).length;

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header & Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2.5 bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 rounded-xl">
              <Puzzle className="w-6 h-6 text-indigo-400" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Plugin Registry</h1>
          </div>
          <p className="text-neutral-400 text-sm">Discover, extend, and manage custom governance evaluators and telemetry plugins.</p>
        </div>

        {/* Stats Row */}
        <div className="flex items-center gap-3">
          <div className="bg-neutral-900/80 border border-neutral-800 rounded-xl px-4 py-2 flex items-center gap-3">
            <Layers className="w-4 h-4 text-indigo-400" />
            <div>
              <div className="text-xs text-neutral-400">Installed</div>
              <div className="text-sm font-semibold text-neutral-200">{totalInstalled} / {plugins.length}</div>
            </div>
          </div>
          <div className="bg-neutral-900/80 border border-neutral-800 rounded-xl px-4 py-2 flex items-center gap-3">
            <Zap className="w-4 h-4 text-emerald-400" />
            <div>
              <div className="text-xs text-neutral-400">Active Evaluators</div>
              <div className="text-sm font-semibold text-emerald-400">{totalActive} Active</div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls: Search & Categories */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <Input
            placeholder="Search plugins by name, capability..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-neutral-900/60 border-neutral-800 text-neutral-200 placeholder:text-neutral-500 focus:border-indigo-500 rounded-xl"
          />
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full sm:w-auto">
          <TabsList className="bg-neutral-900 border border-neutral-800 p-1 rounded-xl flex flex-wrap h-auto">
            <TabsTrigger value="all" className="rounded-lg text-xs font-medium data-[state=active]:bg-neutral-800 data-[state=active]:text-white">All</TabsTrigger>
            <TabsTrigger value="rules" className="rounded-lg text-xs font-medium data-[state=active]:bg-neutral-800 data-[state=active]:text-white">Rules & DSL</TabsTrigger>
            <TabsTrigger value="evaluators" className="rounded-lg text-xs font-medium data-[state=active]:bg-neutral-800 data-[state=active]:text-white">AI Evaluators</TabsTrigger>
            <TabsTrigger value="hooks" className="rounded-lg text-xs font-medium data-[state=active]:bg-neutral-800 data-[state=active]:text-white">Hooks & Agents</TabsTrigger>
            <TabsTrigger value="telemetry" className="rounded-lg text-xs font-medium data-[state=active]:bg-neutral-800 data-[state=active]:text-white">Telemetry</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Plugin Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredPlugins.map((plugin) => (
          <Card key={plugin.id} className="bg-neutral-900/50 border-neutral-800/80 backdrop-blur-sm hover:border-neutral-700 transition-all duration-300 flex flex-col justify-between group relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500/0 via-indigo-500/40 to-purple-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />

            <CardHeader className="pb-3">
              <div className="flex justify-between items-start gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-neutral-400 bg-neutral-800/80 px-2 py-0.5 rounded border border-neutral-700/50">
                    {plugin.version}
                  </span>
                  {plugin.badge && (
                    <Badge variant="secondary" className="bg-indigo-500/10 text-indigo-400 border-indigo-500/20 text-xs font-normal">
                      <Sparkles className="w-3 h-3 mr-1" /> {plugin.badge}
                    </Badge>
                  )}
                </div>

                {plugin.installed ? (
                  <Badge variant="default" className={plugin.active ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : "bg-neutral-800 text-neutral-400"}>
                    {plugin.active ? (
                      <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3 text-emerald-400" /> Active</span>
                    ) : (
                      <span>Disabled</span>
                    )}
                  </Badge>
                ) : (
                  <Badge variant="outline" className="text-neutral-500 border-neutral-800">Available</Badge>
                )}
              </div>

              <CardTitle className="text-lg font-bold text-neutral-100 group-hover:text-indigo-400 transition-colors flex items-center justify-between">
                {plugin.name}
              </CardTitle>
              <CardDescription className="text-xs text-neutral-400 font-mono mt-0.5">
                by {plugin.author}
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4 flex-1 flex flex-col justify-between pt-0">
              <p className="text-sm text-neutral-300 line-clamp-2 leading-relaxed">
                {plugin.description}
              </p>

              {/* Capabilities Chips */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-neutral-400 flex items-center gap-1.5">
                  <Code2 className="w-3.5 h-3.5 text-indigo-400" /> Capabilities
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {plugin.capabilities.map((cap) => (
                    <span key={cap} className="text-[11px] bg-neutral-800/60 text-neutral-300 px-2 py-0.5 rounded-md border border-neutral-800">
                      {cap}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions & Footer */}
              <div className="pt-4 border-t border-neutral-800/60 flex items-center justify-between gap-3 mt-auto">
                <div className="text-xs text-neutral-400 flex items-center gap-3">
                  <span className="flex items-center gap-1"><Download className="w-3 h-3" /> {plugin.downloads}</span>
                  <span>★ {plugin.rating}</span>
                </div>

                <div className="flex items-center gap-2">
                  {plugin.installed ? (
                    <>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleActive(plugin.id)}
                        className={`text-xs h-8 rounded-lg ${plugin.active ? 'text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10' : 'text-neutral-400 hover:text-neutral-200'}`}
                      >
                        {plugin.active ? 'Disable' : 'Enable'}
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleInstall(plugin.id)}
                        className="text-xs h-8 rounded-lg border-neutral-800 text-neutral-400 hover:text-rose-400 hover:bg-rose-500/10 hover:border-rose-500/30"
                      >
                        Uninstall
                      </Button>
                    </>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => toggleInstall(plugin.id)}
                      className="text-xs h-8 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30"
                    >
                      <Download className="w-3.5 h-3.5 mr-1.5" /> Install
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default PluginMarketplace;
