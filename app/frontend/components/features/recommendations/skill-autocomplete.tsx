'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from '@/hooks/use-debounce';
import { catalogService } from '@/services/catalog';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { Loader2, Check } from 'lucide-react';

interface AutocompleteProps {
    value: string;
    onChange: (value: string) => void;
    onSelect: (item: { uri: string; label: string }) => void;
    placeholder?: string;
}

export function SkillAutocomplete({ value, onChange, onSelect, placeholder }: AutocompleteProps) {
    const [isOpen, setIsOpen] = useState(false);
    const debouncedQuery = useDebounce(value, 300);

    const { data: options, isLoading, error } = useQuery({
        queryKey: ['skills-autocomplete', debouncedQuery],
        queryFn: () => catalogService.searchSkills(debouncedQuery),
        enabled: debouncedQuery.length > 0,
    });

    const handleSelect = (item: { uri: string; label: string }) => {
        onSelect(item);
        onChange('');
        setIsOpen(false);
    };

    return (
        <div className="relative w-full">
            <Input
                value={value}
                onChange={(e) => {
                    onChange(e.target.value);
                    setIsOpen(true);
                }}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' && options && options.length > 0) {
                        e.preventDefault();
                        handleSelect(options[0]);
                    }
                }}
                onFocus={() => setIsOpen(true)}
                onBlur={() => {
                    // Slight delay to allow onMouseDown to fire
                    setTimeout(() => setIsOpen(false), 200);
                }}
                placeholder={placeholder || "Type to search skills..."}
                className="w-full"
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
                            No skills found
                        </div>
                    )}

                    {error && (
                        <div className="p-4 text-sm text-destructive text-center">
                            Failed to fetch skills
                        </div>
                    )}

                    {!isLoading && options && options.length > 0 && (
                        <div className="py-1">
                            {options.map((option) => (
                                <button
                                    key={option.uri}
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                        handleSelect(option);
                                    }}
                                    className={cn(
                                        "w-full text-left px-4 py-2 text-sm hover:bg-accent hover:text-accent-foreground cursor-pointer flex items-center justify-between"
                                    )}
                                >
                                    <span>{option.label}</span>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
