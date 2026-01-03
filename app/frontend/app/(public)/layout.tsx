import { Header } from '@/components/layout/header';

export default function PublicLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <main className="flex-1 container py-6">{children}</main>
        </div>
    );
}
