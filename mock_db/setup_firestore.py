#!/usr/bin/env python3
"""
Setup script for creating mock data in Firestore for wellness agent testing.
This creates employees, departments, leave requests, and health trends data.
"""

from google.cloud import firestore
import datetime
import random
import uuid
import os
import json

# Initialize Firestore client
db = firestore.Client()

def create_employee_profiles():
    """Create mock employee profiles"""
    print("Creating employee profiles...")
    collection = db.collection("employee_profiles")
    
    departments = ["Engineering", "Marketing", "Operations", "Sales", "HR", "Finance"]
    titles = {
        "Engineering": ["Software Engineer", "DevOps Engineer", "QA Engineer", "Engineering Manager"],
        "Marketing": ["Marketing Specialist", "Content Creator", "Marketing Manager", "SEO Specialist"],
        "Operations": ["Operations Analyst", "Operations Manager", "Logistics Coordinator"],
        "Sales": ["Sales Representative", "Account Manager", "Sales Director"],
        "HR": ["HR Specialist", "Recruiter", "HR Manager", "Benefits Coordinator"],
        "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Payroll Specialist"]
    }
    
    # Create ~450 employees (as mentioned in the conversation)
    for i in range(450):
        emp_id = f"EMP{i+1:03d}"
        department = random.choice(departments)
        
        # Create employee with anonymous health data
        employee = {
            "employee_id": emp_id,
            "department": department,
            "title": random.choice(titles[department]),
            "join_date": datetime.datetime(
                random.randint(2010, 2024), 
                random.randint(1, 12), 
                random.randint(1, 28)
            ),
            "privacy_level": random.choice(["high", "medium", "low"]),
            "demographic": {
                "age_range": random.choice(["20-30", "30-40", "40-50", "50+"]),
                "remote_eligible": random.choice([True, False]),
            },
            "wellness": {
                "stress_level": random.randint(1, 10),
                "work_life_balance": random.randint(1, 10),
                "job_satisfaction": random.randint(1, 10),
                "physical_activity": random.choice(["Low", "Moderate", "High"]),
                "wellness_program_participation": random.choice([True, False]),
            }
        }
        
        collection.document(emp_id).set(employee)
    
    print(f"Created {450} employee profiles")

def create_department_stats():
    """Create aggregated department statistics"""
    print("Creating department statistics...")
    collection = db.collection("department_stats")
    
    departments = ["Engineering", "Marketing", "Operations", "Sales", "HR", "Finance", "Company-wide"]
    
    current_month = datetime.datetime.now().replace(day=1)
    
    # Create 12 months of data for each department
    for dept in departments:
        for i in range(12):
            month_date = current_month - datetime.timedelta(days=30*i)
            month_str = month_date.strftime("%Y-%m")
            
            # Higher for some departments to create trends
            base_leave_rate = {
                "Engineering": 0.05,
                "Marketing": 0.04,
                "Operations": 0.08,
                "Sales": 0.03,
                "HR": 0.04,
                "Finance": 0.03,
                "Company-wide": 0.05
            }
            
            # Create seasonal variations
            seasonal_factor = 1.0
            if month_date.month in [12, 1]:  # Winter holidays
                seasonal_factor = 1.3
            elif month_date.month in [7, 8]:  # Summer vacation
                seasonal_factor = 1.4
            
            leave_rate = base_leave_rate[dept] * seasonal_factor
            
            # Create department stats document
            stats = {
                "department": dept,
                "month": month_str,
                "date": month_date,
                "metrics": {
                    "headcount": random.randint(50, 100) if dept != "Company-wide" else 450,
                    "leave_rate": leave_rate,
                    "avg_leave_days": random.uniform(1.5, 4.5),
                    "wellness_program_participation_rate": random.uniform(0.3, 0.7),
                    "reported_stress_level": random.uniform(4.0, 7.5),
                    "job_satisfaction": random.uniform(6.0, 8.5),
                }
            }
            
            # Add some department-specific trends
            if dept == "Operations":
                stats["metrics"]["reported_stress_level"] += 1.0  # Higher stress
            elif dept == "Sales":
                stats["metrics"]["job_satisfaction"] += 0.5  # Higher satisfaction
            
            doc_id = f"{dept}-{month_str}"
            collection.document(doc_id).set(stats)
    
    print(f"Created department statistics for {len(departments)} departments over 12 months")

def create_leave_requests():
    """Create anonymized leave request data"""
    print("Creating leave requests...")
    collection = db.collection("leave_requests")
    
    leave_types = [
        "Vacation", 
        "Sick Leave", 
        "Personal Leave", 
        "Family Emergency",
        "Medical Appointment",
        "Mental Health Day",
        "Bereavement",
        "Jury Duty"
    ]
    
    departments = ["Engineering", "Marketing", "Operations", "Sales", "HR", "Finance"]
    
    # Create ~300 leave requests
    for i in range(300):
        request_id = str(uuid.uuid4())
        department = random.choice(departments)
        
        # Randomize dates within last 6 months
        today = datetime.datetime.now()
        request_date = today - datetime.timedelta(days=random.randint(0, 180))
        
        leave_type = random.choice(leave_types)
        duration = 1
        if leave_type in ["Vacation", "Personal Leave"]:
            duration = random.randint(1, 10)
        elif leave_type in ["Sick Leave", "Family Emergency", "Bereavement"]:
            duration = random.randint(1, 5)
        
        # Create anonymized leave request
        leave_request = {
            "request_id": request_id,
            "department": department,
            "request_date": request_date,
            "leave_type": leave_type,
            "duration_days": duration,
            "status": random.choice(["Approved", "Pending", "Rejected"]),
            # Note: No employee identifying information
        }
        
        collection.document(request_id).set(leave_request)
    
    print(f"Created {300} anonymized leave requests")

def create_health_trends():
    """Create aggregated health trend data"""
    print("Creating health trends...")
    collection = db.collection("health_trends")
    
    trend_types = [
        "stress_levels", 
        "work_life_balance", 
        "physical_activity",
        "wellness_program_effectiveness"
    ]
    
    current_month = datetime.datetime.now().replace(day=1)
    
    # Create 12 months of trend data
    for trend in trend_types:
        for i in range(12):
            month_date = current_month - datetime.timedelta(days=30*i)
            month_str = month_date.strftime("%Y-%m")
            
            # Base metrics with slight randomization
            metrics = {
                "company_average": round(random.uniform(6.0, 7.5), 2),
                "department_breakdown": {
                    "Engineering": round(random.uniform(5.5, 7.0), 2),
                    "Marketing": round(random.uniform(6.0, 7.5), 2),
                    "Operations": round(random.uniform(5.0, 6.5), 2),
                    "Sales": round(random.uniform(6.5, 8.0), 2),
                    "HR": round(random.uniform(6.0, 7.5), 2),
                    "Finance": round(random.uniform(5.5, 7.0), 2),
                }
            }
            
            # Add demographic breakdown
            metrics["demographic_breakdown"] = {
                "age_ranges": {
                    "20-30": round(random.uniform(5.5, 7.0), 2),
                    "30-40": round(random.uniform(6.0, 7.5), 2),
                    "40-50": round(random.uniform(5.5, 7.0), 2),
                    "50+": round(random.uniform(5.0, 6.5), 2),
                },
                "remote_vs_office": {
                    "remote": round(random.uniform(6.5, 8.0), 2),
                    "office": round(random.uniform(5.5, 7.0), 2),
                }
            }
            
            # Create health trend document
            trend_data = {
                "trend_type": trend,
                "month": month_str,
                "date": month_date,
                "metrics": metrics,
                "insights": [
                    "Anonymized trend data for company-wide wellness monitoring",
                    f"No individual employee data is exposed in these metrics"
                ]
            }
            
            doc_id = f"{trend}-{month_str}"
            collection.document(doc_id).set(trend_data)
    
    print(f"Created health trends for {len(trend_types)} metrics over 12 months")

def create_wellness_programs():
    """Create wellness program data"""
    print("Creating wellness programs...")
    collection = db.collection("wellness_programs")
    
    programs = [
        {
            "name": "Fitness Challenge",
            "description": "Monthly fitness challenges with rewards for participation",
            "start_date": datetime.datetime(2024, 1, 1),
            "end_date": datetime.datetime(2024, 12, 31),
            "participation_rate": 0.45,
            "satisfaction_score": 8.2,
            "status": "Active"
        },
        {
            "name": "Mental Health Webinars",
            "description": "Bi-weekly webinars on stress management and mental wellness",
            "start_date": datetime.datetime(2024, 2, 15),
            "end_date": datetime.datetime(2024, 11, 30),
            "participation_rate": 0.32,
            "satisfaction_score": 7.8,
            "status": "Active"
        },
        {
            "name": "Ergonomic Assessments",
            "description": "Workstation assessments to prevent musculoskeletal issues",
            "start_date": datetime.datetime(2023, 10, 1),
            "end_date": datetime.datetime(2024, 3, 31),
            "participation_rate": 0.75,
            "satisfaction_score": 8.5,
            "status": "Completed"
        },
        {
            "name": "Wellness App Subscription",
            "description": "Company-sponsored subscription to wellness app",
            "start_date": datetime.datetime(2024, 1, 1),
            "end_date": datetime.datetime(2024, 12, 31),
            "participation_rate": 0.38,
            "satisfaction_score": 6.9,
            "status": "Active"
        },
        {
            "name": "Health Screening Days",
            "description": "On-site health screenings and assessments",
            "start_date": datetime.datetime(2024, 6, 1),
            "end_date": datetime.datetime(2024, 6, 30),
            "participation_rate": 0.0,
            "satisfaction_score": 0.0,
            "status": "Scheduled"
        }
    ]
    
    for program in programs:
        doc_id = program["name"].lower().replace(" ", "_")
        collection.document(doc_id).set(program)
    
    print(f"Created {len(programs)} wellness programs")

if __name__ == "__main__":
    print("Setting up mock data in Firestore...")
    
    create_employee_profiles()
    create_department_stats()
    create_leave_requests()
    create_health_trends()
    create_wellness_programs()
    
    print("Mock data setup complete!") 