'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { occupationService } from '@/services/occupations';
import { catalogService } from '@/services/catalog';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowRight, Target } from 'lucide-react';
import Link from 'next/link';
import { SkillAutocomplete } from '@/components/features/recommendations/skill-autocomplete';
import type { AutocompleteOption } from '@/types';

export default function RoadmapPage() {
    const [targetOccupation, setTargetOccupation] = useState<AutocompleteOption | null>(null);
    const [currentSkills, setCurrentSkills] = useState<AutocompleteOption[]>([]);
    const [occupationInput, setOccupationInput] = useState('');
    const [skillInput, setSkillInput] = useState('');

    const { data: skillGap, isLoading } = useQuery({
        queryKey: ['roadmap-skill-gap', targetOccupation?.uri],
        queryFn: () => occupationService.getSkillGap(targetOccupation!.uri),
        enabled: !!targetOccupation
    });

    const handleSelectOccupation = (occ: AutocompleteOption) => {
        setTargetOccupation(occ);
        setOccupationInput('');
    };

    const handleAddSkill = (skill: AutocompleteOption) => {
        if (!currentSkills.find(s => s.uri === skill.uri)) {
            setCurrentSkills([...currentSkills, skill]);
        }
    };

    const handleRemoveSkill = (uri: string) => {
        setCurrentSkills(currentSkills.filter(s => s.uri !== uri));
    };

    // Calculate skill gap
    const currentSkillUris = new Set(currentSkills.map(s => s.uri));
    const missingEssential = skillGap?.essentialSkills.filter(s => !currentSkillUris.has(s.uri)) || [];
    const missingOptional = skillGap?.optionalSkills.filter(s => !currentSkillUris.has(s.uri)) || [];
    const matchedEssential = skillGap?.essentialSkills.filter(s => currentSkillUris.has(s.uri)) || [];

    const progress = skillGap
        ? Math.round((matchedEssential.length / skillGap.essentialSkills.length) * 100)
        : 0;

    return (
        <div className="space-y-8">
            <div className="space-y-4">
                <h1 className="text-3xl font-bold tracking-tight text-primary">Skill Roadmap</h1>
                <p className="text-muted-foreground">
                    Visualize the path from your current skills to your target career.
                </p>
            </div>

            {/* Step 1: Select Target Occupation */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        Step 1: Select Target Occupation
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {!targetOccupation ? (
                        <div className="space-y-2">
                            <OccupationAutocomplete
                                value={occupationInput}
                                onChange={setOccupationInput}
                                onSelect={handleSelectOccupation}
                                placeholder="Search for your target occupation..."
                            />
                            <p className="text-sm text-muted-foreground">
                                Start typing to search for an occupation (e.g., "Software Developer")
                            </p>
                        </div>
                    ) : (
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Badge variant="default" className="text-base px-3 py-1">
                                    {targetOccupation.label}
                                </Badge>
                            </div>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                    setTargetOccupation(null);
                                    setCurrentSkills([]);
                                }}
                            >
                                Change
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Step 2: Add Current Skills */}
            {targetOccupation && (
                <Card>
                    <CardHeader>
                        <CardTitle>Step 2: Add Your Current Skills</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <SkillAutocomplete
                            value={skillInput}
                            onChange={setSkillInput}
                            onSelect={handleAddSkill}
                            placeholder="Add your current skills..."
                        />
                        <div className="flex flex-wrap gap-2 min-h-[50px] p-4 border rounded-md bg-muted/20">
                            {currentSkills.length === 0 ? (
                                <span className="text-sm text-muted-foreground italic">No skills added yet.</span>
                            ) : (
                                currentSkills.map(skill => (
                                    <Badge key={skill.uri} variant="secondary" className="px-2 py-1">
                                        {skill.label}
                                        <button
                                            onClick={() => handleRemoveSkill(skill.uri)}
                                            className="ml-2 hover:text-destructive"
                                        >
                                            ×
                                        </button>
                                    </Badge>
                                ))
                            )}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Roadmap Visualization */}
            {targetOccupation && currentSkills.length > 0 && (
                <>
                    {isLoading ? (
                        <div className="flex justify-center p-12">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    ) : skillGap && (
                        <>
                            {/* Progress Card */}
                            <Card className="border-primary">
                                <CardHeader>
                                    <CardTitle>Your Progress</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium">Essential Skills Completion</span>
                                            <span className="text-2xl font-bold text-primary">{progress}%</span>
                                        </div>
                                        <div className="h-3 w-full bg-muted rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-primary transition-all duration-500"
                                                style={{ width: `${progress}%` }}
                                            />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <p className="text-muted-foreground">Have</p>
                                                <p className="text-lg font-semibold">{matchedEssential.length} / {skillGap.essentialSkills.length}</p>
                                            </div>
                                            <div>
                                                <p className="text-muted-foreground">Need</p>
                                                <p className="text-lg font-semibold text-destructive">{missingEssential.length}</p>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Missing Essential Skills */}
                            {missingEssential.length > 0 && (
                                <Card className="border-destructive">
                                    <CardHeader>
                                        <CardTitle className="text-destructive flex items-center gap-2">
                                            <ArrowRight className="h-5 w-5" />
                                            Next Steps: Essential Skills to Learn
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid gap-2 md:grid-cols-2">
                                            {missingEssential.map(skill => (
                                                <div key={skill.uri} className="flex items-start gap-2 p-3 border rounded-lg bg-destructive/5">
                                                    <div className="h-2 w-2 rounded-full bg-destructive mt-2" />
                                                    <div className="flex-1">
                                                        <p className="font-medium">{skill.label}</p>
                                                        {skill.skillType && (
                                                            <Badge variant="outline" className="mt-1 text-xs">
                                                                {skill.skillType}
                                                            </Badge>
                                                        )}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Optional Skills */}
                            {missingOptional.length > 0 && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-secondary">Optional Skills (Nice to Have)</CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                                            {missingOptional.slice(0, 12).map(skill => (
                                                <div key={skill.uri} className="p-2 border rounded bg-secondary/5">
                                                    <p className="text-sm">{skill.label}</p>
                                                </div>
                                            ))}
                                            {missingOptional.length > 12 && (
                                                <div className="p-2 text-sm text-muted-foreground italic">
                                                    +{missingOptional.length - 12} more
                                                </div>
                                            )}
                                        </div>
                                    </CardContent>
                                </Card>
                            )}

                            {/* Action */}
                            <div className="flex justify-center">
                                <Link href={`/explore/${encodeURIComponent(targetOccupation.uri)}`}>
                                    <Button size="lg">
                                        View Full Occupation Details
                                        <ArrowRight className="ml-2 h-4 w-4" />
                                    </Button>
                                </Link>
                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    );
}

// Occupation Autocomplete Component
function OccupationAutocomplete({ value, onChange, onSelect, placeholder }: {
    value: string;
    onChange: (value: string) => void;
    onSelect: (item: AutocompleteOption) => void;
    placeholder?: string;
}) {
    const [isOpen, setIsOpen] = useState(false);
    const { data: options, isLoading } = useQuery({
        queryKey: ['occupations-autocomplete', value],
        queryFn: () => catalogService.searchOccupations(value),
        enabled: value.length > 0,
    });

    return (
        <div className="relative">
            <input
                type="text"
                value={value}
                onChange={(e) => {
                    onChange(e.target.value);
                    setIsOpen(true);
                }}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' && options && options.length > 0) {
                        e.preventDefault();
                        onSelect(options[0]);
                        setIsOpen(false);
                    }
                }}
                onFocus={() => setIsOpen(true)}
                onBlur={() => setTimeout(() => setIsOpen(false), 200)}
                placeholder={placeholder}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                autoComplete="off"
            />
            {isOpen && value.length > 0 && (
                <div className="absolute z-50 w-full mt-1 bg-popover border rounded-md shadow-md max-h-60 overflow-auto">
                    {isLoading && (
                        <div className="flex items-center justify-center p-4">
                            <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                    )}
                    {!isLoading && options && options.length === 0 && (
                        <div className="p-4 text-sm text-muted-foreground text-center">
                            No occupations found
                        </div>
                    )}
                    {!isLoading && options && options.length > 0 && (
                        <div className="py-1">
                            {options.map((option) => (
                                <button
                                    key={option.uri}
                                    type="button"
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                        onSelect(option);
                                        setIsOpen(false);
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground"
                                >
                                    {option.label}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
