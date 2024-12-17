// src/app/layout.tsx
import { Metadata } from 'next';
import { Providers } from '@/providers';
import { MainLayout } from '@/components/layout/main-layout';
import { ErrorBoundary } from '@/components/error-boundary';
import { Source_Sans_3 } from 'next/font/google';
import './globals.css';

// Font configuration
const sourceSans = Source_Sans_3({ 
  subsets: ['latin'],
  variable: '--font-source-sans',
});

// Metadata configuration
export const metadata: Metadata = {
  title: {
    default: 'WhatsNew! - AI-Powered News Aggregator',
    template: '%s | WhatsNew!'
  },
  description: 'Stay informed with AI-curated news summaries from trusted sources',
  keywords: ['AI', 'news', 'summaries', 'aggregator', 'artificial intelligence'],
  authors: [{ name: 'WhatsNew Team' }],
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: process.env.NEXT_PUBLIC_APP_URL,
    title: 'WhatsNew! - AI-Powered News Aggregator',
    description: 'Stay informed with AI-curated news summaries from trusted sources',
    siteName: 'WhatsNew!'
  },
  twitter: {
    card: 'summary_large_image',
    title: 'WhatsNew! - AI-Powered News Aggregator',
    description: 'Stay informed with AI-curated news summaries from trusted sources',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

// Root layout configuration
interface RootLayoutProps {
  children: React.ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" className={sourceSans.variable}>
      <body className={`${sourceSans.className} min-h-screen bg-gray-50 antialiased`}>
        <ErrorBoundary>
          <Providers>
            {/* 
              Special case for auth pages - they don't use MainLayout
              This keeps login/register pages full screen
            */}
            {isAuthPage() ? (
              children
            ) : (
              <MainLayout>
                {children}
              </MainLayout>
            )}
          </Providers>
        </ErrorBoundary>

        {/* Portal root for modals */}
        <div id="modal-root" />
      </body>
    </html>
  );
}

// Helper function to determine if current page is an auth page
function isAuthPage(): boolean {
  if (typeof window === 'undefined') return false;
  const authPaths = ['/login', '/register', '/forgot-password', '/reset-password'];
  return authPaths.some(path => window.location.pathname.startsWith(path));
}

// Error handling for root layout
export function generateStaticParams() {
  return [];
}

// Handle layout errors
export function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <div className="rounded-lg bg-white p-8 shadow-lg">
        <h1 className="mb-4 text-2xl font-bold text-red-600">
          Something went wrong!
        </h1>
        <p className="mb-4 text-gray-600">
          {error.message || 'An unexpected error occurred'}
        </p>
        <button
          onClick={reset}
          className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          Try again
        </button>
      </div>
    </div>
  );
}