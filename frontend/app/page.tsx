'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { generateUUID } from '@/lib/utils';

export default function Page() {
  const router = useRouter();
  
  useEffect(() => {
    // Generate a chat ID and directly redirect to it to bypass auth checks
    const chatId = generateUUID();
    router.push(`/chat/${chatId}`);
  }, [router]);
  
  // This will show briefly while redirecting
  return (
    <div className="flex h-screen w-full items-center justify-center">
      <p>Loading chat interface...</p>
    </div>
  );
} 