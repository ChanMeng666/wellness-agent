export async function GET() {
  // Mock CSRF token that next-auth expects
  return Response.json({
    csrfToken: "mock-csrf-token"
  });
} 