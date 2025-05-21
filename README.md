# Wellness Support Agent

A comprehensive workplace wellness agent built with Google's Agent Development Kit (ADK) that supports employees, HR managers, and employers with privacy-focused tools.

## Project Overview

This agent aims to create a more supportive, inclusive workplace by helping:
- **Employees** track symptoms, get wellness tips, and request accommodations
- **HR Managers** analyze anonymous trends, manage accommodations, and develop policies  
- **Employers** calculate ROI, forecast workforce impacts, and improve culture

All while maintaining strict privacy controls and data protections.

## Features

### For Employees
- Quick, judgment-free symptom tracking
- Workplace-appropriate wellness tips
- Privacy-controlled accommodation requests
- Personal health trend insights
- Personalized experiences through persistent memory

### For HR Managers
- Anonymous wellness trend analysis
- Streamlined accommodation management
- Evidence-based policy suggestions
- Privacy-compliant reporting tools
- Organizational memory for policy continuity

### For Employers
- Wellness ROI calculation
- Workforce impact forecasting
- Culture improvement resources
- Anonymous organizational insights
- Long-term trend memory for strategic planning

## Memory System

The agent includes a robust memory system that enhances user experience while preserving privacy:

- **Persistent User Profiles**: Remembers user preferences, history, and wellness journey
- **Context Retention**: Maintains conversation context between sessions
- **Journey Tracking**: Follows users across their wellness journey with appropriate continuity
- **Privacy-Preserving Storage**: Respects user privacy settings in what is remembered
- **Role-Based Memory**: Different information is stored based on user role and permissions

Memory functions include:
- `memorize()`: Store single key-value pairs
- `memorize_list()`: Append to a list of values under a key
- `forget()`: Remove specific information
- `get_memory()`: Retrieve stored information by key
- `clear_memory_key()`: Erase an entire category of information

## Privacy Focus

This agent was built with privacy at its core:
- Symptom data is private by default
- Anonymized aggregation for organizational insights
- Role-based access controls
- Minimum group sizes for trend reports
- User control over data sharing preferences
- Memory system respects privacy settings

## Installation

1. Clone this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your API keys (see `.env.example`)

## Usage

Run the development UI:
```bash
cd wellness-agent
adk web
```

Or run the CLI interface:
```bash
cd wellness-agent
adk run wellness_agent
```

## Architecture

This agent uses a hierarchical multi-agent system with:
- A root coordinator agent
- Specialized sub-agents for different user roles
- Custom privacy callbacks
- Role-based tool access
- Memory integration across all sub-agents

### Memory Architecture

The memory system is implemented with:
- `shared_libraries/memory.py`: Core memory functions and utilities
- Database integration for persistent storage
- Privacy-aware memory access controls
- Session state management for conversation continuity
- Default profile loading for new users

## Development

To contribute:
1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details. 
