'use client';

import * as React from 'react';
import { Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    FilterOption,
    FilterDropdownTrigger,
    FilterSearchInput,
    FilterPagination,
    FilterOptionItem
} from './filter-dropdown-items';

interface FilterDropdownProps {
    title: string;
    options: FilterOption[];
    selectedUris: string[];
    onToggle: (uri: string) => void;
    onClear: () => void;
    placeholder?: string;
}

export function FilterDropdown({
    title,
    options,
    selectedUris,
    onToggle,
    onClear,
    placeholder = "Select options...",
}: FilterDropdownProps) {
    const [open, setOpen] = React.useState(false);
    const [currentPage, setCurrentPage] = React.useState(0);
    const [searchQuery, setSearchQuery] = React.useState('');
    const pageSize = 100;

    // Filter options based on search query
    const filteredOptions = React.useMemo(() => {
        if (!searchQuery) return options;
        const lower = searchQuery.toLowerCase().trim();
        return options.filter(o =>
            o.label.toLowerCase().includes(lower) ||
            (o.code && o.code.toLowerCase().includes(lower))
        );
    }, [options, searchQuery]);

    // Reset pagination when search changes
    React.useEffect(() => {
        setCurrentPage(0);
    }, [searchQuery]);

    const totalPages = Math.ceil(filteredOptions.length / pageSize);
    const paginatedOptions = filteredOptions.slice(
        currentPage * pageSize,
        (currentPage + 1) * pageSize
    );

    const startRange = currentPage * pageSize + 1;
    const endRange = Math.min((currentPage + 1) * pageSize, filteredOptions.length);

    return (
        <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
                <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-muted-foreground uppercase tracking-wider text-[10px]">
                    {title}
                </label>
                {selectedUris.length > 0 && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onClear}
                        className="h-auto p-0 text-xs text-muted-foreground hover:text-primary font-normal"
                    >
                        Clear Selected
                    </Button>
                )}
            </div>
            <Popover open={open} onOpenChange={setOpen} modal={false}>
                <PopoverTrigger asChild>
                    <FilterDropdownTrigger
                        open={open}
                        selectedUris={selectedUris}
                        options={options}
                        placeholder={placeholder}
                    />
                </PopoverTrigger>
                <PopoverContent className="w-[400px] p-0 overflow-hidden rounded-xl border-primary/20 shadow-xl" align="start" side="bottom" sideOffset={25} avoidCollisions={false}>
                    <FilterSearchInput value={searchQuery} onChange={setSearchQuery} />

                    {filteredOptions.length > 0 && totalPages > 1 && (
                        <FilterPagination
                            start={startRange}
                            end={endRange}
                            total={filteredOptions.length}
                            currentPage={currentPage}
                            totalPages={totalPages}
                            onPrev={() => setCurrentPage(prev => prev - 1)}
                            onNext={() => setCurrentPage(prev => prev + 1)}
                        />
                    )}

                    <ScrollArea className="h-96">
                        <div className="p-1.5">
                            {filteredOptions.length === 0 ? (
                                <div className="p-8 text-sm text-center text-muted-foreground flex flex-col items-center gap-2">
                                    <Filter className="h-8 w-8 opacity-20" />
                                    No options available
                                </div>
                            ) : (
                                paginatedOptions.map((option) => (
                                    <FilterOptionItem
                                        key={option.uri}
                                        option={option}
                                        isSelected={selectedUris.includes(option.uri)}
                                        onToggle={onToggle}
                                    />
                                ))
                            )}
                        </div>
                    </ScrollArea>
                </PopoverContent>
            </Popover>
        </div>
    );
}
