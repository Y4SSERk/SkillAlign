'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { recommendationService } from '@/services/recommendations';
import { catalogService } from '@/services/catalog';
import { Button } from '@/components/ui/button';
import { SkillAutocomplete } from '@/components/features/recommendations/skill-autocomplete';
import { Loader2, AlertCircle, Filter, X } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import type { RecommendationResponse } from '@/types';
import { FilterDropdown } from '@/components/ui/filter-dropdown';
import { cn } from '@/lib/utils';
import { OccupationDetail } from '@/components/features/occupations/occupation-detail';

// Extracted sub-components
import { SelectedSkillBadge } from '@/components/features/recommendations/selected-skill-badge';
import { RecommendationCard } from '@/components/features/recommendations/recommendation-card';
import { LoadingState, InitialState, NoResultsState } from '@/components/features/recommendations/empty-state';

interface SelectedSkill {
    uri: string;
    label: string;
}

export default function RecommendationsPage() {
    const [skillInput, setSkillInput] = useState('');
    const [skills, setSkills] = useState<SelectedSkill[]>([]);
    const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
    const [selectedSchemes, setSelectedSchemes] = useState<string[]>([]);
    const [showFilters, setShowFilters] = useState(false);
    const [expandedOccupationUri, setExpandedOccupationUri] = useState<string | null>(null);

    // Fetch filter options
    const { data: occupationGroups } = useQuery({
        queryKey: ['occupation-groups'],
        queryFn: () => catalogService.getOccupationGroups()
    });

    const { data: conceptSchemes } = useQuery({
        queryKey: ['concept-schemes'],
        queryFn: () => catalogService.getConceptSchemes()
    });

    const { mutate: getRecommendations, isPending, data: response, error } = useMutation<
        RecommendationResponse,
        Error,
        { skills: string[]; occupation_groups?: string[]; schemes?: string[]; limit: number }
    >({
        mutationFn: recommendationService.getRecommendations
    });

    const handleAddSkill = (skill: { uri: string; label: string }) => {
        if (!skills.find(s => s.uri === skill.uri)) {
            setSkills([...skills, skill]);
        }
    };

    const handleRemoveSkill = (skillUri: string) => {
        setSkills(skills.filter(s => s.uri !== skillUri));
    };

    const toggleGroup = (uri: string) => {
        setSelectedGroups(prev =>
            prev.includes(uri) ? prev.filter(g => g !== uri) : [...prev, uri]
        );
    };

    const toggleScheme = (uri: string) => {
        setSelectedSchemes(prev =>
            prev.includes(uri) ? prev.filter(s => s !== uri) : [...prev, uri]
        );
    };

    const handleSearch = () => {
        setExpandedOccupationUri(null);
        getRecommendations({
            skills: skills.map(s => s.uri),
            occupation_groups: selectedGroups.length > 0 ? selectedGroups : undefined,
            schemes: selectedSchemes.length > 0 ? selectedSchemes : undefined,
            limit: 10
        });
    };

    return (
        <div className="min-h-screen pb-32 max-w-screen-xl mx-auto px-6 pt-12 md:pt-20 space-y-16">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">

                {/* Left Panel: Input */}
                <div className="lg:col-span-5 space-y-8">
                    <div className="space-y-4">
                        <h1 className="text-4xl md:text-5xl font-serif font-medium tracking-tight text-primary">Match Skills</h1>
                        <p className="text-lg text-muted-foreground font-light">
                            Curate your skill profile to generate intelligent occupation matches.
                        </p>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-none p-6 md:p-8 space-y-6 backdrop-blur-sm">
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Add Skills</label>
                                <SkillAutocomplete
                                    value={skillInput}
                                    onChange={setSkillInput}
                                    onSelect={handleAddSkill}
                                    placeholder="Search skill set..."
                                />
                            </div>

                            <div className="min-h-[100px]">
                                {skills.length === 0 ? (
                                    <div className="text-sm text-muted-foreground/40 italic py-4">No skills selected...</div>
                                ) : (
                                    <div className="flex flex-wrap gap-2">
                                        {skills.map((skill) => (
                                            <SelectedSkillBadge
                                                key={skill.uri}
                                                uri={skill.uri}
                                                label={skill.label}
                                                onRemove={handleRemoveSkill}
                                            />
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="pt-6 border-t border-white/10">
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setShowFilters(!showFilters)}
                                className="text-muted-foreground hover:text-primary w-full justify-between"
                            >
                                <span className="flex items-center gap-2">
                                    <Filter className="h-4 w-4" />
                                    Advanced Filters
                                </span>
                                <span className="text-xs">{showFilters ? '-' : '+'}</span>
                            </Button>

                            <div className={cn(
                                "grid gap-6 overflow-hidden transition-all duration-300 ease-in-out",
                                showFilters ? "grid-rows-[1fr] opacity-100 mt-6" : "grid-rows-[0fr] opacity-0"
                            )}>
                                <div className="min-h-0 space-y-6">
                                    <FilterDropdown
                                        title="Occupation Groups"
                                        options={occupationGroups?.map(g => ({ uri: g.uri, label: g.label, code: g.code })) || []}
                                        selectedUris={selectedGroups}
                                        onToggle={toggleGroup}
                                        onClear={() => setSelectedGroups([])}
                                        placeholder="Select groups"
                                    />

                                    <FilterDropdown
                                        title="Concept Schemes"
                                        options={conceptSchemes?.map(s => ({ uri: s.uri, label: s.label })) || []}
                                        selectedUris={selectedSchemes}
                                        onToggle={toggleScheme}
                                        onClear={() => setSelectedSchemes([])}
                                        placeholder="Select schemes"
                                    />
                                </div>
                            </div>
                        </div>

                        <Button
                            onClick={handleSearch}
                            disabled={isPending || skills.length === 0}
                            className="w-full h-12 text-base font-medium rounded-sm"
                            size="lg"
                        >
                            {isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Analyze Matches"}
                        </Button>
                    </div>
                    {error && (
                        <Alert variant="destructive" className="bg-destructive/10 border-destructive/20 text-destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Error</AlertTitle>
                            <AlertDescription>
                                {error.message}
                            </AlertDescription>
                        </Alert>
                    )}
                </div>

                {/* Right Panel: Results */}
                <div className="lg:col-span-7 space-y-6">
                    {response && (
                        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-8">
                            <div className="flex items-end justify-between border-b border-white/10 pb-4">
                                <h2 className="text-2xl font-serif text-primary">Intelligence Results</h2>
                                <span className="text-sm text-muted-foreground font-mono">{response.total || 0} MATCHES FOUND</span>
                            </div>

                            <div className="space-y-4">
                                {response.recommendations && response.recommendations.length > 0 ? (
                                    response.recommendations.map((rec, index) => (
                                        <RecommendationCard
                                            key={rec.uri}
                                            rec={rec}
                                            index={index}
                                            onClick={() => setExpandedOccupationUri(rec.uri)}
                                        />
                                    ))
                                ) : (
                                    <NoResultsState />
                                )}
                            </div>
                        </div>
                    )}

                    {isPending && <LoadingState />}

                    {!response && !isPending && <InitialState />}
                </div>
            </div>

            {/* Modal Overlay for Expanded View */}
            {expandedOccupationUri && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm p-4 sm:p-6 animate-in fade-in duration-300" onClick={() => setExpandedOccupationUri(null)}>
                    <div
                        className="relative w-full max-w-5xl h-[90vh] bg-[#0a0a0a] border border-white/10 rounded-sm shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95 slide-in-from-bottom-4 duration-300"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="absolute right-6 top-6 z-10">
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setExpandedOccupationUri(null)}
                                className="h-8 w-8 rounded-full bg-white/5 hover:bg-white/10 hover:text-white"
                            >
                                <X className="h-4 w-4" />
                                <span className="sr-only">Close</span>
                            </Button>
                        </div>
                        <div className="flex-1 overflow-y-auto p-0">
                            <OccupationDetail
                                occupationUri={expandedOccupationUri}
                                onClose={() => setExpandedOccupationUri(null)}
                                className="max-w-4xl mx-auto py-12 px-8"
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
