export async function POST(request: Request) {
  try {
    // Get the request body
    const body = await request.json();
    
    // 确保包含用户角色信息
    if (!body.user_role) {
      console.error('Missing user_role parameter in request:', body);
      return new Response(
        JSON.stringify({ error: 'Missing user_role parameter' }),
        {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    }
    
    // 格式化消息，确保与wellness-agent API格式兼容
    const formattedBody = {
      messages: body.messages.map((msg: any) => ({
        role: msg.role,
        content: msg.content
      })),
      user_role: body.user_role,
      session_id: body.session_id
    };
    
    // 打印请求信息以便调试
    console.log('Wellness Agent API Request:', JSON.stringify(formattedBody));
    
    // Forward the request to the backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    console.log(`Sending request to backend at ${backendUrl}/api/chat`);
    
    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formattedBody),
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Wellness Agent API Error:', errorText);
        console.error('Status code:', response.status);
        
        // If backend returns an error, fall back to mock response
        console.log('Falling back to mock response due to backend error');
        return createMockResponse(body);
      }
      
      // 获取并记录后端响应
      const data = await response.json();
      console.log('Wellness Agent API Response:', data);
      
      return new Response(JSON.stringify(data), {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (fetchError) {
      // If fetch fails (e.g., backend not available), fall back to mock response
      console.error('Error fetching from backend:', fetchError);
      console.log('Falling back to mock response due to connection error');
      return createMockResponse(body);
    }
  } catch (error: any) {
    console.error('Error in wellness agent API route:', error);
    return new Response(
      JSON.stringify({ 
        error: `Failed to process chat request: ${error.message}`,
        stack: error.stack 
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

// Helper function to create a mock response when backend is unavailable
function createMockResponse(requestBody: any) {
  // Extract the last user message
  const lastUserMessage = requestBody.messages
    .filter((msg: any) => msg.role === 'user')
    .pop()?.content || 'Hello';
  
  // Generate a mock response
  const mockResponse = {
    response: `This is a mock response because the backend server is not available. You said: "${lastUserMessage}". In a real environment, the Wellness Agent would provide a helpful response.`,
    session_id: requestBody.session_id || 'mock-session-123'
  };
  
  return new Response(JSON.stringify(mockResponse), {
    headers: {
      'Content-Type': 'application/json',
    },
  });
} 