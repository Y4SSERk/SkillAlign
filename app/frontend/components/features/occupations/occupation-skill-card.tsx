'use client';

import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import type { SkillDetail } from '@/types';

interface OccupationSkillCardProps {
    skill: SkillDetail;
    variant: 'essential' | 'optional';
}

export function OccupationSkillCard({ skill, variant }: OccupationSkillCardProps) {
    const borderColor = variant === 'essential' ? 'border-l-destructive' : 'border-l-secondary';

    return (
        <Card className={cn("border-l-4", borderColor)}>
            <CardHeader className="pb-3">
                <CardTitle className="text-base font-semibold">{skill.label}</CardTitle>
                {(skill.skillType || skill.skill_type) && (
                    <Badge variant="outline" className="w-fit text-xs">
                        {skill.skillType || skill.skill_type}
                    </Badge>
                )}
            </CardHeader>
        </Card>
    );
}
