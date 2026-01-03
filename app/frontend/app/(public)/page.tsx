import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Network, Brain, Search, GitBranch, ArrowRight, Database, Code2 } from 'lucide-react';

export default function LandingPage() {
    return (
        <main className="min-h-screen bg-background flex flex-col">
            {/* Hero Section */}
            <section className="flex flex-col items-center justify-center pt-32 pb-20 px-6 transition-all duration-500">
                <div className="w-full max-w-screen-xl grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-24 items-end">
                    <div className="lg:col-span-8 space-y-8">
                        <h1 className="text-6xl md:text-8xl lg:text-9xl font-serif font-medium tracking-tighter text-primary leading-[0.9]">
                            Skill<br />Align
                        </h1>
                        <p className="text-xl md:text-2xl text-muted-foreground font-light max-w-2xl leading-relaxed">
                            A curated intelligence engine for career taxonomy and skill-gap analysis.
                            <span className="block mt-2 text-primary opacity-80">Powered by AI. Grounded in ESCO. Explained by Graph.</span>
                        </p>
                    </div>

                    <div className="lg:col-span-4 flex flex-col items-start gap-6 pb-2">
                        <div className="space-y-4 w-full">
                            <Link href="/recommendations" className="block w-full">
                                <Button size="lg" className="w-full justify-between h-14 text-lg font-light bg-primary text-primary-foreground hover:bg-primary/90 rounded-none border border-transparent group">
                                    Match My Skills
                                    <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                                </Button>
                            </Link>
                            <Link href="/explore" className="block w-full">
                                <Button variant="outline" size="lg" className="w-full justify-between h-14 text-lg font-light bg-transparent border-white/20 hover:bg-white/5 hover:text-primary rounded-none group">
                                    Explore Data
                                    <Database className="ml-2 h-5 w-5 opacity-50 group-hover:opacity-100 transition-opacity" />
                                </Button>
                            </Link>
                        </div>
                        <div className="text-xs text-muted-foreground/40 font-mono pt-8">
                            V 1.0
                        </div>
                    </div>
                </div>
            </section>

            {/* Core Capabilities Section */}
            <section className="py-32 px-6 border-t border-white/5 bg-transparent">
                <div className="max-w-screen-xl mx-auto">
                    <div className="flex flex-col gap-24 md:gap-32">
                        {/* Feature 1 */}
                        <div className="group grid md:grid-cols-12 gap-8 md:gap-16 items-center">
                            <div className="md:col-span-2 flex md:justify-end">
                                <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-500 group-hover:scale-110">
                                    <Brain className="h-[34px] w-[34px] text-primary" />
                                </div>
                            </div>
                            <div className="md:col-span-10 space-y-4">
                                <h3 className="text-2xl md:text-3xl font-bold text-foreground tracking-tight">
                                    Deep Semantic Intelligence.
                                </h3>
                                <p className="text-xl text-muted-foreground font-light leading-relaxed max-w-3xl">
                                    Experience search that understands context. By utilizing <span className="text-foreground/80 font-semibold">Vector Embeddings</span>, SkillAlign decodes the <span className="text-foreground/80 font-semibold">latent meaning</span> of your profile, surfacing opportunities that standard algorithms <span className="text-foreground/80 font-semibold">systematically overlook</span>.
                                </p>
                            </div>
                        </div>

                        {/* Feature 2 */}
                        <div className="group grid md:grid-cols-12 gap-8 md:gap-16 items-center">
                            <div className="md:col-span-2 flex md:justify-end">
                                <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-500 group-hover:scale-110">
                                    <Network className="h-[34px] w-[34px] text-primary" />
                                </div>
                            </div>
                            <div className="md:col-span-10 space-y-4">
                                <h3 className="text-2xl md:text-3xl font-bold text-foreground tracking-tight">
                                    Enterprise-Grade Knowledge Graph.
                                </h3>
                                <p className="text-xl text-muted-foreground font-light leading-relaxed max-w-3xl">
                                    Orchestrating the complexity of the labor market. Our <span className="text-foreground/80 font-semibold">Neo4j Engine</span> indexes over <span className="text-foreground/80 font-semibold">13,400+ data points</span>, mapping the <span className="text-foreground/80 font-semibold">hidden architecture</span> of occupations to guide your trajectory with <span className="text-foreground/80 font-semibold">absolute precision</span>.
                                </p>
                            </div>
                        </div>

                        {/* Feature 3 */}
                        <div className="group grid md:grid-cols-12 gap-8 md:gap-16 items-center">
                            <div className="md:col-span-2 flex md:justify-end">
                                <div className="h-20 w-20 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-500 group-hover:scale-110">
                                    <GitBranch className="h-[34px] w-[34px] text-primary" />
                                </div>
                            </div>
                            <div className="md:col-span-10 space-y-4">
                                <h3 className="text-2xl md:text-3xl font-bold text-foreground tracking-tight">
                                    Deterministically Explainable Insights.
                                </h3>
                                <p className="text-xl text-muted-foreground font-light leading-relaxed max-w-3xl">
                                    Complete visibility into the algorithm. We demystify the black box by presenting a <span className="text-foreground/80 font-semibold">visual audit</span> of your <span className="text-foreground/80 font-semibold">Skill Gap</span>—delineating precisely which <span className="text-foreground/80 font-semibold">Essential Competencies</span> you possess and the <span className="text-foreground/80 font-semibold">Strategic Skills</span> required to advance.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Technical Footer */}
            <footer className="mt-auto py-12 px-6 border-t border-white/5">
                <div className="max-w-screen-xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="text-sm text-muted-foreground font-light">
                        <span className="font-medium text-primary">SkillAlign</span> &copy; 2026.
                        <span className="opacity-50 mx-2">|</span>
                        Grounded in <a href="https://esco.ec.europa.eu" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors underline decoration-white/20 underline-offset-4">ESCO Taxonomy v1.1</a>
                    </div>

                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground/40 font-mono uppercase tracking-wider">
                            <span>Next.js 14</span>
                            <span>•</span>
                            <span>FastAPI</span>
                            <span>•</span>
                            <span>Neo4j</span>
                        </div>
                        <a
                            href="https://github.com/Y4SSERk/SkillAlign"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-white transition-colors pl-6 border-l border-white/10"
                        >
                            <Code2 className="h-4 w-4" />
                            GitHub
                        </a>
                    </div>
                </div>
            </footer>
        </main>
    );
}
