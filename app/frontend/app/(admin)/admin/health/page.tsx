'use client';

import { useQuery } from '@tanstack/react-query';
import { diagnosticsService } from '@/services/diagnostics';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Loader2, Database, GitBranch, Activity, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export default function SystemHealthPage() {
    const { data: nodes, isLoading: nodesLoading } = useQuery({
        queryKey: ['diagnostics-nodes'],
        queryFn: diagnosticsService.getNodesByLabel,
        refetchInterval: 30000 // Refresh every 30s
    });

    const { data: rels, isLoading: relsLoading } = useQuery({
        queryKey: ['diagnostics-rels'],
        queryFn: diagnosticsService.getRelsByType,
        refetchInterval: 30000
    });

    const { data: endpoints, isLoading: endpointsLoading } = useQuery({
        queryKey: ['diagnostics-endpoints'],
        queryFn: diagnosticsService.getEndpoints,
        refetchInterval: 60000 // Refresh every 60s
    });

    const { data: metrics, isLoading: metricsLoading } = useQuery({
        queryKey: ['diagnostics-metrics'],
        queryFn: diagnosticsService.getMetrics,
        refetchInterval: 5000 // Refresh every 5s for real-time feel
    });

    const isLoading = nodesLoading || relsLoading;

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    const totalNodes = nodes?.labels.reduce((sum, n) => sum + n.count, 0) || 0;
    const totalRels = rels?.types.reduce((sum, r) => sum + r.count, 0) || 0;

    // Group endpoints by tag
    const endpointsByTag = endpoints?.endpoints.reduce((acc, ep) => {
        const tag = ep.tags[0] || 'other';
        if (!acc[tag]) acc[tag] = [];
        acc[tag].push(ep);
        return acc;
    }, {} as Record<string, typeof endpoints.endpoints>) || {};

    return (
        <div className="space-y-12 px-6 py-12 md:py-20 max-w-screen-2xl mx-auto">
            <div className="space-y-4 border-b border-white/10 pb-8">
                <h1 className="text-5xl md:text-6xl font-serif font-medium tracking-tight text-primary">System Health</h1>
                <p className="text-lg text-muted-foreground font-light">
                    Real-time diagnostics for Neo4j knowledge graph and API performance
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="bg-white/5 border border-white/10 p-6 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground uppercase tracking-wider">Total Nodes</span>
                        <Database className="h-4 w-4 text-muted-foreground/40" />
                    </div>
                    <div className="text-3xl font-light tracking-tight">{totalNodes.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground/60">
                        {nodes?.labels.length} label types
                    </p>
                </div>

                <div className="bg-white/5 border border-white/10 p-6 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground uppercase tracking-wider">Relationships</span>
                        <GitBranch className="h-4 w-4 text-muted-foreground/40" />
                    </div>
                    <div className="text-3xl font-light tracking-tight">{totalRels.toLocaleString()}</div>
                    <p className="text-xs text-muted-foreground/60">
                        {rels?.types.length} relationship types
                    </p>
                </div>

                <div className="bg-white/5 border border-white/10 p-6 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground uppercase tracking-wider">API Endpoints</span>
                        <Activity className="h-4 w-4 text-muted-foreground/40" />
                    </div>
                    <div className="text-3xl font-light tracking-tight">{endpoints?.endpoints.length || 0}</div>
                    <p className="text-xs text-muted-foreground/60">
                        {Object.keys(endpointsByTag).length} categories
                    </p>
                </div>

                <div className="bg-white/5 border border-white/10 p-6 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground uppercase tracking-wider">Avg Latency</span>
                        <Zap className="h-4 w-4 text-muted-foreground/40" />
                    </div>
                    <div className="text-3xl font-light tracking-tight">
                        {metrics?.metrics.length
                            ? Math.round(metrics.metrics.reduce((sum, m) => sum + m.avg_ms, 0) / metrics.metrics.length)
                            : 0}ms
                    </div>
                    <p className="text-xs text-muted-foreground/60">
                        across {metrics?.metrics.length || 0} endpoints
                    </p>
                </div>
            </div>

            {/* API Endpoints */}
            <div className="space-y-6">
                <h2 className="text-2xl font-serif text-primary">API Endpoints</h2>
                {endpointsLoading ? (
                    <div className="flex justify-center p-12">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground/20" />
                    </div>
                ) : (
                    <div className="space-y-6">
                        {Object.entries(endpointsByTag).map(([tag, eps]) => (
                            <div key={tag} className="space-y-3">
                                <h3 className="text-sm uppercase tracking-widest text-muted-foreground/60">{tag}</h3>
                                <div className="grid gap-2">
                                    {eps.map((ep, idx) => (
                                        <div
                                            key={`${ep.method}-${ep.path}-${idx}`}
                                            className="flex items-center gap-4 p-4 bg-white/5 border border-white/5 hover:border-white/10 transition-colors font-mono text-sm"
                                        >
                                            <Badge
                                                variant="outline"
                                                className={`w-16 justify-center font-mono text-xs ${ep.method === 'GET' ? 'text-green-400 border-green-400/30' :
                                                        ep.method === 'POST' ? 'text-blue-400 border-blue-400/30' :
                                                            ep.method === 'PUT' ? 'text-yellow-400 border-yellow-400/30' :
                                                                ep.method === 'DELETE' ? 'text-red-400 border-red-400/30' :
                                                                    'text-muted-foreground border-white/20'
                                                    }`}
                                            >
                                                {ep.method}
                                            </Badge>
                                            <span className="text-muted-foreground">{ep.path}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Latency Metrics */}
            <div className="space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-serif text-primary">Latency Metrics</h2>
                    <span className="text-xs text-muted-foreground/40 font-mono">LIVE • 5s refresh</span>
                </div>
                {metricsLoading ? (
                    <div className="flex justify-center p-12">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground/20" />
                    </div>
                ) : metrics?.metrics.length === 0 ? (
                    <div className="text-center p-12 border border-dashed border-white/5 text-muted-foreground/40">
                        No metrics yet. Make some API requests to see latency data.
                    </div>
                ) : (
                    <div className="space-y-2">
                        {metrics?.metrics
                            .sort((a, b) => b.avg_ms - a.avg_ms)
                            .map((metric) => (
                                <div
                                    key={metric.endpoint}
                                    className="p-4 bg-white/5 border border-white/5 hover:bg-white/10 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-4 mb-3">
                                        <span className="font-mono text-sm text-muted-foreground">{metric.endpoint}</span>
                                        <div className="flex items-center gap-4 text-xs">
                                            <span className="text-muted-foreground/60">{metric.count} requests</span>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-3 gap-4 text-xs">
                                        <div>
                                            <span className="text-muted-foreground/60 block mb-1">AVG</span>
                                            <span className="text-lg font-light">{metric.avg_ms}ms</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground/60 block mb-1">MIN</span>
                                            <span className="text-lg font-light text-green-400/80">{metric.min_ms}ms</span>
                                        </div>
                                        <div>
                                            <span className="text-muted-foreground/60 block mb-1">MAX</span>
                                            <span className="text-lg font-light text-orange-400/80">{metric.max_ms}ms</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                    </div>
                )}
            </div>

            {/* Nodes by Label */}
            <div className="space-y-6">
                <h2 className="text-2xl font-serif text-primary">Nodes by Label</h2>
                <div className="grid gap-2">
                    {nodes?.labels.map((node) => (
                        <div key={node.label} className="flex items-center justify-between p-4 bg-white/5 border border-white/5">
                            <div className="flex items-center gap-3">
                                <Database className="h-4 w-4 text-muted-foreground/40" />
                                <span className="font-medium">{node.label}</span>
                            </div>
                            <span className="text-2xl font-light tabular-nums">
                                {node.count.toLocaleString()}
                            </span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Relationships by Type */}
            <div className="space-y-6">
                <h2 className="text-2xl font-serif text-primary">Relationships by Type</h2>
                <div className="grid gap-2">
                    {rels?.types.map((rel) => (
                        <div key={rel.type} className="flex items-center justify-between p-4 bg-white/5 border border-white/5">
                            <div className="flex items-center gap-3">
                                <GitBranch className="h-4 w-4 text-muted-foreground/40" />
                                <span className="font-medium">{rel.type}</span>
                            </div>
                            <span className="text-2xl font-light tabular-nums">
                                {rel.count.toLocaleString()}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
