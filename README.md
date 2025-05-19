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

### For HR Managers
- Anonymous wellness trend analysis
- Streamlined accommodation management
- Evidence-based policy suggestions
- Privacy-compliant reporting tools

### For Employers
- Wellness ROI calculation
- Workforce impact forecasting
- Culture improvement resources
- Anonymous organizational insights

## Privacy Focus

This agent was built with privacy at its core:
- Symptom data is private by default
- Anonymized aggregation for organizational insights
- Role-based access controls
- Minimum group sizes for trend reports
- User control over data sharing preferences

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

## Development

To contribute:
1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details. 