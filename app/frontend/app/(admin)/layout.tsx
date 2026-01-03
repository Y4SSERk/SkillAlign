import { Sidebar } from '@/components/layout/sidebar';

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 bg-background p-4 md:p-8 pt-20 lg:pt-8">{children}</main>
        </div>
    );
}
