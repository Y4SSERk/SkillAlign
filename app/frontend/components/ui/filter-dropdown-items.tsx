'use client';

import * as React from 'react';
import { Check, ChevronDown, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';

export interface FilterOption {
    uri: string;
    label: string;
    code?: string;
}

interface FilterDropdownTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    open: boolean;
    selectedUris: string[];
    options: FilterOption[];
    placeholder: string;
}

export const FilterDropdownTrigger = React.forwardRef<HTMLButtonElement, FilterDropdownTriggerProps>(
    ({ open, selectedUris, options, placeholder, ...props }, ref) => {
        return (
            <Button
                variant="outline"
                role="combobox"
                aria-expanded={open}
                className="w-full justify-between h-auto min-h-10 py-2.5 border-dashed hover:border-primary/50 transition-all shadow-sm"
                ref={ref}
                {...props}
            >
                <div className="flex flex-wrap gap-1.5 items-center max-w-[90%]">
                    {selectedUris.length > 0 ? (
                        <>
                            <Badge variant="secondary" className="rounded-md px-2 py-0.5 font-medium bg-primary/10 text-primary border-none">
                                {selectedUris.length} selected
                            </Badge>
                            <div className="hidden space-x-1 lg:flex overflow-hidden">
                                {selectedUris.length > 2 ? (
                                    <span className="text-xs text-muted-foreground ml-1">
                                        including {options.find(o => selectedUris.includes(o.uri))?.label.substring(0, 20)}...
                                    </span>
                                ) : (
                                    options
                                        .filter((opt) => selectedUris.includes(opt.uri))
                                        .map((opt) => (
                                            <Badge
                                                variant="outline"
                                                key={opt.uri}
                                                className="rounded-md px-2 py-0.5 font-normal whitespace-nowrap overflow-hidden max-w-[150px] bg-background"
                                            >
                                                {opt.code ? `${opt.code}` : opt.label.substring(0, 15)}
                                            </Badge>
                                        ))
                                )}
                            </div>
                        </>
                    ) : (
                        <span className="text-muted-foreground text-sm">{placeholder}</span>
                    )}
                </div>
                <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
        );
    }
);

FilterDropdownTrigger.displayName = 'FilterDropdownTrigger';

interface FilterSearchInputProps {
    value: string;
    onChange: (value: string) => void;
}

export function FilterSearchInput({ value, onChange }: FilterSearchInputProps) {
    return (
        <div className="p-2 border-b bg-muted/30">
            <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Search options..."
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="pl-9 bg-background border-primary/20"
                />
            </div>
        </div>
    );
}

interface FilterPaginationProps {
    start: number;
    end: number;
    total: number;
    currentPage: number;
    totalPages: number;
    onPrev: () => void;
    onNext: () => void;
}

export function FilterPagination({ start, end, total, currentPage, totalPages, onPrev, onNext }: FilterPaginationProps) {
    return (
        <div className="flex items-center justify-between px-3 py-2 bg-muted/10 border-b">
            <span className="text-[11px] font-medium text-muted-foreground">
                {start}-{end} of {total}
            </span>
            <div className="flex items-center gap-1">
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    disabled={currentPage === 0}
                    onClick={(e) => {
                        e.stopPropagation();
                        onPrev();
                    }}
                >
                    <ChevronDown className="h-4 w-4 rotate-90" />
                </Button>
                <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    disabled={currentPage === totalPages - 1}
                    onClick={(e) => {
                        e.stopPropagation();
                        onNext();
                    }}
                >
                    <ChevronDown className="h-4 w-4 -rotate-90" />
                </Button>
            </div>
        </div>
    );
}

interface FilterOptionItemProps {
    option: FilterOption;
    isSelected: boolean;
    onToggle: (uri: string) => void;
}

export function FilterOptionItem({ option, isSelected, onToggle }: FilterOptionItemProps) {
    return (
        <div
            className={cn(
                "relative flex w-full cursor-pointer select-none items-center rounded-lg px-2.5 py-2 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground",
                isSelected && "bg-primary/5 text-primary font-medium"
            )}
            onClick={() => onToggle(option.uri)}
        >
            <div
                className={cn(
                    "mr-3 flex h-4 w-4 items-center justify-center rounded border border-primary/30 transition-all",
                    isSelected
                        ? "bg-primary border-primary text-primary-foreground scale-110"
                        : "opacity-50"
                )}
            >
                {isSelected && <Check className="h-3 w-3 bold" />}
            </div>
            <span className="flex-1 truncate">
                {option.code && <span className="mr-3 font-mono text-xs opacity-60 bg-muted px-1.5 py-0.5 rounded uppercase tracking-tighter">{option.code}</span>}
                {option.label}
            </span>
        </div>
    );
}
