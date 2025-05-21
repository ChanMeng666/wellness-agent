'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useWindowSize } from 'usehooks-ts';
import { useState, useEffect } from 'react';

import { ModelSelector } from '@/components/model-selector';
import { SidebarToggle } from '@/components/sidebar-toggle';
import { Button } from '@/components/ui/button';
import { PlusIcon } from './icons';
import { useSidebar } from './ui/sidebar';
import { memo } from 'react';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { type VisibilityType, VisibilitySelector } from './visibility-selector';
import type { Session } from 'next-auth';
import { RoleSelector, type UserRole } from './role-selector';

// 保存用户角色到localStorage的键名
const USER_ROLE_KEY = 'wellness-agent-user-role';

function PureChatHeader({
  chatId,
  selectedModelId,
  selectedVisibilityType,
  isReadonly,
  session,
  onRoleChange,
}: {
  chatId: string;
  selectedModelId: string;
  selectedVisibilityType: VisibilityType;
  isReadonly: boolean;
  session: Session;
  onRoleChange?: (role: UserRole) => void;
}) {
  const router = useRouter();
  const { open } = useSidebar();
  const { width: windowWidth } = useWindowSize();
  
  // Initialize with a stable value for server-side rendering
  const [selectedRole, setSelectedRole] = useState<UserRole>('employee');
  
  // After component mounts, hydrate with localStorage value if available
  useEffect(() => {
    const savedRole = localStorage.getItem(USER_ROLE_KEY) as UserRole;
    if (savedRole) {
      setSelectedRole(savedRole);
    }
  }, []);
  
  // 当角色变化时保存到localStorage
  useEffect(() => {
    localStorage.setItem(USER_ROLE_KEY, selectedRole);
  }, [selectedRole]);
  
  // 处理角色变化
  const handleRoleChange = (role: UserRole) => {
    setSelectedRole(role);
    if (onRoleChange) {
      onRoleChange(role);
    }
  };

  return (
    <header className="flex sticky top-0 bg-background py-1.5 items-center px-2 md:px-2 gap-2">
      <SidebarToggle />

      {(!open || windowWidth < 768) && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="outline"
              className="order-2 md:order-1 px-3 md:h-fit ml-auto md:ml-0"
              onClick={() => {
                router.push('/');
                router.refresh();
              }}
            >
              <span>New Chat</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>Start a new conversation</TooltipContent>
        </Tooltip>
      )}

      {!isReadonly && (
        <ModelSelector
          session={session}
          selectedModelId={selectedModelId}
          className="order-1 md:order-2"
        />
      )}

      {!isReadonly && (
        <VisibilitySelector
          chatId={chatId}
          selectedVisibilityType={selectedVisibilityType}
          className="order-1 md:order-3"
        />
      )}

      {/* 添加角色选择器 */}
      <RoleSelector
        selectedRole={selectedRole}
        onChange={handleRoleChange}
        className="order-1 md:order-4 md:ml-auto"
      />
    </header>
  );
}

export const ChatHeader = memo(PureChatHeader, (prevProps, nextProps) => {
  return prevProps.selectedModelId === nextProps.selectedModelId;
});
