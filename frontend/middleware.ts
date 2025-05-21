// 此中间件已被禁用，仅保留最小配置以允许应用正常启动
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 空的中间件函数
export function middleware(request: NextRequest) {
  // 不做任何拦截，直接放行所有请求
  return NextResponse.next();
}

// 空的匹配器配置，表示不匹配任何路径
export const config = {
  matcher: [],
};
