'use client';

import type { Attachment, UIMessage } from 'ai';
import { useChat } from '@ai-sdk/react';
import { useEffect, useState } from 'react';
import useSWR, { useSWRConfig } from 'swr';
import { ChatHeader } from '@/components/chat-header';
import type { Vote } from '@/lib/db/schema';
import { fetcher, fetchWithErrorHandlers, generateUUID } from '@/lib/utils';
import { Artifact } from './artifact';
import { MultimodalInput } from './multimodal-input';
import { Messages } from './messages';
import type { VisibilityType } from './visibility-selector';
import { useArtifactSelector } from '@/hooks/use-artifact';
import { unstable_serialize } from 'swr/infinite';
import { getChatHistoryPaginationKey } from './sidebar-history';
import { toast } from './toast';
import type { Session } from 'next-auth';
import { useSearchParams } from 'next/navigation';
import { useChatVisibility } from '@/hooks/use-chat-visibility';
import { useAutoResume } from '@/hooks/use-auto-resume';
import { ChatSDKError } from '@/lib/errors';
import { type UserRole } from './role-selector';

export function Chat({
  id,
  initialMessages,
  initialChatModel,
  initialVisibilityType,
  isReadonly,
  session,
  autoResume,
}: {
  id: string;
  initialMessages: Array<UIMessage>;
  initialChatModel: string;
  initialVisibilityType: VisibilityType;
  isReadonly: boolean;
  session: Session;
  autoResume: boolean;
}) {
  const { mutate } = useSWRConfig();
  const [userRole, setUserRole] = useState<UserRole>('employee');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const { visibilityType } = useChatVisibility({
    chatId: id,
    initialVisibilityType,
  });

  const {
    messages,
    setMessages,
    handleSubmit: originalHandleSubmit,
    input,
    setInput,
    append,
    status,
    stop,
    reload,
    experimental_resume,
    data,
  } = useChat({
    id,
    initialMessages,
    experimental_throttle: 100,
    sendExtraMessageFields: true,
    generateId: generateUUID,
    fetch: fetchWithErrorHandlers,
    experimental_prepareRequestBody: (body) => ({
      id,
      message: body.messages.at(-1),
      selectedChatModel: initialChatModel,
      selectedVisibilityType: visibilityType,
    }),
    onFinish: () => {
      mutate(unstable_serialize(getChatHistoryPaginationKey));
    },
    onError: (error) => {
      if (error instanceof ChatSDKError) {
        toast({
          type: 'error',
          description: error.message,
        });
      }
    },
  });

  // 自定义handleSubmit函数，添加用户角色和会话ID
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    try {
      // 准备请求数据
      const userMessage = { 
        role: 'user' as const, 
        content: input,
        id: generateUUID(),
        createdAt: new Date(),
      };
      
      // 清空输入框
      setInput('');
      
      // 将用户消息添加到UI
      setMessages((prev) => [...prev, userMessage]);
      
      // 设置加载状态为true
      setIsLoading(true);
      
      // 直接使用fetch发送到后端的聊天API
      const response = await fetch('/api/direct-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages.concat(userMessage),
          user_role: userRole,
          session_id: sessionId
        }),
      });
      
      const data = await response.json();
      
      // 设置加载状态为false
      setIsLoading(false);
      
      if (response.ok) {
        // 保存会话ID
        setSessionId(data.session_id);
        
        // 添加机器人回复到消息列表
        setMessages((prev) => [
          ...prev, 
          { 
            role: 'assistant', 
            content: data.response,
            id: generateUUID(),
            createdAt: new Date()
          }
        ]);
      } else {
        // 错误处理
        toast({
          type: 'error',
          description: data.error || 'Failed to process your request',
        });
      }
    } catch (error) {
      // 错误时也需要关闭加载状态
      setIsLoading(false);
      console.error('Error sending message:', error);
      toast({
        type: 'error',
        description: 'Failed to connect to the server',
      });
    }
  };

  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  const [hasAppendedQuery, setHasAppendedQuery] = useState(false);

  useEffect(() => {
    if (query && !hasAppendedQuery) {
      append({
        role: 'user',
        content: query,
      });

      setHasAppendedQuery(true);
      window.history.replaceState({}, '', `/chat/${id}`);
    }
  }, [query, append, hasAppendedQuery, id]);

  const { data: votes } = useSWR<Array<Vote>>(
    messages.length >= 2 ? `/api/vote?chatId=${id}` : null,
    fetcher,
  );

  const [attachments, setAttachments] = useState<Array<Attachment>>([]);
  const isArtifactVisible = useArtifactSelector((state) => state.isVisible);

  useAutoResume({
    autoResume,
    initialMessages,
    experimental_resume,
    data,
    setMessages,
  });

  // 当角色改变时，更新欢迎消息
  const handleRoleChange = (newRole: UserRole) => {
    setUserRole(newRole);
    setSessionId(null);
    
    let greeting = "Hello! I'm your workplace wellness assistant.";
    
    if (newRole === "employee") {
      greeting += " How can I support your wellbeing today?";
    } else if (newRole === "hr_manager") {
      greeting += " How can I help you manage workplace wellness policies and programs?";
    } else if (newRole === "employer") {
      greeting += " How can I help you with organization-level wellness insights?";
    }
    
    // 重置消息列表，只保留欢迎消息
    setMessages([
      { 
        role: 'assistant',
        content: greeting,
        id: generateUUID(),
        createdAt: new Date()
      }
    ]);
  };

  return (
    <>
      <div className="flex flex-col min-w-0 h-dvh bg-background">
        <ChatHeader
          chatId={id}
          selectedModelId={initialChatModel}
          selectedVisibilityType={initialVisibilityType}
          isReadonly={isReadonly}
          session={session}
          onRoleChange={handleRoleChange}
        />

        <Messages
          chatId={id}
          status={isLoading ? 'submitted' : status}
          votes={votes}
          messages={messages}
          setMessages={setMessages}
          reload={reload}
          isReadonly={isReadonly}
          isArtifactVisible={isArtifactVisible}
        />

        <form onSubmit={handleSubmit} className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
          {!isReadonly && (
            <MultimodalInput
              chatId={id}
              input={input}
              setInput={setInput}
              handleSubmit={handleSubmit}
              status={isLoading ? 'submitted' : status}
              stop={stop}
              attachments={attachments}
              setAttachments={setAttachments}
              messages={messages}
              setMessages={setMessages}
              append={append}
              selectedVisibilityType={visibilityType}
            />
          )}
        </form>
      </div>

      {isArtifactVisible && <Artifact />}
    </>
  );
}
