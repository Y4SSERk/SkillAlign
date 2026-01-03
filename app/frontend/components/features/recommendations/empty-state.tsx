'use client';

import { Loader2, Filter } from 'lucide-react';

export function LoadingState() {
    return (
        <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-muted-foreground/30 border border-dashed border-white/5 rounded-sm">
            <Loader2 className="h-12 w-12 mb-4 animate-spin opacity-20" />
            <p className="font-light">Analyzing skill patterns...</p>
        </div>
    );
}

export function InitialState() {
    return (
        <div className="h-full min-h-[1200px] flex flex-col items-center justify-center text-muted-foreground/20 border border-dashed border-white/5 rounded-none group">
            <div className="relative mb-6">
                <Filter className="h-20 w-20 stroke-[0.5] group-hover:scale-110 transition-transform duration-700" />
                <div className="absolute inset-0 bg-primary/20 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
            </div>
            <p className="font-serif italic text-3xl tracking-tight opacity-70">Discovery awaits</p>
            <p className="text-[12px] uppercase tracking-[0.3em] mt-6 opacity-50">Add your expertise to unlock matches</p>
        </div>
    );
}

export function NoResultsState() {
    return (
        <div className="py-20 text-center border border-dashed border-white/5 rounded-sm">
            <p className="text-muted-foreground font-light">No direct matches found for your current skill selection.</p>
        </div>
    );
}
