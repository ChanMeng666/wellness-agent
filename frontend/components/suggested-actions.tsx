'use client';

import { motion } from 'framer-motion';
import { Button } from './ui/button';
import { memo, useState, useEffect } from 'react';
import type { UseChatHelpers } from '@ai-sdk/react';
import type { VisibilityType } from './visibility-selector';
import type { UserRole } from './role-selector';
import { CrossSmallIcon } from './icons';

interface SuggestedActionsProps {
  chatId: string;
  append: UseChatHelpers['append'];
  selectedVisibilityType: VisibilityType;
  userRole: UserRole;
}

// Key for localStorage to remember if suggestions are hidden
const getSuggestionsHiddenKey = (userRole: UserRole) => `wellness-agent-suggestions-hidden-${userRole}`;

function PureSuggestedActions({
  chatId,
  append,
  selectedVisibilityType,
  userRole,
}: SuggestedActionsProps) {
  // Track whether suggestions are visible
  const [isSuggestionsVisible, setIsSuggestionsVisible] = useState(true);

  // Load hidden preference from localStorage on mount and when userRole changes
  useEffect(() => {
    const hiddenState = localStorage.getItem(getSuggestionsHiddenKey(userRole));
    if (hiddenState === 'true') {
      setIsSuggestionsVisible(false);
    } else {
      setIsSuggestionsVisible(true);
    }
  }, [userRole]);

  // Handle closing the suggestions
  const handleCloseSuggestions = () => {
    setIsSuggestionsVisible(false);
    localStorage.setItem(getSuggestionsHiddenKey(userRole), 'true');
  };
  
  // Handle showing the suggestions again
  const handleShowSuggestions = () => {
    setIsSuggestionsVisible(true);
    localStorage.removeItem(getSuggestionsHiddenKey(userRole));
  };

  // If suggestions are hidden, show a button to display them again
  if (!isSuggestionsVisible) {
    return (
      <div className="flex justify-center w-full mb-4">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleShowSuggestions}
          className="text-sm flex items-center gap-1 px-4 py-2 border-dashed"
        >
          <svg 
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor" 
            strokeWidth="1.5"
            className="mr-1"
          >
            <path d="M8 4V12M4 8H12" strokeLinecap="round" />
          </svg>
          <span>Show suggested questions</span>
        </Button>
      </div>
    );
  }

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
      {/* Close button - redesigned to be more obvious */}
      <div className="flex justify-end w-full mb-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleCloseSuggestions}
          className="text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
        >
          <CrossSmallIcon size={12} />
          <span>Hide suggestions</span>
        </Button>
      </div>
    
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
              onClick={async () => {
                window.history.replaceState({}, '', `/chat/${chatId}`);

                append({
                  role: 'user',
                  content: suggestedAction.action,
                });
              }}
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
