import api from '@/lib/api';
import { RecommendationRequest, RecommendationResponse } from '@/types';

export const recommendationService = {
    getRecommendations: async (data: RecommendationRequest): Promise<RecommendationResponse> => {
        // Note: occupation_groups and schemes filters can be added to RecommendationRequest
        const response = await api.post<RecommendationResponse>('/recommendations', data);
        return response.data;
    }
};
