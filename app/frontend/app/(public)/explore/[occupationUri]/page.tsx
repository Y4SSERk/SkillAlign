'use client';

import Link from 'next/link';
import { OccupationDetail } from '@/components/features/occupations/occupation-detail';

interface PageProps {
    params: {
        occupationUri: string;
    };
}

export default function OccupationDetailPage({ params }: PageProps) {
    const decodedUri = decodeURIComponent(params.occupationUri);

    return (
        <div className="space-y-8">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Link href="/explore" className="hover:text-foreground">Explore Data</Link>
                <span>/</span>
                {/* We don't have the label here readily available without fetching, 
                    but OccupationDetail will show it in header.
                    Ideally we fetch it or just show / Occupation Details 
                */}
                <span className="text-foreground">Occupation Details</span>
            </div>

            <OccupationDetail occupationUri={decodedUri} />
        </div>
    );
}
