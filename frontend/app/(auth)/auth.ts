import { compare } from 'bcrypt-ts';
import NextAuth, { type DefaultSession } from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import { createGuestUser, getUser } from '@/lib/db/queries';
import { authConfig } from './auth.config';
import { DUMMY_PASSWORD } from '@/lib/constants';
import type { DefaultJWT } from 'next-auth/jwt';

export type UserType = 'guest' | 'regular';

declare module 'next-auth' {
  interface Session extends DefaultSession {
    user: {
      id: string;
      type: UserType;
    } & DefaultSession['user'];
  }

  interface User {
    id?: string;
    email?: string | null;
    type: UserType;
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    id: string;
    type: UserType;
  }
}

// Create a mock user for development
const mockUser = {
  id: 'mock-user-id',
  name: 'Demo User',
  email: 'chanmeng@sanicle.cloud',
  type: 'regular' as UserType,
  image: null
};

// Mock auth for development
export const auth = async () => {
  // Return a dummy session to bypass authentication
  return {
    user: mockUser
  };
};

// Keep these for interface compatibility but they won't be used
export const {
  handlers: { GET, POST },
  signIn,
  signOut,
} = NextAuth({
  ...authConfig,
  providers: [
    Credentials({
      credentials: {},
      async authorize() {
        return mockUser;
      },
    }),
  ],
});
