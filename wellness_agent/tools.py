"""Tools for the Wellness Agent."""

from typing import Dict, List, Optional, Literal, Any, Union
from google.adk.tools import FunctionTool

from wellness_agent.tool_handlers import (
    track_symptom_handler,
    quick_check_in_handler,
    get_wellness_tips_handler,
    request_accommodation_handler,
    view_symptom_history_handler,
    visualize_symptom_trends_handler
)

# ----- Define Function Tools -----

# Employee Tools
track_symptom_tool = FunctionTool(func=track_symptom_handler)
quick_check_in_tool = FunctionTool(func=quick_check_in_handler)
get_wellness_tips_tool = FunctionTool(func=get_wellness_tips_handler)
request_accommodation_tool = FunctionTool(func=request_accommodation_handler)
view_symptom_history_tool = FunctionTool(func=view_symptom_history_handler)
visualize_symptom_trends_tool = FunctionTool(func=visualize_symptom_trends_handler)

# Group Employee tools
EMPLOYEE_TOOLS = [
    track_symptom_tool,
    quick_check_in_tool,
    get_wellness_tips_tool,
    request_accommodation_tool,
    view_symptom_history_tool,
    visualize_symptom_trends_tool
]

# ----- Legacy Tool Handlers (kept for reference) -----
# These will be gradually migrated to the service-based handlers

def update_privacy_settings_handler(
    default_data_retention: Literal["30_days", "90_days", "1_year", "forever"],
    default_anonymization: Literal["high", "medium", "basic"],
    default_sharing_level: Literal["fully_private", "anonymous_only", "shareable"]
) -> Dict[str, Any]:
    """
    Update personal privacy settings for health data.
    
    Args:
        default_data_retention: How long to keep personal health data
        default_anonymization: Level of detail to remove when anonymizing data
        default_sharing_level: Default sharing permission for new health data
        
    Returns:
        A confirmation message and the updated settings
    """
    # This would update user preferences in a database

# ---- HR Tools ----

def view_anonymous_trends_handler(
    trend_type: Literal["symptom_frequency", "accommodation_requests", "wellbeing_scores", "absenteeism"],
    time_period: Literal["week", "month", "quarter", "year"] = "month",
    department: Optional[str] = None
) -> Dict[str, Any]:
    """
    View anonymous trend data for HR planning and policy development.
    
    Args:
        trend_type: The type of trend data to view
        time_period: The time range to analyze
        department: Optional filter for a specific department
        
    Returns:
        Anonymized trend data and insights
    """
    # In a real implementation, this would query anonymized data
    
    department_str = f" in the {department} department" if department else " across all departments"
    
    # Sample insights based on trend type
    insights_by_type = {
        "symptom_frequency": [
            f"Headaches were reported 28% more frequently{department_str} compared to last {time_period}",
            f"Fatigue reports peak on Wednesdays and Thursdays{department_str}",
            f"Focus-related symptoms show strong correlation with project deadline weeks{department_str}"
        ],
        "accommodation_requests": [
            f"Flexible schedule remains the most requested accommodation{department_str}",
            f"Remote work requests have decreased by 12%{department_str} as hybrid policies improved",
            f"Physical workspace modifications show seasonal patterns{department_str}"
        ],
        "wellbeing_scores": [
            f"Overall wellbeing scores improved 8%{department_str} following the new meeting policy",
            f"Employee-reported mood scores dip significantly during quarter-end periods{department_str}",
            f"Teams with flex-time policies show 15% higher average wellbeing scores{department_str}"
        ],
        "absenteeism": [
            f"Unplanned absences decreased 17%{department_str} since implementing the wellness program",
            f"Monday and Friday show similar absence patterns{department_str}, contradicting assumptions",
            f"Departments with flexible scheduling show 22% fewer partial-day absences{department_str}"
        ]
    }
    
    insights = insights_by_type.get(trend_type, [
        "No specific insights available for this trend type.",
        "Consider refining your search parameters."
    ])
    
    # Sample chart data that would be visualized in the UI
    sample_chart_data = {
        "symptom_frequency": {
            "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "datasets": [
                {"label": "Headache", "data": [12, 19, 15, 10]},
                {"label": "Fatigue", "data": [15, 14, 22, 17]},
                {"label": "Focus Issues", "data": [8, 9, 14, 11]}
            ]
        },
        "accommodation_requests": {
            "labels": ["Flexible Schedule", "Remote Work", "Physical Mods", "Leave", "Other"],
            "datasets": [
                {"label": "Current Period", "data": [42, 28, 15, 10, 5]},
                {"label": "Previous Period", "data": [38, 32, 12, 12, 6]}
            ]
        }
    }
    
    chart_data = sample_chart_data.get(trend_type, {
        "labels": ["No data available"],
        "datasets": [{"label": "No data", "data": [0]}]
    })
    
    return {
        "status": "success",
        "message": f"Here are the anonymous {trend_type} trends for the past {time_period}{department_str}:",
        "insights": insights,
        "chart_data": chart_data,
        "recommendation": "Consider reviewing the meeting policy to further improve wellbeing scores."
    }

def manage_accommodation_requests_handler(
    action: Literal["list", "approve", "request_info", "deny"],
    request_id: Optional[str] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage employee accommodation requests.
    
    Args:
        action: The action to take on accommodation requests
        request_id: The ID of the specific request to act on (not needed for 'list')
        notes: Optional notes about the action (required for 'deny')
        
    Returns:
        Request data or confirmation message
    """
    # In a real implementation, this would interact with a request management system
    
    # Sample list of requests for demonstration
    sample_requests = [
        {
            "request_id": "ACC-12345",
            "type": "flexible_schedule",
            "status": "pending",
            "requested_date": "2025-05-15",
            "details": "Requesting to shift schedule to 10am-6pm for 2 weeks",
            "department": "Marketing",
            "employee_id": "[anonymized]"  # HR can't see who made the request unless necessary
        },
        {
            "request_id": "ACC-12346",
            "type": "remote_work",
            "status": "pending",
            "requested_date": "2025-05-16",
            "details": "Requesting to work remotely on Tuesdays and Thursdays",
            "department": "Engineering",
            "employee_id": "[anonymized]"
        }
    ]
    
    if action == "list":
        return {
            "status": "success",
            "message": "Current accommodation requests:",
            "requests": sample_requests
        }
    
    # For other actions, we need a request_id
    if not request_id:
        return {
            "status": "error",
            "message": "Request ID is required for this action."
        }
    
    # For deny action, notes are required
    if action == "deny" and not notes:
        return {
            "status": "error",
            "message": "Notes explaining the reason for denial are required."
        }
    
    # Find the request with the given ID
    request = next((r for r in sample_requests if r["request_id"] == request_id), None)
    if not request:
        return {
            "status": "error",
            "message": f"No request found with ID {request_id}."
        }
    
    # Process the action
    action_responses = {
        "approve": {
            "status": "success",
            "message": f"Request {request_id} has been approved.",
            "next_steps": [
                "The employee has been notified.",
                "Accommodation details have been shared with their manager.",
                "A calendar reminder has been set for follow-up in 2 weeks."
            ]
        },
        "request_info": {
            "status": "success",
            "message": f"Additional information has been requested for request {request_id}.",
            "next_steps": [
                "The employee has been notified.",
                "You will receive an alert when they respond."
            ]
        },
        "deny": {
            "status": "success",
            "message": f"Request {request_id} has been denied with explanation.",
            "next_steps": [
                "The employee has been notified with your explanation.",
                "Alternative accommodations have been suggested.",
                "This decision has been logged for compliance purposes."
            ]
        }
    }
    
    return action_responses.get(action, {
        "status": "error",
        "message": f"Unknown action: {action}"
    })

def create_wellness_policy_handler(
    policy_type: Literal["menstrual_leave", "mental_health", "flexible_work", "environmental", "custom"],
    policy_name: str,
    eligibility_criteria: str,
    implementation_date: str
) -> Dict[str, Any]:
    """
    Create or update a workplace wellness policy.
    
    Args:
        policy_type: The category of policy being created
        policy_name: The name of the new policy
        eligibility_criteria: Who is eligible for this policy
        implementation_date: When the policy takes effect (YYYY-MM-DD)
        
    Returns:
        Policy template and implementation steps
    """
    # In a real implementation, this would generate policy documents based on best practices
    
    # Sample policy templates
    policy_templates = {
        "menstrual_leave": """
        # {policy_name}
        
        ## Purpose
        This policy establishes guidelines for employees experiencing menstrual symptoms that impact their work.
        
        ## Eligibility
        {eligibility_criteria}
        
        ## Policy Details
        1. Eligible employees may take up to 12 paid menstrual health days per year.
        2. No medical documentation is required.
        3. Privacy will be maintained; the reason for leave will be listed as "wellness leave" in systems.
        4. Leave can be taken in full or half-day increments.
        
        ## Effective Date
        This policy takes effect on {implementation_date}.
        """,
        
        "mental_health": """
        # {policy_name}
        
        ## Purpose
        This policy supports employee mental health and wellbeing in the workplace.
        
        ## Eligibility
        {eligibility_criteria}
        
        ## Policy Details
        1. Employees are entitled to 4 mental health days per year, separate from sick leave.
        2. Flexible work arrangements are available for employees with documented needs.
        3. All employees have access to the confidential Employee Assistance Program.
        4. Managers will receive training on supporting team mental health.
        
        ## Effective Date
        This policy takes effect on {implementation_date}.
        """,
        
        "flexible_work": """
        # {policy_name}
        
        ## Purpose
        This policy establishes guidelines for flexible working arrangements.
        
        ## Eligibility
        {eligibility_criteria}
        
        ## Policy Details
        1. Eligible employees may request flexible hours, compressed workweeks, or remote work.
        2. Requests will be evaluated based on job requirements and business needs.
        3. All arrangements will have a 30-day trial period followed by evaluation.
        4. Arrangements will be reviewed quarterly.
        
        ## Effective Date
        This policy takes effect on {implementation_date}.
        """
    }
    
    # Get the template for the specified policy type or use a generic one
    template = policy_templates.get(policy_type, """
        # {policy_name}
        
        ## Purpose
        This policy supports employee wellness in the workplace.
        
        ## Eligibility
        {eligibility_criteria}
        
        ## Policy Details
        1. [Policy details to be customized]
        2. [Additional policy points]
        3. [Implementation guidelines]
        
        ## Effective Date
        This policy takes effect on {implementation_date}.
    """)
    
    # Fill in the template
    filled_template = template.format(
        policy_name=policy_name,
        eligibility_criteria=eligibility_criteria,
        implementation_date=implementation_date
    )
    
    return {
        "status": "success",
        "message": f"Your {policy_type} policy has been created.",
        "policy_document": filled_template,
        "implementation_steps": [
            "1. Review the draft policy with legal counsel",
            "2. Share with leadership team for feedback",
            "3. Plan communication strategy for roll-out",
            "4. Schedule manager training sessions",
            "5. Prepare FAQ document for employees"
        ]
    }

# Create FunctionTool instances for all the HR handlers
view_anonymous_trends_tool = FunctionTool(func=view_anonymous_trends_handler)
manage_accommodation_requests_tool = FunctionTool(func=manage_accommodation_requests_handler)
create_wellness_policy_tool = FunctionTool(func=create_wellness_policy_handler)

# Combine all HR tools into a list for the HR agent
HR_TOOLS = [
    view_anonymous_trends_tool,
    manage_accommodation_requests_tool,
    create_wellness_policy_tool
]

# ---- Employer Tools ----

def calculate_wellness_roi_handler(
    initiative_type: Literal["mental_health", "physical_wellness", "flexible_work", "comprehensive"],
    investment_amount: float,
    time_period: Literal["6_months", "1_year", "2_years", "5_years"] = "1_year"
) -> Dict[str, Any]:
    """
    Calculate the potential return on investment for workplace wellness initiatives.
    
    Args:
        initiative_type: The category of wellness program
        investment_amount: The budget allocated to the initiative (in USD)
        time_period: The time horizon for ROI calculation
        
    Returns:
        ROI projections and benefits breakdown
    """
    # In a real implementation, this would use research-based ROI models
    
    # Sample ROI multipliers based on initiative type and time period
    roi_multipliers = {
        "mental_health": {
            "6_months": 1.5,
            "1_year": 2.8,
            "2_years": 4.3,
            "5_years": 7.1
        },
        "physical_wellness": {
            "6_months": 1.2,
            "1_year": 2.4,
            "2_years": 3.7,
            "5_years": 6.2
        },
        "flexible_work": {
            "6_months": 1.3,
            "1_year": 2.6,
            "2_years": 4.1,
            "5_years": 6.9
        },
        "comprehensive": {
            "6_months": 1.7,
            "1_year": 3.1,
            "2_years": 5.2,
            "5_years": 8.5
        }
    }
    
    # Calculate projected ROI
    multiplier = roi_multipliers.get(initiative_type, {}).get(time_period, 2.0)
    projected_return = investment_amount * multiplier
    net_gain = projected_return - investment_amount
    roi_percentage = (net_gain / investment_amount) * 100
    
    # Benefits breakdown (would be based on research in a real implementation)
    benefits_breakdown = {
        "mental_health": {
            "Reduced absenteeism": 35,
            "Improved productivity": 25,
            "Reduced turnover": 20,
            "Healthcare savings": 15,
            "Other benefits": 5
        },
        "physical_wellness": {
            "Healthcare cost savings": 40,
            "Reduced absenteeism": 25,
            "Improved productivity": 20,
            "Reduced turnover": 10,
            "Other benefits": 5
        },
        "flexible_work": {
            "Reduced turnover": 35,
            "Improved productivity": 30,
            "Reduced real estate costs": 15,
            "Reduced absenteeism": 15,
            "Other benefits": 5
        },
        "comprehensive": {
            "Reduced turnover": 25,
            "Healthcare cost savings": 25,
            "Improved productivity": 20,
            "Reduced absenteeism": 20,
            "Other benefits": 10
        }
    }
    
    breakdown = benefits_breakdown.get(initiative_type, {
        "Improved outcomes": 100
    })
    
    # Sample comparison data
    industry_average_roi = roi_percentage * 0.8  # 20% below the projected for this company
    
    return {
        "status": "success",
        "message": f"ROI projection for {initiative_type} initiative over {time_period}:",
        "investment": investment_amount,
        "projected_return": projected_return,
        "net_gain": net_gain,
        "roi_percentage": roi_percentage,
        "industry_comparison": f"Your projected ROI is {(roi_percentage / industry_average_roi - 1) * 100:.1f}% higher than the industry average.",
        "benefits_breakdown": breakdown,
        "key_metrics_to_track": [
            "Employee retention rates",
            "Absenteeism and presenteeism",
            "Employee satisfaction scores",
            "Healthcare utilization changes",
            "Productivity measurements"
        ]
    }

def forecast_workforce_impact_handler(
    scenario: Literal["current_trend", "improved_support", "reduced_support"],
    department: Optional[str] = None,
    time_horizon: Literal["6_months", "1_year", "3_years", "5_years"] = "1_year"
) -> Dict[str, Any]:
    """
    Forecast the impact of wellness policies on workforce metrics.
    
    Args:
        scenario: The wellness support scenario to analyze
        department: Optional filter for a specific department
        time_horizon: How far into the future to forecast
        
    Returns:
        Workforce impact projections and recommendations
    """
    # In a real implementation, this would use predictive models based on research
    
    department_str = f" in the {department} department" if department else " across all departments"
    
    # Impact multipliers for different scenarios
    impact_factors = {
        "current_trend": {
            "turnover": 1.0,
            "productivity": 1.0,
            "engagement": 1.0,
            "absenteeism": 1.0,
            "recruitment": 1.0
        },
        "improved_support": {
            "turnover": 0.82,  # 18% reduction
            "productivity": 1.15,  # 15% increase
            "engagement": 1.23,  # 23% increase
            "absenteeism": 0.75,  # 25% reduction
            "recruitment": 0.85  # 15% reduction in time-to-hire
        },
        "reduced_support": {
            "turnover": 1.28,  # 28% increase
            "productivity": 0.91,  # 9% decrease
            "engagement": 0.84,  # 16% decrease
            "absenteeism": 1.32,  # 32% increase
            "recruitment": 1.20  # 20% increase in time-to-hire
        }
    }
    
    factors = impact_factors.get(scenario, impact_factors["current_trend"])
    
    # Base metrics (would be from company data in a real implementation)
    base_metrics = {
        "turnover": "15%",
        "productivity": "100 (baseline)",
        "engagement": "7.2/10",
        "absenteeism": "4.5 days per employee per year",
        "recruitment": "42 days average time-to-hire"
    }
    
    # Calculate projected metrics
    projected_metrics = {
        "turnover": f"{15 * factors['turnover']:.1f}%",
        "productivity": f"{100 * factors['productivity']:.1f} ({'+' if factors['productivity'] > 1 else ''}{(factors['productivity'] - 1) * 100:.1f}%)",
        "engagement": f"{7.2 * factors['engagement']:.1f}/10",
        "absenteeism": f"{4.5 * factors['absenteeism']:.1f} days per employee per year",
        "recruitment": f"{42 * factors['recruitment']:.1f} days average time-to-hire"
    }
    
    # Recommendations based on scenario
    recommendations = {
        "current_trend": [
            "Maintain current wellness programs",
            "Collect more detailed data to identify optimization opportunities",
            "Benchmark against industry leaders to identify gaps"
        ],
        "improved_support": [
            "Implement the proposed enhanced wellness initiatives",
            "Prioritize flexible work and mental health support for highest ROI",
            "Create communication strategy to ensure high program awareness",
            "Develop manager training to support the initiatives"
        ],
        "reduced_support": [
            "Reconsider reduction in wellness support due to projected negative impacts",
            "If reduction necessary, phase gradually to minimize disruption",
            "Invest in retention strategies for key talent to offset increased turnover risk",
            "Enhance remaining wellness offerings to maximize impact"
        ]
    }
    
    return {
        "status": "success",
        "message": f"Workforce impact forecast for {scenario} scenario{department_str} over {time_horizon}:",
        "current_metrics": base_metrics,
        "projected_metrics": projected_metrics,
        "cost_implications": {
            "turnover": f"${1500000 * (factors['turnover'] - 1):.2f}" if factors['turnover'] != 1 else "$0",
            "productivity": f"${2500000 * (factors['productivity'] - 1):.2f}" if factors['productivity'] != 1 else "$0",
            "absenteeism": f"${750000 * (factors['absenteeism'] - 1):.2f}" if factors['absenteeism'] != 1 else "$0",
            "recruitment": f"${350000 * (factors['recruitment'] - 1):.2f}" if factors['recruitment'] != 1 else "$0"
        },
        "recommendations": recommendations.get(scenario, ["No specific recommendations available."]),
        "data_sources": [
            "Current company metrics",
            "Industry research on wellness program impacts",
            "Meta-analysis of 142 workplace wellness studies",
            "Peer company benchmarking"
        ]
    }

def get_insights_dashboard_handler(
    focus_area: Literal["overview", "retention", "productivity", "culture", "cost_savings"] = "overview"
) -> Dict[str, Any]:
    """
    Generate an organizational insights dashboard for decision-making.
    
    Args:
        focus_area: The specific area to analyze in depth
        
    Returns:
        Dashboard data and insights
    """
    # In a real implementation, this would generate visualizations from anonymized data
    
    # Generate insights based on the focus area
    insights_by_area = {
        "overview": [
            "Wellness program participation is at 72%, with highest engagement in Engineering and Marketing",
            "Accommodation requests have decreased by 18% since implementing flexible work policies",
            "Healthcare utilization costs are down 12% year-over-year for participating employees",
            "Departments with >80% wellness participation show 24% lower turnover"
        ],
        "retention": [
            "Exit interviews cite work-life balance as top reason for staying/leaving",
            "Teams with managers trained in wellness support show 31% higher retention",
            "Employees who use wellness programs stay 2.4 years longer on average",
            "91% of employees rate wellness support as 'very important' to job satisfaction"
        ],
        "productivity": [
            "Teams with flexible schedules report 16% fewer missed deadlines",
            "Self-reported productivity is 22% higher among regular wellness program users",
            "Focus-related symptoms decrease by 35% for employees using mindfulness program",
            "Meeting efficiency increased 27% after implementing wellness-focused meeting policies"
        ],
        "culture": [
            "Employee satisfaction scores increased from 7.1 to 8.4 after wellness program expansion",
            "88% of employees report feeling 'valued' by the organization due to wellness support",
            "Applications increased 42% after highlighting wellness benefits in job postings",
            "Employees rate the culture as 'supportive' 3.2x more frequently than before program"
        ],
        "cost_savings": [
            "Healthcare premium increases held at 2.1% vs. industry average of 7.3%",
            "Recruiting costs decreased $425,000 due to improved retention",
            "Productivity gains estimated at $1.2M annually based on self-reporting",
            "Absenteeism-related costs down $380,000 year-over-year"
        ]
    }
    
    insights = insights_by_area.get(focus_area, [
        "No specific insights available for this focus area.",
        "Consider refining your search parameters."
    ])
    
    # Sample chart data
    chart_data = {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [
            {"label": "Program Participation", "data": [65, 68, 72, 75]},
            {"label": "Wellness Scores", "data": [72, 74, 78, 82]},
            {"label": "Retention Rate", "data": [88, 89, 91, 93]}
        ]
    }
    
    return {
        "status": "success",
        "message": f"Organizational insights dashboard focused on {focus_area}:",
        "insights": insights,
        "chart_data": chart_data,
        "strategic_recommendations": [
            "Expand flexible work policies to all departments based on positive impacts",
            "Invest in manager training on supporting team wellness",
            "Consider piloting the menstrual leave policy organization-wide",
            "Develop more sophisticated measurement systems for wellness impact"
        ]
    }

# Create FunctionTool instances for all the employer handlers
calculate_wellness_roi_tool = FunctionTool(func=calculate_wellness_roi_handler)
forecast_workforce_impact_tool = FunctionTool(func=forecast_workforce_impact_handler)
get_insights_dashboard_tool = FunctionTool(func=get_insights_dashboard_handler)

# Combine all employer tools into a list for the employer agent
EMPLOYER_TOOLS = [
    calculate_wellness_roi_tool,
    forecast_workforce_impact_tool,
    get_insights_dashboard_tool
]

# All tools combined
ALL_TOOLS = EMPLOYEE_TOOLS + HR_TOOLS + EMPLOYER_TOOLS 