import api from '@/lib/api';
import type { AutocompleteOption } from '@/types';

export interface OccupationGroup {
    uri: string;
    code: string;
    label: string;
}

export interface SkillGroup {
    uri: string;
    label: string;
}

export interface ConceptScheme {
    uri: string;
    label: string;
}

// Cache to store the full list of occupation groups
let occupationGroupsCache: OccupationGroup[] | null = null;
let isFetchingGroups = false;

export const catalogService = {
    searchSkills: async (q: string, limit = 10): Promise<AutocompleteOption[]> => {
        const response = await api.get<AutocompleteOption[]>('/catalog/skills', {
            params: { q, limit }
        });
        return response.data;
    },

    searchOccupations: async (q: string, limit = 10): Promise<AutocompleteOption[]> => {
        const response = await api.get<AutocompleteOption[]>('/catalog/occupations', {
            params: { q, limit }
        });
        return response.data;
    },

    // Get occupation label from URI 
    getOccupationLabel: async (occupationUri: string): Promise<string> => {
        try {
            const response = await api.get('/occupations', {
                params: { limit: 100 }
            });
            const occupations = response.data;
            const match = occupations.find((o: any) => o.uri === occupationUri);
            if (match) return match.label;

            const parts = occupationUri.split('/');
            const lastPart = parts[parts.length - 1];
            const searchResults = await catalogService.searchOccupations(lastPart, 50);
            const searchMatch = searchResults.find(o => o.uri === occupationUri);
            return searchMatch?.label || occupationUri;
        } catch {
            return occupationUri;
        }
    },

    getOccupationGroups: async (q?: string, limit = 100): Promise<OccupationGroup[]> => {
        // If searching, use the normal API
        if (q) {
            const response = await api.get<OccupationGroup[]>('/catalog/occupation-groups', {
                params: { q, limit }
            });
            return response.data;
        }

        // If not searching and we have a cache, return it
        if (occupationGroupsCache) {
            return occupationGroupsCache;
        }

        // If we're already fetching, wait for it (simple promise-based lock could be added here if needed)
        // For now, we'll just implement the aggregator
        if (isFetchingGroups) return [];

        try {
            isFetchingGroups = true;

            // Recursive crawler to fetch all groups despite backend limits
            const fetchRecursively = async (prefix: string): Promise<OccupationGroup[]> => {
                const limit = 100;
                const response = await api.get<OccupationGroup[]>('/catalog/occupation-groups', {
                    params: { q: prefix, limit }
                });
                const data = response.data;

                // If we hit the limit, we likely missed some items. Drill down.
                // We stop recursing at length 2 to avoid explosion (26*26 = 676 requests max worst case)
                if (data.length === limit && prefix.length < 2) {
                    const suffixes = 'abcdefghijklmnopqrstuvwxyz'.split('');
                    const subResults = await Promise.all(
                        suffixes.map(char => fetchRecursively(prefix + char))
                    );
                    return subResults.flat();
                }

                return data;
            };

            // Start with base alphanumeric characters
            // We search for single letters. If any letter returns 100 items, the recursive function will split it.
            const baseKeys = 'abcdefghijklmnopqrstuvwxyz0123456789'.split('');
            const results = await Promise.all(baseKeys.map(key => fetchRecursively(key)));

            const allGroups = results.flat();
            // Deduplicate by URI
            const uniqueGroups = Array.from(new Map(allGroups.map(item => [item.uri, item])).values());

            // Sort alphabetically
            uniqueGroups.sort((a, b) => a.label.localeCompare(b.label));

            occupationGroupsCache = uniqueGroups;
            return uniqueGroups;
        } finally {
            isFetchingGroups = false;
        }
    },

    getSkillGroups: async (q?: string, limit = 50): Promise<SkillGroup[]> => {
        const response = await api.get<SkillGroup[]>('/catalog/skill-groups', {
            params: { q, limit }
        });
        return response.data;
    },

    getConceptSchemes: async (): Promise<ConceptScheme[]> => {
        const response = await api.get<ConceptScheme[]>('/catalog/concept-schemes');
        return response.data;
    }
};
