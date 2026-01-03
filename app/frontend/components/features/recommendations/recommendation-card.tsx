'use client';

import type { OccupationRecommendation } from '@/types';

interface RecommendationCardProps {
    rec: OccupationRecommendation;
    index: number;
    onClick: () => void;
}

export function RecommendationCard({ rec, index, onClick }: RecommendationCardProps) {
    return (
        <div
            onClick={onClick}
            className="group relative p-8 bg-white/[0.02] hover:bg-white/[0.04] border border-white/5 hover:border-primary/20 transition-all duration-500 cursor-pointer rounded-none active:scale-[0.99]"
        >
            {/* Accent Line */}
            <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-primary/0 group-hover:bg-primary transition-all duration-500" />

            <div className="flex items-start justify-between gap-4 mb-4">
                <div className="space-y-1">
                    <div className="flex items-center gap-3">
                        <span className="font-mono text-xs text-muted-foreground/50">
                            {(index + 1).toString().padStart(2, '0')}
                        </span>
                        <h3 className="text-xl font-medium text-primary group-hover:text-white transition-colors">
                            {rec.label}
                        </h3>
                    </div>
                    {rec.isco_code && (
                        <span className="text-xs text-muted-foreground/60 block pl-8">
                            ISCO {rec.isco_code}
                        </span>
                    )}
                </div>
                <div className="text-right">
                    <span className="text-3xl font-light tracking-tighter text-white">
                        {Math.round(rec.match_percentage || 0)}%
                    </span>
                </div>
            </div>

            <div className="pl-8 space-y-4">
                {rec.description && (
                    <p className="text-sm text-muted-foreground line-clamp-2 font-light leading-relaxed">
                        {rec.description}
                    </p>
                )}

                <div className="flex flex-wrap gap-x-6 gap-y-2 text-xs">
                    {rec.matched_skills && rec.matched_skills.length > 0 && (
                        <div className="flex items-center gap-2 text-muted-foreground">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500/50"></span>
                            <span>{rec.matched_skills.length} Matched Skills</span>
                        </div>
                    )}
                    {rec.missing_skills && rec.missing_skills.length > 0 && (
                        <div className="flex items-center gap-2 text-muted-foreground">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-500/50"></span>
                            <span>{rec.missing_skills.length} To Learn</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
