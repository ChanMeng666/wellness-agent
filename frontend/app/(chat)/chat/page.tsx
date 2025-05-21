'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { generateUUID } from '@/lib/utils';

export default function ChatIndexPage() {
  const router = useRouter();
  
  useEffect(() => {
    // Generate a new chat ID and redirect to it
    const newChatId = generateUUID();
    router.push(`/chat/${newChatId}`);
  }, [router]);
  
  return (
    <div className="flex h-screen w-full items-center justify-center">
      <p>Creating new chat session...</p>
    </div>
  );
} 