'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notesService } from '@/services/notes';
import { catalogService } from '@/services/catalog';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Plus, Trash2, Edit } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

// Client-side cache for occupation labels
const CACHE_KEY = 'occupation_labels_cache';

function getOccupationCache(): Record<string, string> {
    if (typeof window === 'undefined') return {};
    try {
        const cached = localStorage.getItem(CACHE_KEY);
        return cached ? JSON.parse(cached) : {};
    } catch {
        return {};
    }
}

function setOccupationCache(uri: string, label: string) {
    if (typeof window === 'undefined') return;
    try {
        const cache = getOccupationCache();
        cache[uri] = label;
        localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
    } catch {
        // Silent fail if localStorage is not available
    }
}

export default function NotesPage() {
    const [editingId, setEditingId] = useState<string | null>(null);
    const [noteText, setNoteText] = useState('');
    const [occupationSearch, setOccupationSearch] = useState('');
    const [selectedOccupation, setSelectedOccupation] = useState<{ uri: string; label: string } | null>(null);
    const queryClient = useQueryClient();

    const { data, isLoading } = useQuery({
        queryKey: ['notes'],
        queryFn: () => notesService.searchNotes()
    });

    // Occupation autocomplete
    const { data: occupationOptions } = useQuery({
        queryKey: ['occupations-search', occupationSearch],
        queryFn: () => catalogService.searchOccupations(occupationSearch, 10),
        enabled: occupationSearch.length > 0
    });

    const upsertMutation = useMutation({
        mutationFn: ({ occupationUri, noteId, text }: { occupationUri: string; noteId: string; text: string }) =>
            notesService.upsertNote(occupationUri, noteId, text),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notes'] });
            setEditingId(null);
            setNoteText('');
            setSelectedOccupation(null);
            setOccupationSearch('');
        }
    });

    const deleteMutation = useMutation({
        mutationFn: ({ occupationUri, noteId }: { occupationUri: string; noteId: string }) =>
            notesService.deleteNote(occupationUri, noteId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notes'] });
        }
    });

    const handleSave = () => {
        if (!selectedOccupation || !noteText.trim()) return;

        // Cache the occupation label before saving
        setOccupationCache(selectedOccupation.uri, selectedOccupation.label);

        const noteId = editingId || `note-${Date.now()}`;
        upsertMutation.mutate({
            occupationUri: selectedOccupation.uri,
            noteId,
            text: noteText
        });
    };

    const handleSelectOccupation = (occ: { uri: string; label: string }) => {
        setSelectedOccupation(occ);
        setOccupationSearch('');
        // Cache immediately when selected
        setOccupationCache(occ.uri, occ.label);
    };

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="space-y-4">
                <h1 className="text-3xl font-bold tracking-tight text-primary">Notes Manager</h1>
                <p className="text-muted-foreground">
                    Attach private context and observations to occupations
                </p>
            </div>

            {/* Create Note Form */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Plus className="h-5 w-5" />
                        {editingId ? 'Edit Note' : 'Create Note'}
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <label className="text-sm font-medium">Select Occupation</label>
                        {!selectedOccupation ? (
                            <div className="relative mt-1">
                                <input
                                    type="text"
                                    value={occupationSearch}
                                    onChange={(e) => setOccupationSearch(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && occupationOptions && occupationOptions.length > 0) {
                                            e.preventDefault();
                                            handleSelectOccupation(occupationOptions[0]);
                                        }
                                    }}
                                    onFocus={() => { }}
                                    onBlur={() => setTimeout(() => setOccupationSearch(''), 200)}
                                    placeholder="Search for an occupation..."
                                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                                    autoComplete="off"
                                />
                                {occupationSearch.length > 0 && occupationOptions && occupationOptions.length > 0 && (
                                    <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-md max-h-60 overflow-auto">
                                        {occupationOptions.map((occ) => (
                                            <button
                                                key={occ.uri}
                                                type="button"
                                                onMouseDown={(e) => {
                                                    e.preventDefault();
                                                    handleSelectOccupation(occ);
                                                }}
                                                className="w-full text-left px-4 py-2 text-sm hover:bg-accent"
                                            >
                                                {occ.label}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 mt-1">
                                <Badge variant="secondary" className="text-sm px-3 py-1">
                                    {selectedOccupation.label}
                                </Badge>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        setSelectedOccupation(null);
                                        setOccupationSearch('');
                                    }}
                                >
                                    Change
                                </Button>
                            </div>
                        )}
                    </div>
                    <div>
                        <label className="text-sm font-medium">Note Content</label>
                        <textarea
                            value={noteText}
                            onChange={(e) => setNoteText(e.target.value)}
                            placeholder="Enter your notes about this occupation..."
                            rows={4}
                            className="mt-1 flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                        />
                    </div>
                    <div className="flex gap-2">
                        <Button
                            onClick={handleSave}
                            disabled={!selectedOccupation || !noteText.trim() || upsertMutation.isPending}
                        >
                            {upsertMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            {editingId ? 'Update' : 'Create'} Note
                        </Button>
                        {editingId && (
                            <Button
                                variant="outline"
                                onClick={() => {
                                    setEditingId(null);
                                    setNoteText('');
                                    setSelectedOccupation(null);
                                    setOccupationSearch('');
                                }}
                            >
                                Cancel
                            </Button>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Notes List */}
            <div className="space-y-4">
                <h2 className="text-2xl font-semibold">
                    All Notes <Badge variant="secondary">{data?.total || 0}</Badge>
                </h2>
                {data && data.notes.length === 0 ? (
                    <Alert>
                        <AlertDescription>
                            No notes yet. Create your first note above.
                        </AlertDescription>
                    </Alert>
                ) : (
                    <div className="grid gap-4">
                        {data?.notes.map((note) => (
                            <NoteCard
                                key={note.noteId}
                                note={note}
                                onEdit={(uri, id, text) => {
                                    setEditingId(id);
                                    setNoteText(text);
                                    // Try to get label from cache
                                    const cache = getOccupationCache();
                                    const label = cache[uri] || 'Loading...';
                                    setSelectedOccupation({ uri, label });
                                }}
                                onDelete={(uri, id) => deleteMutation.mutate({ occupationUri: uri, noteId: id })}
                                isDeleting={deleteMutation.isPending}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// Note Card Component with Cached Label Display
function NoteCard({ note, onEdit, onDelete, isDeleting }: {
    note: { noteId: string; occupationUri: string; text: string; updatedAt: string };
    onEdit: (uri: string, id: string, text: string) => void;
    onDelete: (uri: string, id: string) => void;
    isDeleting: boolean;
}) {
    // Check cache first, fallback to URI
    const cache = getOccupationCache();
    const occupationLabel = cache[note.occupationUri] || note.occupationUri;

    return (
        <Card>
            <CardHeader>
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <CardTitle className="text-base font-medium">
                            {occupationLabel}
                        </CardTitle>
                        <p className="text-xs text-muted-foreground mt-1">
                            Updated: {new Date(note.updatedAt).toLocaleString()}
                        </p>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onEdit(note.occupationUri, note.noteId, note.text)}
                        >
                            <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onDelete(note.occupationUri, note.noteId)}
                            disabled={isDeleting}
                        >
                            <Trash2 className="h-4 w-4" />
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <p className="text-sm whitespace-pre-wrap">{note.text}</p>
            </CardContent>
        </Card>
    );
}
