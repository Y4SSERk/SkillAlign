'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Menu, X } from 'lucide-react';

export function Header() {
    const pathname = usePathname();
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const routes = [
        { href: '/recommendations', label: 'Match My Skills' },
        { href: '/roadmap', label: 'Skill Roadmap' },
        { href: '/explore', label: 'Explore Data' },
    ];

    return (
        <header className="sticky top-0 z-50 w-full bg-background/50 backdrop-blur-xl border-b border-white/5 transition-all duration-300">
            <div className="container flex h-16 items-center px-6 md:px-12">
                <Link href="/" className="mr-12 flex items-center space-x-2">
                    <span className="text-2xl font-serif font-medium tracking-tight text-primary">SkillAlign</span>
                </Link>

                {/* Desktop Navigation */}
                <nav className="hidden md:flex items-center space-x-8 text-sm font-medium tracking-wide">
                    {routes.map((route) => (
                        <Link
                            key={route.href}
                            href={route.href}
                            className={cn(
                                "transition-colors duration-200 hover:text-foreground",
                                pathname === route.href ? "text-foreground" : "text-muted-foreground/60"
                            )}
                        >
                            {route.label}
                        </Link>
                    ))}
                </nav>

                <div className="ml-auto hidden md:flex items-center space-x-4">
                    <Link href="/admin">
                        <Button variant="ghost" size="sm" className="text-muted-foreground/60 hover:text-foreground font-normal hover:bg-transparent">
                            Admin
                        </Button>
                    </Link>
                </div>

                {/* Mobile Menu Button */}
                <button
                    className="ml-auto md:hidden p-2 text-muted-foreground hover:text-primary transition-colors"
                    onClick={() => setIsMenuOpen(!isMenuOpen)}
                >
                    {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                </button>
            </div>

            {/* Mobile Navigation Overlay */}
            {isMenuOpen && (
                <div className="md:hidden fixed inset-0 top-16 z-40 bg-background/95 backdrop-blur-md animate-in fade-in duration-300">
                    <nav className="flex flex-col items-center justify-center h-full space-y-8 p-6">
                        {routes.map((route) => (
                            <Link
                                key={route.href}
                                href={route.href}
                                onClick={() => setIsMenuOpen(false)}
                                className={cn(
                                    "text-2xl font-serif tracking-tight transition-colors",
                                    pathname === route.href ? "text-primary" : "text-muted-foreground/60"
                                )}
                            >
                                {route.label}
                            </Link>
                        ))}
                        <Link
                            href="/admin"
                            onClick={() => setIsMenuOpen(false)}
                            className={cn(
                                "text-2xl font-serif tracking-tight transition-colors",
                                pathname.startsWith('/admin') ? "text-primary" : "text-muted-foreground/60"
                            )}
                        >
                            Admin Portal
                        </Link>

                        <div className="mt-12 text-[10px] uppercase tracking-[0.5em] text-muted-foreground/20">
                            SkillAlign v2.0
                        </div>
                    </nav>
                </div>
            )}
        </header>
    );
}
