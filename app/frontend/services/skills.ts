import api from '@/lib/api';

export interface Skill {
    uri: string;
    label: string;
    description?: string;
    skillType?: string;
}

export interface SkillSearchParams {
    q?: string;
    type?: string;  // 'knowledge' or 'skill/competence'
    groups?: string;  // comma-separated URIs
    schemes?: string;  // comma-separated URIs
    relatedTo?: string;  // skill URI
    limit?: number;
    offset?: number;
}

export const skillsService = {
    search: async (params: SkillSearchParams): Promise<Skill[]> => {
        const response = await api.get<Skill[]>('/skills', { params });
        return response.data;
    }
};
