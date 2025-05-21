'use client';

import { SessionProvider } from 'next-auth/react';
import { ReactNode } from 'react';

// Simplified providers without ThemeProvider to avoid import errors
export function Providers({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      {children}
    </SessionProvider>
  );
} 