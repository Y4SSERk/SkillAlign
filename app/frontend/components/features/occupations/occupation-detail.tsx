'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { occupationService } from '@/services/occupations';
import { catalogService } from '@/services/catalog';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, AlertCircle, CheckCircle2, Filter, X } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { FilterDropdown } from '@/components/ui/filter-dropdown';
import { cn } from '@/lib/utils';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { OccupationSkillCard } from './occupation-skill-card';

interface OccupationDetailProps {
    occupationUri: string;
    onClose?: () => void;
    showHeader?: boolean;
    className?: string;
}

export function OccupationDetail({
    occupationUri,
    onClose,
    showHeader = true,
    className
}: OccupationDetailProps) {
    const decodedUri = decodeURIComponent(occupationUri);
    const [essentialOnly, setEssentialOnly] = useState(false);
    const [selectedSkillType, setSelectedSkillType] = useState<string>('');
    const [selectedSchemes, setSelectedSchemes] = useState<string[]>([]);
    const [showFilters, setShowFilters] = useState(false);

    // Fetch filter options
    const { data: conceptSchemes } = useQuery({
        queryKey: ['concept-schemes'],
        queryFn: () => catalogService.getConceptSchemes()
    });

    const { data: skillGap, isLoading, error } = useQuery({
        queryKey: ['skill-gap', decodedUri, essentialOnly, selectedSkillType, selectedSchemes],
        queryFn: () => occupationService.getSkillGap(decodedUri, {
            essentialOnly,
            skillType: selectedSkillType || undefined,
            schemes: selectedSchemes.length > 0 ? selectedSchemes.join(',') : undefined
        })
    });

    if (isLoading) {
        return (
            <div className="flex justify-center items-center min-h-[400px]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="space-y-4">
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>
                        Failed to load occupation details. {(error as Error).message}
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    if (!skillGap) return null;

    const totalSkills = skillGap.essentialSkills.length + skillGap.optionalSkills.length;

    const toggleScheme = (uri: string) => {
        setSelectedSchemes(prev =>
            prev.includes(uri) ? prev.filter(s => s !== uri) : [...prev, uri]
        );
    };

    return (
        <div className={cn("space-y-8", className)}>
            {/* Occupation Header */}
            {showHeader && (
                <div className="space-y-4">
                    <div className="flex items-start justify-between">
                        <div className="space-y-2">
                            <h1 className="text-3xl font-bold tracking-tight text-primary">
                                {skillGap.occupationLabel}
                            </h1>
                            {skillGap.iscoCode && (
                                <Badge variant="outline">ISCO {skillGap.iscoCode}</Badge>
                            )}
                        </div>
                        <div className="flex gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setShowFilters(!showFilters)}
                            >
                                <Filter className="h-4 w-4 mr-2" />
                                Filters
                            </Button>
                            {onClose && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={onClose}
                                    className="h-8 w-8 p-0"
                                >
                                    <X className="h-4 w-4" />
                                </Button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Filters Content */}
            <div className={cn(
                "bg-card border rounded-xl p-6 shadow-sm space-y-6 overflow-hidden transition-all duration-300 ease-in-out",
                showFilters ? "max-h-[1000px] opacity-100" : "max-h-0 opacity-0 p-0 border-0"
            )}>
                <div className="flex items-center gap-2 mb-2">
                    <Filter className="h-5 w-5 text-primary" />
                    <h2 className="font-semibold text-lg">Filter Skills</h2>
                </div>

                <div className="grid gap-8 md:grid-cols-2">
                    <div className="space-y-6">
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="essential-mode"
                                checked={essentialOnly}
                                onCheckedChange={setEssentialOnly}
                            />
                            <Label htmlFor="essential-mode" className="font-medium">Show essential skills only</Label>
                        </div>

                        <div className="space-y-3">
                            <Label className="text-sm font-medium text-muted-foreground">Skill Type</Label>
                            <Tabs value={selectedSkillType || "all"} onValueChange={(val) => setSelectedSkillType(val === "all" ? "" : val)}>
                                <TabsList className="grid w-full grid-cols-3">
                                    <TabsTrigger value="all">All</TabsTrigger>
                                    <TabsTrigger value="knowledge">Knowledge</TabsTrigger>
                                    <TabsTrigger value="skill/competence">Skills</TabsTrigger>
                                </TabsList>
                            </Tabs>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <span className="block text-sm font-medium text-muted-foreground mb-1">Concept Schemes</span>
                        <FilterDropdown
                            title=""
                            options={conceptSchemes?.map(s => ({ uri: s.uri, label: s.label })) || []}
                            selectedUris={selectedSchemes}
                            onToggle={toggleScheme}
                            onClear={() => setSelectedSchemes([])}
                            placeholder="Select concept schemes..."
                        />
                    </div>
                </div>
            </div>

            {/* Skills Overview */}
            <Card>
                <CardHeader>
                    <CardTitle>Skills Overview</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div className="space-y-1">
                            <p className="text-3xl font-bold text-primary">{totalSkills}</p>
                            <p className="text-sm text-muted-foreground">Total Skills</p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-3xl font-bold text-destructive">{skillGap.essentialSkills.length}</p>
                            <p className="text-sm text-muted-foreground">Essential</p>
                        </div>
                        <div className="space-y-1">
                            <p className="text-3xl font-bold text-secondary">{skillGap.optionalSkills.length}</p>
                            <p className="text-sm text-muted-foreground">Optional</p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Essential Skills */}
            {(!essentialOnly || skillGap.essentialSkills.length > 0) && (
                <div className="space-y-4">
                    <div className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-destructive" />
                        <h2 className="text-2xl font-semibold">Essential Skills</h2>
                        <Badge variant="destructive">{skillGap.essentialSkills.length}</Badge>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {skillGap.essentialSkills.map((skill) => (
                            <OccupationSkillCard key={skill.uri} skill={skill} variant="essential" />
                        ))}
                    </div>
                </div>
            )}

            {/* Optional Skills */}
            {!essentialOnly && skillGap.optionalSkills.length > 0 && (
                <div className="space-y-4">
                    <div className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-secondary" />
                        <h2 className="text-2xl font-semibold">Optional Skills</h2>
                        <Badge variant="secondary">{skillGap.optionalSkills.length}</Badge>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {skillGap.optionalSkills.map((skill) => (
                            <OccupationSkillCard key={skill.uri} skill={skill} variant="optional" />
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
