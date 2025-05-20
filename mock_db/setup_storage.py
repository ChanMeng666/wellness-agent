#!/usr/bin/env python3
"""
Setup script for creating sample files in Cloud Storage Bucket for wellness agent testing.
This creates wellness resources, policy documents, and aggregated reports.
"""

from google.cloud import storage
import json
import os
import tempfile
import csv
import io

# Initialize Storage client
storage_client = storage.Client()

# Define your bucket name - update this to match your actual bucket name
BUCKET_NAME = "wellness-agent-resources"

def ensure_bucket_exists():
    """Ensure the bucket exists, create if it doesn't"""
    try:
        bucket = storage_client.get_bucket(BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} already exists")
    except Exception:
        print(f"Creating bucket {BUCKET_NAME}...")
        bucket = storage_client.create_bucket(BUCKET_NAME)
    
    return bucket

def upload_string_to_blob(bucket, destination_blob_name, content, content_type="text/plain"):
    """Upload a string to a blob"""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(content, content_type=content_type)
    print(f"Uploaded to {destination_blob_name}")

def create_wellness_resources(bucket):
    """Create wellness resources files"""
    print("Creating wellness resources...")
    
    # Create directory structure
    directories = [
        "wellness_guides/",
        "wellness_guides/mental_health/",
        "wellness_guides/physical_health/",
        "wellness_guides/work_life_balance/",
        "policy_documents/",
        "aggregated_reports/"
    ]
    
    for directory in directories:
        # Create empty file to ensure directory exists
        upload_string_to_blob(bucket, f"{directory}.keep", "")
    
    # Create wellness guides
    mental_health_guide = """# Mental Health Guide for Employees

## Understanding Mental Health in the Workplace

Mental health affects how we think, feel, and act. It also helps determine how we handle stress, relate to others, and make choices.

## Common Workplace Mental Health Challenges

- Work-related stress
- Burnout
- Anxiety
- Depression
- Imposter syndrome

## Resources Available to You

- Employee Assistance Program (EAP)
- Mental Health Days
- Confidential Counseling Services
- Stress Management Workshops

## Supporting Your Colleagues

- Recognize the signs
- Listen without judgment
- Respect privacy and confidentiality
- Know how to refer to appropriate resources

## Self-Care Strategies

- Practice mindfulness
- Set boundaries between work and personal life
- Take regular breaks
- Maintain social connections
- Engage in physical activity
"""

    work_life_balance_guide = """# Work-Life Balance Guide

## The Importance of Balance

Maintaining a healthy work-life balance is essential for your physical and mental wellbeing. It helps prevent burnout and increases job satisfaction.

## Setting Boundaries

- Define clear working hours
- Create a dedicated workspace for remote work
- Turn off notifications after work hours
- Use your vacation time

## Time Management Techniques

- Prioritize tasks
- Use the Pomodoro technique
- Schedule breaks throughout the day
- Plan your week in advance

## Flexible Work Options

- Remote work opportunities
- Flexible hours
- Compressed workweeks
- Part-time schedules

## Supporting Your Team's Balance

- Respect others' time boundaries
- Model healthy work habits
- Encourage use of vacation time
- Check in on workload management
"""

    remote_work_guide = """# Remote Work Best Practices

## Setting Up Your Workspace

- Choose a dedicated space
- Ensure proper ergonomics
- Manage lighting and noise
- Secure reliable internet connection

## Communication Guidelines

- Set clear availability hours
- Use appropriate communication channels
- Schedule regular check-ins
- Be proactive in updates

## Maintaining Productivity

- Follow a routine
- Use time-blocking techniques
- Take regular breaks
- Set daily goals

## Staying Connected

- Participate in virtual team events
- Use video for important meetings
- Schedule informal catch-ups
- Share accomplishments

## Security Considerations

- Use secure connections
- Follow company data policies
- Keep software updated
- Report security concerns promptly
"""

    upload_string_to_blob(bucket, "wellness_guides/mental_health/mental_health_guide.md", mental_health_guide)
    upload_string_to_blob(bucket, "wellness_guides/work_life_balance/work_life_balance_guide.md", work_life_balance_guide)
    upload_string_to_blob(bucket, "wellness_guides/remote_work_guide.md", remote_work_guide)

def create_policy_documents(bucket):
    """Create policy document files"""
    print("Creating policy documents...")
    
    leave_policy = """# Company Leave Policy

## Types of Leave

### Vacation Leave
- Full-time employees: 15 days per year
- Part-time employees: Prorated based on hours worked
- Accrual: 1.25 days per month
- Maximum carry-over: 5 days

### Sick Leave
- Full-time employees: 10 days per year
- Part-time employees: Prorated based on hours worked
- Doctor's note required for absences exceeding 3 consecutive days

### Mental Health Days
- All employees: 3 days per year
- No advance notice required
- Confidential tracking separate from regular sick leave

### Parental Leave
- Birthing parents: 12 weeks paid
- Non-birthing parents: 6 weeks paid
- Additional unpaid leave available upon request

### Bereavement Leave
- Immediate family: 5 days paid
- Extended family: 3 days paid

## Requesting Leave
1. Submit request through the HR portal
2. Provide at least 2 weeks notice for planned absences
3. For unexpected absences, notify manager as soon as possible

## Privacy Considerations
- Health-related leave reasons are confidential
- Only HR has access to medical documentation
- Aggregated leave data may be used for planning purposes
"""

    accommodation_policy = """# Workplace Accommodations Policy

## Purpose
This policy outlines the process for requesting and implementing reasonable accommodations for employees with disabilities or health conditions.

## Eligibility
All employees who have a physical or mental impairment that substantially limits one or more major life activities.

## Types of Accommodations
- Modified work schedules
- Ergonomic equipment
- Remote work arrangements
- Accessible technology
- Physical workspace modifications
- Job restructuring

## Request Process
1. Employee submits accommodation request to HR
2. Interactive dialogue between employee, HR, and manager
3. Medical documentation may be requested (maintained confidentially)
4. Decision within 10 business days
5. Implementation plan developed
6. Regular check-ins to ensure effectiveness

## Confidentiality
- All medical information is kept strictly confidential
- Information shared only on need-to-know basis
- Records maintained separately from personnel files

## Appeal Process
If a request is denied, employees may appeal within 5 business days to the Chief People Officer.
"""

    remote_work_policy = """# Remote Work Policy

## Eligibility
- Minimum 3 months employment
- Role compatibility assessment
- Manager approval required
- Performance in good standing

## Equipment and Setup
- Company-provided laptop
- Stipend for home office setup: $300
- Personal internet connection required
- VPN access for secure connections

## Work Expectations
- Core hours: 10am-3pm local time
- Regular availability on communication platforms
- Daily check-ins with team
- Weekly progress reports
- Attendance at virtual team meetings

## Security Requirements
- Secure home network
- Regular software updates
- Password-protected devices
- No public WiFi for company business
- Report security incidents immediately

## Evaluation Process
- 30-day trial period
- Quarterly performance reviews
- Productivity and quality metrics
- Communication effectiveness assessment
- Arrangement subject to review and modification

## Termination of Arrangement
The company reserves the right to terminate remote work arrangements if:
- Business needs change
- Performance issues arise
- Security concerns emerge
- Communication problems persist
"""

    upload_string_to_blob(bucket, "policy_documents/leave_policy.md", leave_policy)
    upload_string_to_blob(bucket, "policy_documents/accommodation_policy.md", accommodation_policy)
    upload_string_to_blob(bucket, "policy_documents/remote_work_policy.md", remote_work_policy)

def create_aggregated_reports(bucket):
    """Create aggregated reports files"""
    print("Creating aggregated reports...")
    
    # Annual wellness report in JSON format
    annual_wellness_report = {
        "report_title": "Annual Wellness Program Assessment",
        "year": 2024,
        "executive_summary": [
            "Overall wellness program participation increased by 12% compared to previous year",
            "Mental health resources were the most utilized category",
            "Departments with flexible schedules showed 15% lower reported stress levels",
            "ROI on wellness initiatives estimated at 1.5x program costs through reduced absenteeism"
        ],
        "participation_metrics": {
            "overall_participation_rate": 0.68,
            "participation_by_department": {
                "Engineering": 0.72,
                "Marketing": 0.65,
                "Operations": 0.58,
                "Sales": 0.62,
                "HR": 0.88,
                "Finance": 0.61
            },
            "program_utilization": {
                "fitness_challenges": 0.45,
                "mental_health_resources": 0.53,
                "nutrition_programs": 0.38,
                "wellness_seminars": 0.42,
                "health_screenings": 0.76
            }
        },
        "health_metrics": {
            "average_stress_levels": {
                "q1": 6.8,
                "q2": 6.5,
                "q3": 6.2,
                "q4": 6.0
            },
            "work_life_balance_satisfaction": {
                "q1": 6.9,
                "q2": 7.1,
                "q3": 7.3,
                "q4": 7.4
            },
            "physical_activity_levels": {
                "low": 0.25,
                "moderate": 0.45,
                "high": 0.30
            }
        },
        "business_impact": {
            "absenteeism_reduction": 0.18,
            "turnover_reduction": 0.12,
            "productivity_improvement": 0.08,
            "healthcare_cost_reduction": 0.07
        },
        "recommendations": [
            "Expand mental health resources based on high utilization",
            "Target programs for Operations department which shows lowest participation",
            "Increase manager training on supporting team wellness",
            "Implement quarterly wellness challenges instead of annual",
            "Develop metrics to better track productivity impacts"
        ]
    }
    
    # Leave trends CSV
    leave_trends_csv = """month,total_leave_days,sick_leave_percent,vacation_percent,personal_leave_percent,mental_health_percent
2023-06,253,22,65,10,3
2023-07,312,18,72,8,2
2023-08,345,15,77,6,2
2023-09,201,25,62,9,4
2023-10,187,30,55,10,5
2023-11,194,32,52,11,5
2023-12,287,28,58,9,5
2024-01,265,35,50,9,6
2024-02,198,38,47,8,7
2024-03,210,30,54,9,7
2024-04,222,27,56,10,7
2024-05,248,24,59,10,7
"""

    # Department wellness metrics CSV
    department_metrics_csv = """department,avg_stress_level,wellness_participation,leave_rate,job_satisfaction
Engineering,6.5,72%,5.2%,7.1
Marketing,6.2,65%,4.8%,7.5
Operations,7.8,58%,8.1%,6.2
Sales,6.7,62%,3.9%,7.8
HR,5.9,88%,4.5%,8.2
Finance,6.8,61%,3.8%,7.0
"""

    upload_string_to_blob(bucket, "aggregated_reports/annual_wellness_report.json", json.dumps(annual_wellness_report, indent=2), content_type="application/json")
    upload_string_to_blob(bucket, "aggregated_reports/leave_trends.csv", leave_trends_csv, content_type="text/csv")
    upload_string_to_blob(bucket, "aggregated_reports/department_wellness_metrics.csv", department_metrics_csv, content_type="text/csv")

if __name__ == "__main__":
    print(f"Setting up sample files in bucket {BUCKET_NAME}...")
    
    bucket = ensure_bucket_exists()
    create_wellness_resources(bucket)
    create_policy_documents(bucket)
    create_aggregated_reports(bucket)
    
    print("Sample files setup complete!") 