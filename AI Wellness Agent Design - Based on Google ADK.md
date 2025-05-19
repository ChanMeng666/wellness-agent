# AI Wellness Agent Design - Based on Google ADK

Based on the user stories from User-Journey.md and following Google ADK architecture patterns, here's a comprehensive design for your AI Wellness Agent that serves employees, HR managers, and employers while maintaining privacy.

## System Architecture

```mermaid
graph TD
    User[User Interface] --> API[API Gateway]
    API --> Auth[Authentication & Authorization]
    Auth --> WellnessAgent[Root Wellness Agent]
    WellnessAgent --> EmployeeAgent[Employee Support Agent]
    WellnessAgent --> HRAgent[HR Manager Agent]
    WellnessAgent --> EmployerAgent[Employer Insights Agent]
    
    EmployeeAgent --> SymptomTracker[Symptom Tracking Tool]
    EmployeeAgent --> WellnessTips[Wellness Tips Tool]
    EmployeeAgent --> LeaveRequests[Leave Request Tool]
    
    HRAgent --> PolicyManager[Policy Management Tool]
    HRAgent --> TrendAnalyzer[Anonymous Trend Analysis Tool]
    HRAgent --> RequestManager[Request Management Tool]
    
    EmployerAgent --> ROICalculator[Wellness ROI Tool]
    EmployerAgent --> ForecastTool[Workforce Forecast Tool]
    EmployerAgent --> ReportGenerator[Report Generator Tool]
    
    subgraph "Data Layer"
    DB[(Database)]
    AnonymizedDB[(Anonymized Analytics)]
    end
    
    SymptomTracker --> DB
    WellnessTips --> DB
    LeaveRequests --> DB
    PolicyManager --> DB
    RequestManager --> DB
    
    DB --> AnonymizedDB
    TrendAnalyzer --> AnonymizedDB
    ROICalculator --> AnonymizedDB
    ForecastTool --> AnonymizedDB
    ReportGenerator --> AnonymizedDB
```

## User Flow

```mermaid
sequenceDiagram
    participant Employee
    participant HR as HR Manager
    participant Employer
    participant Agent as Wellness Agent
    participant DB as Database
    
    Note over Employee,DB: Employee Journey
    
    Employee->>Agent: Onboarding (minimal health data)
    Agent->>DB: Create user profile (privacy-focused)
    Employee->>Agent: Daily check-in
    Agent->>DB: Log symptoms & metrics
    Employee->>Agent: Request accommodation
    Agent->>DB: Record request
    Agent->>HR: Notify (anonymous if preferred)
    Agent->>Employee: Suggest wellness tips
    Employee->>Agent: View personal trends
    Agent->>Employee: Display personalized dashboard
    
    Note over HR,DB: HR Manager Journey
    
    HR->>Agent: Configure company policies
    Agent->>DB: Store company settings
    HR->>Agent: Review anonymous trend data
    Agent->>HR: Display anonymized insights
    HR->>Agent: Manage accommodation requests
    Agent->>DB: Update request status
    Agent->>Employee: Notify of request status
    HR->>Agent: Request policy recommendations
    Agent->>HR: Suggest policy improvements
    
    Note over Employer,DB: Employer Journey
    
    Employer->>Agent: View organizational metrics
    Agent->>Employer: Display anonymized dashboard
    Employer->>Agent: Request ROI analysis
    Agent->>Employer: Present wellness program ROI
    Employer->>Agent: Request staffing forecast
    Agent->>Employer: Display workforce projections
```

## Database Schema

```mermaid
erDiagram
    USERS {
        string user_id PK
        string role "employee|hr|employer"
        string email
        string name
        json preferences
        timestamp created_at
    }
    
    EMPLOYEE_PROFILES {
        string profile_id PK
        string user_id FK
        json privacy_settings
        timestamp created_at
    }
    
    SYMPTOM_LOGS {
        string log_id PK
        string profile_id FK
        timestamp date
        json symptom_data
        int severity_level
        string notes
    }
    
    ACCOMMODATION_REQUESTS {
        string request_id PK
        string profile_id FK
        string type "remote|time_off|flexible"
        string status "pending|approved|denied"
        date request_date
        date start_date
        date end_date
        string notes
        string anonymity_level
    }
    
    COMPANY_POLICIES {
        string policy_id PK
        string organization_id FK
        string name
        string description
        json details
        timestamp updated_at
    }
    
    ORGANIZATIONS {
        string organization_id PK
        string name
        json settings
        timestamp created_at
    }
    
    ANONYMIZED_METRICS {
        string metric_id PK
        string organization_id FK
        timestamp period_start
        timestamp period_end
        json aggregated_data
        int employee_count
    }
    
    USERS ||--o{ EMPLOYEE_PROFILES : has
    EMPLOYEE_PROFILES ||--o{ SYMPTOM_LOGS : records
    EMPLOYEE_PROFILES ||--o{ ACCOMMODATION_REQUESTS : makes
    ORGANIZATIONS ||--o{ COMPANY_POLICIES : defines
    ORGANIZATIONS ||--o{ ANONYMIZED_METRICS : generates
```

## UI/UX Design

### Employee Dashboard

```mermaid
graph TD
    subgraph "Employee Dashboard"
        A[Quick Check-in]
        B[Symptom Tracker]
        C[Time-off Requests]
        D[Wellness Tips]
        E[Personal Trends]
        F[Privacy Settings]
    end
    
    style A fill:#f9d5e5,stroke:#333,stroke-width:2px
    style B fill:#eeac99,stroke:#333,stroke-width:2px
    style C fill:#e06377,stroke:#333,stroke-width:2px
    style D fill:#c83349,stroke:#333,stroke-width:2px
    style E fill:#5b9aa0,stroke:#333,stroke-width:2px
    style F fill:#d6e1c7,stroke:#333,stroke-width:2px
```

Key UX Principles:
- Quick emoji-based check-ins
- Non-judgmental language
- One-click accommodation requests
- Emphasis on privacy controls
- Focus on self-care and agency

### HR Manager Dashboard

```mermaid
graph TD
    subgraph "HR Manager Dashboard"
        A[Policy Management]
        B[Anonymous Trends]
        C[Request Management]
        D[Impact Metrics]
        E[Recommendation Engine]
    end
    
    style A fill:#d6e1c7,stroke:#333,stroke-width:2px
    style B fill:#5b9aa0,stroke:#333,stroke-width:2px
    style C fill:#c83349,stroke:#333,stroke-width:2px
    style D fill:#e06377,stroke:#333,stroke-width:2px
    style E fill:#eeac99,stroke:#333,stroke-width:2px
```

Key UX Principles:
- Anonymized data visualization
- Automated request handling
- Compliance checks built-in
- Evidence-based recommendations
- Privacy-first design

### Employer Dashboard

```mermaid
graph TD
    subgraph "Employer Dashboard"
        A[Organizational Health]
        B[ROI Analysis]
        C[Workforce Planning]
        D[Policy Effectiveness]
        E[Manager Resources]
    end
    
    style A fill:#5b9aa0,stroke:#333,stroke-width:2px
    style B fill:#e06377,stroke:#333,stroke-width:2px
    style C fill:#eeac99,stroke:#333,stroke-width:2px
    style D fill:#d6e1c7,stroke:#333,stroke-width:2px
    style E fill:#f9d5e5,stroke:#333,stroke-width:2px
```

Key UX Principles:
- Zero PII exposure
- ROI visualization
- Forecast modeling
- Culture-building resources
- Manager conversation guides

## Agent Structure

```mermaid
graph TD
    subgraph "Root Wellness Agent"
        A[Router & Coordinator]
    end
    
    subgraph "Employee Support Agent"
        B1[Symptom Tracking Sub-agent]
        B2[Wellness Recommendation Sub-agent]
        B3[Request Management Sub-agent]
        B4[Trend Analysis Sub-agent]
    end
    
    subgraph "HR Manager Agent"
        C1[Policy Management Sub-agent]
        C2[Anonymous Insight Sub-agent]
        C3[Request Processing Sub-agent]
        C4[Recommendation Sub-agent]
    end
    
    subgraph "Employer Insights Agent"
        D1[ROI Analysis Sub-agent]
        D2[Workforce Forecasting Sub-agent]
        D3[Culture Support Sub-agent]
    end
    
    A --> B1
    A --> B2
    A --> B3
    A --> B4
    A --> C1
    A --> C2
    A --> C3
    A --> C4
    A --> D1
    A --> D2
    A --> D3
```

## Privacy Architecture

```mermaid
graph TD
    Data[Raw User Data] --> PII[PII Identification]
    PII --> Consent[Consent Manager]
    Consent --> Processing[Data Processing]
    Processing --> Anonymization[Anonymization Engine]
    Processing --> Encrypted[Encrypted Personal Storage]
    Anonymization --> Aggregation[Aggregation Service]
    Aggregation --> Analytics[Analytics Database]
    
    subgraph "Employee Access Only"
        Encrypted
    end
    
    subgraph "HR & Employer Access"
        Analytics
    end
```

## Implementation Plan Using ADK

1. **Setup Environment & Install ADK**
   - Create virtual environment
   - Install google-adk
   - Set up project structure

2. **Build Core Agent Components**
   - Define root_agent and sub-agents
   - Create tools for each functionality
   - Set up callbacks for privacy protection

3. **Develop Database & Storage Layer**
   - Set up secure databases
   - Implement anonymization pipeline
   - Create memory and artifact management

4. **Create User Interfaces**
   - Implement employee dashboard
   - Develop HR manager interface
   - Build employer analytics dashboard

5. **Test & Evaluate**
   - Create evaluation datasets
   - Run local tests using `adk api_server`
   - Perform privacy audits

6. **Deploy & Monitor**
   - Deploy to Agent Engine or Cloud Run
   - Implement monitoring system
   - Set up continuous evaluation

## Tech Stack Recommendations

- **Backend**: Google ADK with Python
- **Database**: Firestore for structured data
- **Analytics**: BigQuery for anonymized analytics
- **Frontend**: React with Material UI
- **Authentication**: Firebase Auth
- **Deployment**: Google Cloud (Agent Engine or Cloud Run)
- **Privacy**: Differential privacy libraries
- **Notifications**: Firebase Cloud Messaging