# Wellness Agent Testing Guide

This guide provides instructions for setting up mock data and testing the wellness agent with its new data capabilities.

## Prerequisites

Ensure you have:

1. Google Cloud credentials set up and available in your environment
2. Python 3.9+ installed
3. All required packages installed (`pip install -r requirements.txt`)
4. Access to Firestore and Cloud Storage

## Setting Up Mock Data

Before testing, you need to populate Firestore and Cloud Storage with mock data:

```bash
# Run the setup script 
python setup_mock_data.py
```

This will:
1. Create mock employee profiles in Firestore (~450 employees)
2. Set up department statistics for 6 departments over 12 months
3. Generate anonymized leave request data
4. Create health trend data for various metrics 
5. Add wellness program information to Firestore
6. Upload wellness guides, policy documents and reports to Cloud Storage

## Running the Application

Start the development server:

```bash
python run_dev_server.py
```

The server will run by default on `http://localhost:8000`.

## Testing Scenarios

Here are specific test scenarios to verify the agent's data capabilities while respecting privacy:

### HR Manager Scenarios

1. **Department Leave Rate Analysis**
   - Log in as an HR Manager
   - Ask: "Which department has the highest leave rate?"
   - Verify: Agent provides department-level statistics without revealing individual employee data

2. **Wellness Program Effectiveness**
   - Ask: "How effective are our wellness programs?"
   - Verify: Agent provides aggregated program participation and satisfaction metrics

3. **Health Trend Analysis**
   - Ask: "What are the stress level trends across departments?"
   - Verify: Agent provides anonymized trend data with appropriate privacy disclaimers

4. **Policy Information**
   - Ask: "Can you show me our leave policy?"
   - Verify: Agent retrieves and displays the policy document from storage

### Employer/Leadership Scenarios

1. **ROI Analysis**
   - Log in as an Employer
   - Ask: "What's the ROI on our wellness initiatives?"
   - Verify: Agent provides company-wide metrics on business impact without individual data

2. **Department Comparisons**
   - Ask: "Compare wellness metrics across departments"
   - Verify: Agent provides comparative analysis at department level only

3. **Wellness Report**
   - Ask: "Show me the annual wellness report"
   - Verify: Agent retrieves and summarizes the annual wellness report with privacy protection

### Employee Scenarios

1. **Wellness Guide Access**
   - Log in as an Employee
   - Ask: "I'm feeling stressed at work, what resources are available?"
   - Verify: Agent provides appropriate wellness guides and resources

2. **Policy Information**
   - Ask: "How many mental health days am I entitled to?"
   - Verify: Agent retrieves policy information without accessing any personal data

3. **Tracking Personal Goals**
   - Set a wellness goal: "I want to track my work-life balance"
   - Verify: Agent uses memory to remember this preference and doesn't share it with others

## Privacy Testing

For each test scenario, verify that:

1. **No Individual Data**: The agent never reveals individual employee health data
2. **Anonymized Aggregation**: All statistics are properly anonymized and aggregated
3. **Privacy Disclaimers**: The agent mentions privacy protections when sharing data
4. **Role-Based Access**: Different user roles get appropriate levels of data access
5. **Memory Separation**: Personal data stored in memory isn't shared across users

## Troubleshooting

If you encounter issues:

1. **Database Connection**: Ensure your Google Cloud credentials are correctly set up
2. **Missing Data**: Check if the setup script completed successfully
3. **API Errors**: Verify that your Firestore and Cloud Storage resources are accessible
4. **Log Analysis**: Check the server logs for error messages

## Extending the Tests

To add more test scenarios:

1. Add new mock data to the setup scripts
2. Create additional test cases for specific user roles
3. Test edge cases around privacy boundaries
4. Verify cross-role interactions maintain proper data isolation 