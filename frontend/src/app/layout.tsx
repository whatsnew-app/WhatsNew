import type { Metadata } from 'next';
import { Providers } from '@/providers';
import './globals.css';
import { Source_Sans_3 } from 'next/font/google';

const sourceSans = Source_Sans_3({ 
  subsets: ['latin'],
  variable: '--font-source-sans',
});

export const metadata: Metadata = {
  title: 'WhatsNews AI - AI-Powered News Aggregator',
  description: 'Stay informed with AI-curated news from multiple sources',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={sourceSans.variable}>
      <body className={sourceSans.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}