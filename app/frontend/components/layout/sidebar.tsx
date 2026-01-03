'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LayoutDashboard, Settings, Activity, FileText, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

const adminRoutes = [
    { href: '/admin', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/admin/notes', label: 'Notes Manager', icon: FileText },
    { href: '/admin/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Mobile Toggle */}
            <Button
                variant="ghost"
                size="icon"
                className="lg:hidden fixed top-4 left-4 z-50 bg-background/80 backdrop-blur-sm border"
                onClick={() => setIsOpen(!isOpen)}
            >
                {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>

            {/* Overlay */}
            {isOpen && (
                <div
                    className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}

            {/* Sidebar */}
            <div className={cn(
                "fixed inset-y-0 left-0 z-40 w-64 border-r bg-muted/40 p-4 transition-transform duration-300 transform lg:translate-x-0 lg:sticky lg:top-0 lg:h-screen",
                isOpen ? "translate-x-0" : "-translate-x-full"
            )}>
                <div className="mb-8 px-4 flex items-center gap-2 pt-12 lg:pt-0">
                    <span className="text-lg font-bold text-primary">Admin Portal</span>
                </div>
                <nav className="space-y-2">
                    {adminRoutes.map((route) => {
                        const Icon = route.icon;
                        return (
                            <Link
                                key={route.href}
                                href={route.href}
                                onClick={() => setIsOpen(false)}
                                className={cn(
                                    "flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
                                    pathname === route.href ? "bg-accent text-accent-foreground" : "text-muted-foreground"
                                )}
                            >
                                <Icon className="h-4 w-4" />
                                <span>{route.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                <div className="mt-auto absolute bottom-8 px-4">
                    <Link href="/" className="text-sm text-muted-foreground hover:text-primary">
                        ← Back to App
                    </Link>
                </div>
            </div>
        </>
    );
}
