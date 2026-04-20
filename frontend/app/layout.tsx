import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'DataLens AI - Conversational Business Intelligence',
  description: 'Chat with your CSV data using natural language',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}