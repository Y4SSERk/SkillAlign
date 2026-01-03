'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { occupationService } from '@/services/occupations';
import { catalogService } from '@/services/catalog';
import { Button } from '@/components/ui/button';
import { Loader2, Search, X } from 'lucide-react';
import Link from 'next/link';
import { FilterDropdown } from '@/components/ui/filter-dropdown';

export default function ExplorePage() {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedGroups, setSelectedGroups] = useState<string[]>([]);
    const [selectedSchemes, setSelectedSchemes] = useState<string[]>([]);
    const [debouncedQuery, setDebouncedQuery] = useState('');

    // Debounce search
    const handleSearch = (value: string) => {
        setSearchQuery(value);
        const timer = setTimeout(() => setDebouncedQuery(value), 500);
        return () => clearTimeout(timer);
    };

    // Fetch filter options
    const { data: occupationGroups } = useQuery({
        queryKey: ['occupation-groups'],
        queryFn: () => catalogService.getOccupationGroups()
    });

    const { data: conceptSchemes } = useQuery({
        queryKey: ['concept-schemes'],
        queryFn: () => catalogService.getConceptSchemes()
    });

    // Search occupations with filters
    const { data: occupations, isLoading } = useQuery({
        queryKey: ['occupations', debouncedQuery, selectedGroups, selectedSchemes],
        queryFn: () => occupationService.search({
            q: debouncedQuery || undefined,
            groups: selectedGroups.length > 0 ? selectedGroups.join(',') : undefined,
            schemes: selectedSchemes.length > 0 ? selectedSchemes.join(',') : undefined,
            limit: 50
        })
    });

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

    const clearFilters = () => {
        setSelectedGroups([]);
        setSelectedSchemes([]);
        setSearchQuery('');
        setDebouncedQuery('');
    };

    const hasFilters = selectedGroups.length > 0 || selectedSchemes.length > 0 || debouncedQuery;

    return (
        <div className="space-y-12 px-6 py-12 md:py-20 max-w-screen-2xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 border-b border-white/10 pb-12">
                <div className="space-y-4 max-w-xl">
                    <h1 className="text-5xl md:text-6xl font-serif font-medium tracking-tight text-primary">Explore</h1>
                    <p className="text-lg text-muted-foreground font-light leading-relaxed">
                        Navigate the usage ESCO taxonomy. Discover occupations, skills, and relations through our intelligence engine.
                    </p>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground/50">
                    <span className="text-4xl font-light">{occupations?.length || 0}</span>
                    <span className="text-sm uppercase tracking-widest text-muted-foreground/40">Results</span>
                </div>
            </div>

            {/* Controls Bar */}
            <div className="sticky top-20 z-30 bg-background/80 backdrop-blur-xl -mx-6 px-6 py-4 border-b border-transparent transition-all">
                <div className="flex flex-col xl:flex-row gap-4 xl:items-center justify-between">
                    <div className="block md:flex items-center gap-4 flex-1">
                        <div className="relative flex-1 max-w-md">
                            <Search className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => handleSearch(e.target.value)}
                                placeholder="Search by keyword..."
                                className="w-full bg-transparent border-b border-white/20 py-3 pl-8 pr-4 text-base focus:outline-none focus:border-white transition-colors placeholder:text-muted-foreground/50"
                            />
                        </div>

                        <div className="flex gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0 pt-4 md:pt-0 no-scrollbar">
                            <FilterDropdown
                                title="Groups"
                                options={occupationGroups?.map(g => ({ uri: g.uri, label: g.label, code: g.code })) || []}
                                selectedUris={selectedGroups}
                                onToggle={toggleGroup}
                                onClear={() => setSelectedGroups([])}
                                placeholder="Filter Groups"
                            />
                            <FilterDropdown
                                title="Schemes"
                                options={conceptSchemes?.map(s => ({ uri: s.uri, label: s.label })) || []}
                                selectedUris={selectedSchemes}
                                onToggle={toggleScheme}
                                onClear={() => setSelectedSchemes([])}
                                placeholder="Filter Schemes"
                            />
                            {hasFilters && (
                                <Button variant="ghost" size="icon" onClick={clearFilters} className="text-muted-foreground hover:text-destructive">
                                    <X className="h-4 w-4" />
                                </Button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Results Grid */}
            {isLoading ? (
                <div className="flex justify-center p-32">
                    <Loader2 className="h-10 w-10 animate-spin text-muted-foreground/20" />
                </div>
            ) : occupations && occupations.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-px bg-white/5 border border-white/5">
                    {occupations.map((occupation) => (
                        <Link key={occupation.uri} href={`/explore/${encodeURIComponent(occupation.uri)}`} className="group relative bg-background h-64 p-8 flex flex-col justify-between hover:bg-white/5 transition-colors overflow-hidden">
                            <div className="space-y-4 z-10">
                                {occupation.iscoCode && (
                                    <span className="text-xs font-mono text-muted-foreground/40 block">
                                        {occupation.iscoCode}
                                    </span>
                                )}
                                <h3 className="text-xl font-medium tracking-tight text-primary group-hover:underline decoration-1 underline-offset-4">
                                    {occupation.label}
                                </h3>
                            </div>

                            <div className="opacity-0 translate-y-4 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300">
                                <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
                                    {occupation.description}
                                </p>
                            </div>

                            {/* Decorative corner */}
                            <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-white/10 opacity-50"></div>
                        </Link>
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center p-24 text-center border border-dashed border-white/10 rounded-lg">
                    <p className="text-muted-foreground text-lg">No matches found.</p>
                </div>
            )}
        </div>
    );
}
