'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { CheckIcon } from 'lucide-react';

export type UserRole = 'employee' | 'hr_manager' | 'employer';

// 角色配置
const ROLES = [
  {
    id: 'employee',
    name: 'Employee',
    description: 'For personal wellbeing support'
  },
  {
    id: 'hr_manager',
    name: 'HR Manager',
    description: 'For workplace wellness policies'
  },
  {
    id: 'employer',
    name: 'Employer',
    description: 'For organization-level insights'
  }
];

interface RoleSelectorProps {
  selectedRole: UserRole;
  onChange: (role: UserRole) => void;
  className?: string;
}

export function RoleSelector({ selectedRole, onChange, className = '' }: RoleSelectorProps) {
  // 获取当前选中角色的名称
  const selectedRoleName = ROLES.find(role => role.id === selectedRole)?.name || 'Employee';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className={`flex h-8 items-center gap-1 sm:gap-2 ${className}`}>
          <span>Role: {selectedRoleName}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-[200px]">
        {ROLES.map(role => (
          <DropdownMenuItem
            key={role.id}
            className="flex items-center justify-between"
            onClick={() => onChange(role.id as UserRole)}
          >
            <div className="flex flex-col">
              <span>{role.name}</span>
              <span className="text-xs text-zinc-500">{role.description}</span>
            </div>
            {role.id === selectedRole && <CheckIcon className="h-4 w-4" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 