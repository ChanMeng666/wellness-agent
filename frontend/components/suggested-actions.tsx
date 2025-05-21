'use client';

import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { memo, useState, useEffect } from 'react';
import type { UseChatHelpers } from '@ai-sdk/react';
import type { VisibilityType } from './visibility-selector';
import type { UserRole } from './role-selector';
import { CrossSmallIcon } from './icons';
import { generateUUID } from '@/lib/utils';
import { toast } from './toast';
import type { UIMessage } from 'ai';

interface SuggestedActionsProps {
  chatId: string;
  append?: UseChatHelpers['append']; // Make append optional
  setParentMessages?: UseChatHelpers['setMessages']; // Add prop to update parent messages
  setParentLoading?: (isLoading: boolean) => void; // Add prop to control parent loading state
  selectedVisibilityType: VisibilityType;
  userRole: UserRole;
}

function PureSuggestedActions({
  chatId,
  append,
  setParentMessages,
  setParentLoading,
  selectedVisibilityType,
  userRole,
}: SuggestedActionsProps) {
  // Track loading state
  const [isLoading, setIsLoading] = useState(false);
  // Track current session ID
  const [sessionId, setSessionId] = useState<string | null>(null);
  // Track messages for direct-chat API
  const [messages, setMessages] = useState<any[]>([]);
  
  // 确保没有副作用在组件挂载时运行
  // 所有逻辑只有在用户明确点击推荐问题时才会执行

  // Direct chat API handler
  const handleSuggestedAction = async (content: string) => {
    if (isLoading) return;
    
    try {
      // Set local loading state
      setIsLoading(true);
      
      // Set parent loading state if available
      if (setParentLoading) {
        setParentLoading(true);
      }
      
      // Create user message
      const userMessage = { 
        role: 'user' as const, 
        content,
        id: generateUUID(),
        createdAt: new Date(),
      };
      
      // Update the local state directly instead of using append
      const updatedMessages = [...messages, userMessage];
      setMessages(updatedMessages);
      
      // Add message to parent state right away for immediate UI feedback
      if (setParentMessages) {
        setParentMessages((prev) => [...prev, userMessage as UIMessage]);
      }
      
      // Send to direct-chat API
      const response = await fetch('/api/direct-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: updatedMessages,
          user_role: userRole,
          session_id: sessionId
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Save session ID for subsequent requests
        setSessionId(data.session_id);
        
        // Add bot response to messages
        const assistantMessage = { 
          role: 'assistant', 
          content: data.response,
          id: generateUUID(),
          createdAt: new Date()
        };
        
        setMessages([...updatedMessages, assistantMessage]);
        
        // Add bot response to parent state for UI
        if (setParentMessages) {
          setParentMessages((prev) => [...prev, assistantMessage as UIMessage]);
        } 
        // Only use URL redirect if no parent state management available
        else if (!append) {
          // If no state management available, redirect
          window.location.href = `/chat/${chatId}?message=${encodeURIComponent(content)}&response=${encodeURIComponent(data.response)}`;
        }
        // Removed the append calls to prevent duplicate messages
      } else {
        // Error handling
        toast({
          type: 'error',
          description: data.error || 'Failed to process your request',
        });
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        type: 'error',
        description: 'Failed to connect to the server',
      });
    } finally {
      // Reset local loading state
      setIsLoading(false);
      
      // Reset parent loading state if available
      if (setParentLoading) {
        setParentLoading(false);
      }
    }
  };

  // Employee-specific questions
  const employeeQuestions = [
    {
      title: 'I\'m feeling stressed',
      label: 'what resources are available?',
      action: 'I\'m feeling stressed at work, what resources are available?',
    },
    {
      title: 'How many mental health days',
      label: 'am I entitled to?',
      action: 'How many mental health days am I entitled to?',
    },
    {
      title: 'I want to track',
      label: 'my work-life balance',
      action: 'I want to track my work-life balance',
    },
    {
      title: 'What wellness programs',
      label: 'can I participate in?',
      action: 'What wellness programs can I participate in?',
    },
  ];

  // HR Manager-specific questions
  const hrManagerQuestions = [
    {
      title: 'Which department has',
      label: 'the highest leave rate?',
      action: 'Which department has the highest leave rate?',
    },
    {
      title: 'How effective are',
      label: 'our wellness programs?',
      action: 'How effective are our wellness programs?',
    },
    {
      title: 'What are the stress level trends',
      label: 'across departments?',
      action: 'What are the stress level trends across departments?',
    },
    {
      title: 'Can you show me',
      label: 'our leave policy?',
      action: 'Can you show me our leave policy?',
    },
  ];

  // Employer/Leadership-specific questions
  const employerQuestions = [
    {
      title: 'What\'s the ROI',
      label: 'on our wellness initiatives?',
      action: 'What\'s the ROI on our wellness initiatives?',
    },
    {
      title: 'Compare wellness metrics',
      label: 'across departments',
      action: 'Compare wellness metrics across departments',
    },
    {
      title: 'Show me',
      label: 'the annual wellness report',
      action: 'Show me the annual wellness report',
    },
    {
      title: 'How has employee satisfaction',
      label: 'changed this quarter?',
      action: 'How has employee satisfaction changed this quarter?',
    },
  ];

  // Select the appropriate questions based on the user role
  const suggestedActions = 
    userRole === 'hr_manager' ? hrManagerQuestions :
    userRole === 'employer' ? employerQuestions :
    employeeQuestions;  // Default to employee questions

  return (
    <div className="relative w-full">
      <div
        data-testid="suggested-actions"
        className="grid sm:grid-cols-2 gap-2 w-full"
      >
        {suggestedActions.map((suggestedAction, index) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            transition={{ delay: 0.05 * index }}
            key={`suggested-action-${suggestedAction.title}-${index}`}
            className={index > 1 ? 'hidden sm:block' : 'block'}
          >
            <Button
              variant="ghost"
              onClick={(e) => {
                // 阻止事件冒泡和默认行为
                e.preventDefault();
                e.stopPropagation();
                // 更新URL并发送请求
                window.history.replaceState({}, '', `/chat/${chatId}`);
                handleSuggestedAction(suggestedAction.action);
              }}
              disabled={isLoading}
              className="text-left border rounded-xl px-4 py-3.5 text-sm flex-1 gap-1 sm:flex-col w-full h-auto justify-start items-start"
            >
              <span className="font-medium">{suggestedAction.title}</span>
              <span className="text-muted-foreground">
                {suggestedAction.label}
              </span>
            </Button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export const SuggestedActions = memo(
  PureSuggestedActions,
  (prevProps, nextProps) => {
    if (prevProps.chatId !== nextProps.chatId) return false;
    if (prevProps.selectedVisibilityType !== nextProps.selectedVisibilityType)
      return false;
    if (prevProps.userRole !== nextProps.userRole) return false;

    return true;
  },
);
