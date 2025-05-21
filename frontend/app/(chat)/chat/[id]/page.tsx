import { cookies } from 'next/headers';
import { auth } from '@/app/(auth)/auth';
import { Chat } from '@/components/chat';
import { DataStreamHandler } from '@/components/data-stream-handler';
import { DEFAULT_CHAT_MODEL } from '@/lib/ai/models';
import type { UIMessage } from 'ai';
import { generateUUID } from '@/lib/utils';

export default async function Page(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const { id } = params;
  
  // Get session using our mock auth
  const session = await auth();
  
  // Mock empty initial messages array
  const initialMessages: UIMessage[] = [];
  
  // Mock chat data
  const chat = {
    id: id,
    visibility: 'private',
    userId: session.user.id
  };

  const cookieStore = await cookies();
  const chatModelFromCookie = cookieStore.get('chat-model');
  const chatModel = chatModelFromCookie?.value || DEFAULT_CHAT_MODEL;

  return (
    <>
      <Chat
        id={chat.id}
        initialMessages={initialMessages}
        initialChatModel={chatModel}
        initialVisibilityType={'private'}
        isReadonly={false}
        session={session}
        autoResume={false}
      />
      <DataStreamHandler id={id} />
    </>
  );
}
