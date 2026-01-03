'use client';

import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface SelectedSkillBadgeProps {
    uri: string;
    label: string;
    onRemove: (uri: string) => void;
}

export function SelectedSkillBadge({ uri, label, onRemove }: SelectedSkillBadgeProps) {
    return (
        <Badge
            variant="secondary"
            className="gap-2 py-2 px-3 bg-white/10 hover:bg-white/20 text-primary-foreground font-normal rounded-sm border-transparent transition-colors"
        >
            {label}
            <button
                onClick={() => onRemove(uri)}
                className="hover:text-destructive transition-colors"
            >
                <X className="h-3 w-3" />
            </button>
        </Badge>
    );
}
