import api from '@/lib/api';

export interface NoteCreate {
    text: string;
}

export interface NoteResponse {
    noteId: string;
    occupationUri: string;
    text: string;
    createdAt: string;
    updatedAt: string;
}

export interface NoteSearchResponse {
    total: number;
    notes: NoteResponse[];
}

export const notesService = {
    searchNotes: async (occupationUri?: string, limit = 100, skip = 0): Promise<NoteSearchResponse> => {
        const response = await api.get<NoteSearchResponse>('/notes', {
            params: { occupation_uri: occupationUri, limit, skip }
        });
        return response.data;
    },

    upsertNote: async (occupationUri: string, noteId: string, text: string): Promise<NoteResponse> => {
        const encodedUri = encodeURIComponent(occupationUri);
        const response = await api.put<NoteResponse>(
            `/notes/admin/occupations/${encodedUri}/notes/${noteId}`,
            { text }
        );
        return response.data;
    },

    deleteNote: async (occupationUri: string, noteId: string): Promise<void> => {
        const encodedUri = encodeURIComponent(occupationUri);
        await api.delete(`/notes/admin/occupations/${encodedUri}/notes/${noteId}`);
    }
};
