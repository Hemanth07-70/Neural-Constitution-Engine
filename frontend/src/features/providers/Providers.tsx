import React from 'react';
import { useProvidersList, useProvidersHealth, useProviderModels } from './providerApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Server, Database, CheckCircle, XCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export const Providers: React.FC = () => {
  const { data: providers, isLoading: isLoadingProviders } = useProvidersList();
  const { data: healthData, isLoading: isLoadingHealth } = useProvidersHealth();
  const { data: modelsData, isLoading: isLoadingModels } = useProviderModels();

  if (isLoadingProviders || isLoadingHealth || isLoadingModels) {
    return (
      <div className="p-8 space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-48 w-full rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2">AI Providers</h1>
        <p className="text-neutral-400">Manage and monitor connected AI model providers for the Governance Engine.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {providers?.map((provider) => {
          const isHealthy = healthData?.providers[provider];
          const models = modelsData?.[provider] || [];

          return (
            <Card key={provider} className="bg-neutral-900/50 border-neutral-800 backdrop-blur-sm overflow-hidden group hover:border-neutral-700 transition-all duration-300">
              <CardHeader className="pb-4">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-neutral-800 rounded-lg group-hover:bg-neutral-700 transition-colors">
                      <Server className="w-5 h-5 text-neutral-300" />
                    </div>
                    <CardTitle className="capitalize text-xl text-neutral-100">{provider}</CardTitle>
                  </div>
                  <Badge variant={isHealthy ? "default" : "destructive"} className={isHealthy ? "bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20" : ""}>
                    {isHealthy ? (
                      <span className="flex items-center gap-1"><CheckCircle className="w-3 h-3" /> Healthy</span>
                    ) : (
                      <span className="flex items-center gap-1"><XCircle className="w-3 h-3" /> Offline</span>
                    )}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-neutral-400 mb-2 flex items-center gap-2">
                    <Database className="w-4 h-4" />
                    Available Models
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {models.length > 0 ? (
                      models.slice(0, 5).map(model => (
                        <Badge key={model} variant="secondary" className="bg-neutral-800 text-neutral-300 font-mono text-xs">
                          {model}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-neutral-500 italic">No models available</span>
                    )}
                    {models.length > 5 && (
                      <Badge variant="secondary" className="bg-neutral-800 text-neutral-300 font-mono text-xs">
                        +{models.length - 5} more
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-neutral-800/50 flex justify-between items-center text-sm text-neutral-400">
                  <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4" />
                    <span>Telemetry Active</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
