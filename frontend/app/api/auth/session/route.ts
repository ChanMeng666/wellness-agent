export async function GET() {
  // Mock session response that next-auth expects
  return Response.json({
    user: {
      id: 'mock-user-id',
      name: 'Demo User',
      email: 'demo@example.com',
      image: null
    },
    expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString() // 30 days from now
  });
} 