import api from '@/lib/api';

export interface NodeCount {
    label: string;
    count: number;
}

export interface RelCount {
    type: string;
    count: number;
}

export interface NodesByLabelResponse {
    labels: NodeCount[];
}

export interface RelsByTypeResponse {
    types: RelCount[];
}

export interface Endpoint {
    method: string;
    path: string;
    name: string;
    tags: string[];
}

export interface EndpointsResponse {
    endpoints: Endpoint[];
}

export interface Metric {
    endpoint: string;
    count: number;
    avg_ms: number;
    min_ms: number;
    max_ms: number;
}

export interface MetricsResponse {
    metrics: Metric[];
}

export const diagnosticsService = {
    getNodesByLabel: async (): Promise<NodesByLabelResponse> => {
        const response = await api.get<NodesByLabelResponse>('/admin/diagnostics/nodes-by-label');
        return response.data;
    },

    getRelsByType: async (): Promise<RelsByTypeResponse> => {
        const response = await api.get<RelsByTypeResponse>('/admin/diagnostics/rels-by-type');
        return response.data;
    },

    getEndpoints: async (): Promise<EndpointsResponse> => {
        const response = await api.get<EndpointsResponse>('/admin/diagnostics/endpoints');
        return response.data;
    },

    getMetrics: async (): Promise<MetricsResponse> => {
        const response = await api.get<MetricsResponse>('/admin/diagnostics/metrics');
        return response.data;
    }
};
