export interface Skill {
    uri: string;
    label: string;
    skillType?: string;
    skill_type?: string;
    relationType?: string;
    relation_type?: string;
}

export interface Occupation {
    uri: string;
    label: string;
    description?: string;
    iscoCode?: string;
}

export interface RecommendationRequest {
    skills: string[];
    limit?: number;
    occupation_groups?: string[];
    schemes?: string[];
}

export interface OccupationRecommendation {
    uri: string;
    label: string;
    description?: string;
    isco_code?: string;
    similarity_score: number;
    match_percentage: number;
    matched_skills: Skill[];
    missing_skills: Skill[];
    groups: string[];
    schemes: string[];
}

export interface RecommendationResponse {
    total: number;
    user_skills: string[];
    recommendations: OccupationRecommendation[];
}

export interface SearchFilters {
    q?: string;
    group?: string;
    limit?: number;
    offset?: number;
}

export interface AutocompleteOption {
    uri: string;
    label: string;
}

export interface SkillDetail {
    uri: string;
    label: string;
    relationType: string;
    relation_type?: string;
    skillType?: string;
    skill_type?: string;
}

export interface SkillGapResponse {
    occupationUri: string;
    occupationLabel: string;
    iscoCode?: string;
    essentialSkills: SkillDetail[];
    optionalSkills: SkillDetail[];
}
