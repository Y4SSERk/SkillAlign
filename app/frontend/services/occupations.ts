import api from '@/lib/api';
import type { Occupation, SkillGapResponse } from '@/types';

export interface OccupationSearchParams {
    q?: string;
    groups?: string;  // comma-separated URIs
    requiredSkills?: string;  // comma-separated URIs
    schemes?: string;  // comma-separated URIs
    limit?: number;
    offset?: number;
}

export interface SkillGapParams {
    essentialOnly?: boolean;
    skillType?: string;  // 'knowledge' or 'skill/competence'
    skillGroups?: string;  // comma-separated URIs
    schemes?: string;  // comma-separated URIs
}

export const occupationService = {
    search: async (params: OccupationSearchParams): Promise<Occupation[]> => {
        const response = await api.get<Occupation[]>('/occupations', { params });
        return response.data;
    },

    getSkillGap: async (occupationUri: string, filters?: SkillGapParams): Promise<SkillGapResponse> => {
        const encodedUri = encodeURIComponent(occupationUri);
        const response = await api.get<SkillGapResponse>(`/occupations/${encodedUri}/skill-gap`, {
            params: filters
        });
        return response.data;
    }
};
