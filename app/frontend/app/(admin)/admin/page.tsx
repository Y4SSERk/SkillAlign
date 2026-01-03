'use client';

import { useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { diagnosticsService } from '@/services/diagnostics';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Loader2, Database, GitBranch, Activity } from 'lucide-react';

export default function AdminDashboard() {
    const queryClient = useQueryClient();

    // Auto-refresh data when navigating to dashboard
    useEffect(() => {
        queryClient.invalidateQueries({ queryKey: ['diagnostics-nodes'] });
        queryClient.invalidateQueries({ queryKey: ['diagnostics-rels'] });
    }, [queryClient]);

    const { data: nodes, isLoading: nodesLoading } = useQuery({
        queryKey: ['diagnostics-nodes'],
        queryFn: diagnosticsService.getNodesByLabel
    });

    const { data: rels, isLoading: relsLoading } = useQuery({
        queryKey: ['diagnostics-rels'],
        queryFn: diagnosticsService.getRelsByType
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

    return (
        <div className="space-y-8">
            <div className="space-y-4">
                <div className="flex items-center gap-2">
                    <Activity className="h-8 w-8 text-primary" />
                    <h1 className="text-3xl font-bold tracking-tight text-primary">Admin Dashboard</h1>
                </div>
                <p className="text-muted-foreground">
                    Real-time system diagnostics and knowledge graph statistics
                </p>
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Nodes</CardTitle>
                        <Database className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalNodes.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">
                            Across {nodes?.labels.length} label types
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Relationships</CardTitle>
                        <GitBranch className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{totalRels.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">
                            Across {rels?.types.length} relationship types
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Nodes by Label */}
            <Card>
                <CardHeader>
                    <CardTitle>Nodes by Label</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {nodes?.labels.map((node) => (
                            <div key={node.label} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <Database className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">{node.label}</span>
                                </div>
                                <span className="text-2xl font-bold tabular-nums">
                                    {node.count.toLocaleString()}
                                </span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Relationships by Type */}
            <Card>
                <CardHeader>
                    <CardTitle>Relationships by Type</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {rels?.types.map((rel) => (
                            <div key={rel.type} className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <GitBranch className="h-4 w-4 text-muted-foreground" />
                                    <span className="font-medium">{rel.type}</span>
                                </div>
                                <span className="text-2xl font-bold tabular-nums">
                                    {rel.count.toLocaleString()}
                                </span>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
