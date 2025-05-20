"""
Firestore service for accessing wellness data with privacy protections.
"""

from google.cloud import firestore
import datetime
from typing import Dict, List, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirestoreService:
    """Service class for accessing Firestore data with privacy protections."""
    
    def __init__(self):
        """Initialize Firestore client"""
        self.db = firestore.Client()
    
    def get_department_stats(self, department: Optional[str] = None, months: int = 3) -> Dict[str, Any]:
        """
        Get aggregated department statistics.
        
        Args:
            department: Optional department to filter by, or None for all departments
            months: Number of months to retrieve (defaults to 3 months)
            
        Returns:
            Dict with department statistics
        """
        try:
            collection = self.db.collection("department_stats")
            
            # Get current date and calculate date threshold
            now = datetime.datetime.now()
            date_threshold = now - datetime.timedelta(days=30*months)
            
            # Query for department stats within time range
            if department and department != "Company-wide":
                query = collection.where("department", "==", department).where("date", ">=", date_threshold)
            else:
                # For company-wide, we'll specifically query for the "Company-wide" stats
                query = collection.where("department", "==", "Company-wide").where("date", ">=", date_threshold)
            
            # Execute query and process results
            results = query.get()
            
            if not results:
                return {"message": "No data found for the specified parameters", "data": []}
            
            # Process data
            stats_data = []
            for doc in results:
                data = doc.to_dict()
                # Only include aggregated metrics, no individual employee data
                stats_data.append({
                    "department": data.get("department"),
                    "month": data.get("month"),
                    "metrics": data.get("metrics", {})
                })
            
            # Sort by date
            stats_data.sort(key=lambda x: x.get("month", ""), reverse=True)
            
            return {
                "message": f"Retrieved {len(stats_data)} months of data for {department if department else 'all departments'}",
                "data": stats_data
            }
            
        except Exception as e:
            logger.error(f"Error retrieving department stats: {str(e)}")
            return {"error": f"Could not retrieve department statistics: {str(e)}"}
    
    def get_leave_trends(self, department: Optional[str] = None, months: int = 6) -> Dict[str, Any]:
        """
        Get anonymized leave trends by department.
        
        Args:
            department: Optional department to filter by
            months: Number of months to analyze
            
        Returns:
            Dict with leave trend analysis
        """
        try:
            collection = self.db.collection("leave_requests")
            
            # Get current date and calculate date threshold
            now = datetime.datetime.now()
            date_threshold = now - datetime.timedelta(days=30*months)
            
            # Query for leave requests within time range
            if department:
                query = collection.where("department", "==", department).where("request_date", ">=", date_threshold)
            else:
                query = collection.where("request_date", ">=", date_threshold)
            
            # Execute query
            results = query.get()
            
            if not results:
                return {"message": "No leave data found for the specified parameters", "data": {}}
            
            # Process and aggregate data
            leave_data = {}
            leave_types = {}
            total_requests = 0
            
            for doc in results:
                data = doc.to_dict()
                
                # Extract month from request date
                request_date = data.get("request_date")
                if not request_date:
                    continue
                    
                month_str = request_date.strftime("%Y-%m")
                
                # Initialize month data if not exists
                if month_str not in leave_data:
                    leave_data[month_str] = {
                        "total_requests": 0,
                        "total_days": 0,
                        "leave_types": {}
                    }
                
                # Update counters
                leave_data[month_str]["total_requests"] += 1
                leave_data[month_str]["total_days"] += data.get("duration_days", 0)
                
                # Count leave types
                leave_type = data.get("leave_type", "Unknown")
                if leave_type not in leave_data[month_str]["leave_types"]:
                    leave_data[month_str]["leave_types"][leave_type] = 0
                leave_data[month_str]["leave_types"][leave_type] += 1
                
                # Update overall leave types counter
                if leave_type not in leave_types:
                    leave_types[leave_type] = 0
                leave_types[leave_type] += 1
                
                total_requests += 1
            
            # Calculate percentages for leave types
            for month, month_data in leave_data.items():
                for leave_type, count in month_data["leave_types"].items():
                    month_data["leave_types"][leave_type] = {
                        "count": count,
                        "percentage": round(count / month_data["total_requests"] * 100, 1)
                    }
            
            # Sort months chronologically
            sorted_months = sorted(leave_data.keys())
            sorted_leave_data = {month: leave_data[month] for month in sorted_months}
            
            # Prepare summary
            summary = {
                "total_requests": total_requests,
                "leave_types_breakdown": {},
                "highest_month": max(sorted_leave_data.items(), key=lambda x: x[1]["total_days"])[0] if sorted_leave_data else None
            }
            
            for leave_type, count in leave_types.items():
                summary["leave_types_breakdown"][leave_type] = {
                    "count": count,
                    "percentage": round(count / total_requests * 100, 1)
                }
            
            return {
                "message": f"Retrieved leave trends for {department if department else 'all departments'} across {len(sorted_leave_data)} months",
                "summary": summary,
                "monthly_data": sorted_leave_data
            }
            
        except Exception as e:
            logger.error(f"Error retrieving leave trends: {str(e)}")
            return {"error": f"Could not retrieve leave trend data: {str(e)}"}
    
    def get_health_trends(self, trend_type: str = "stress_levels", months: int = 6) -> Dict[str, Any]:
        """
        Get anonymized health trend data.
        
        Args:
            trend_type: Type of health trend to analyze
            months: Number of months to analyze
            
        Returns:
            Dict with health trend analysis
        """
        try:
            collection = self.db.collection("health_trends")
            
            # Get current date and calculate date threshold
            now = datetime.datetime.now()
            date_threshold = now - datetime.timedelta(days=30*months)
            
            # Query for health trends within time range
            query = collection.where("trend_type", "==", trend_type).where("date", ">=", date_threshold)
            
            # Execute query
            results = query.get()
            
            if not results:
                return {"message": f"No {trend_type} trend data found for the specified parameters", "data": {}}
            
            # Process data
            trend_data = []
            for doc in results:
                data = doc.to_dict()
                trend_data.append({
                    "month": data.get("month"),
                    "metrics": data.get("metrics", {}),
                    "insights": data.get("insights", [])
                })
            
            # Sort by month
            trend_data.sort(key=lambda x: x.get("month", ""))
            
            # Calculate averages and trends
            averages = {
                "company_average": sum(item["metrics"].get("company_average", 0) for item in trend_data) / len(trend_data) if trend_data else 0
            }
            
            # Calculate department averages if department breakdown exists
            if trend_data and "department_breakdown" in trend_data[0]["metrics"]:
                averages["department_averages"] = {}
                for dept in trend_data[0]["metrics"]["department_breakdown"]:
                    dept_values = [item["metrics"]["department_breakdown"].get(dept, 0) for item in trend_data]
                    averages["department_averages"][dept] = sum(dept_values) / len(dept_values)
            
            # Identify trend direction (improving/worsening)
            if len(trend_data) >= 2:
                first_value = trend_data[0]["metrics"].get("company_average", 0)
                last_value = trend_data[-1]["metrics"].get("company_average", 0)
                
                if trend_type in ["stress_levels"]:  # Lower is better
                    trend_direction = "improving" if last_value < first_value else "worsening"
                else:  # Higher is better
                    trend_direction = "improving" if last_value > first_value else "worsening"
                
                trend_change = round(abs(last_value - first_value) / first_value * 100, 1) if first_value else 0
            else:
                trend_direction = "unchanged"
                trend_change = 0
            
            return {
                "message": f"Retrieved {trend_type} trends across {len(trend_data)} months",
                "trend_name": trend_type,
                "trend_direction": trend_direction,
                "trend_change_percent": trend_change,
                "averages": averages,
                "monthly_data": trend_data
            }
            
        except Exception as e:
            logger.error(f"Error retrieving health trends: {str(e)}")
            return {"error": f"Could not retrieve health trend data: {str(e)}"}
    
    def get_wellness_programs(self) -> Dict[str, Any]:
        """
        Get information about wellness programs.
        
        Returns:
            Dict with wellness program information
        """
        try:
            collection = self.db.collection("wellness_programs")
            
            # Get all programs
            results = collection.get()
            
            if not results:
                return {"message": "No wellness programs found", "programs": []}
            
            # Process data
            programs = []
            for doc in results:
                data = doc.to_dict()
                programs.append({
                    "name": data.get("name"),
                    "description": data.get("description"),
                    "status": data.get("status"),
                    "participation_rate": data.get("participation_rate"),
                    "satisfaction_score": data.get("satisfaction_score")
                })
            
            # Sort by status then name
            status_order = {"Active": 0, "Scheduled": 1, "Completed": 2}
            programs.sort(key=lambda x: (status_order.get(x.get("status"), 99), x.get("name", "")))
            
            # Categorize programs
            categorized = {
                "active": [p for p in programs if p.get("status") == "Active"],
                "scheduled": [p for p in programs if p.get("status") == "Scheduled"],
                "completed": [p for p in programs if p.get("status") == "Completed"]
            }
            
            return {
                "message": f"Retrieved {len(programs)} wellness programs",
                "summary": {
                    "total_programs": len(programs),
                    "active_programs": len(categorized["active"]),
                    "scheduled_programs": len(categorized["scheduled"]),
                    "completed_programs": len(categorized["completed"]),
                    "avg_participation_rate": sum(p.get("participation_rate", 0) for p in programs) / len(programs) if programs else 0,
                    "avg_satisfaction_score": sum(p.get("satisfaction_score", 0) for p in programs if p.get("satisfaction_score", 0) > 0) / len([p for p in programs if p.get("satisfaction_score", 0) > 0]) if [p for p in programs if p.get("satisfaction_score", 0) > 0] else 0
                },
                "categorized": categorized,
                "all_programs": programs
            }
            
        except Exception as e:
            logger.error(f"Error retrieving wellness programs: {str(e)}")
            return {"error": f"Could not retrieve wellness programs: {str(e)}"}
    
    def get_department_leave_rates(self) -> Dict[str, Any]:
        """
        Get anonymized leave rates by department.
        
        Returns:
            Dict with department leave rates
        """
        try:
            collection = self.db.collection("department_stats")
            
            # Get the latest month stats for each department
            departments = ["Engineering", "Marketing", "Operations", "Sales", "HR", "Finance"]
            
            # Get current date
            now = datetime.datetime.now()
            current_month = now.strftime("%Y-%m")
            
            # Fetch latest data for each department
            leave_rates = {}
            for dept in departments:
                # Query for latest month available
                query = collection.where("department", "==", dept).order_by("date", direction=firestore.Query.DESCENDING).limit(1)
                results = query.get()
                
                if results:
                    doc = next(iter(results))
                    data = doc.to_dict()
                    leave_rates[dept] = {
                        "leave_rate": data.get("metrics", {}).get("leave_rate", 0),
                        "avg_leave_days": data.get("metrics", {}).get("avg_leave_days", 0),
                        "month": data.get("month", "Unknown")
                    }
            
            # Sort departments by leave rate (highest to lowest)
            sorted_depts = sorted(leave_rates.keys(), key=lambda x: leave_rates[x]["leave_rate"], reverse=True)
            sorted_leave_rates = {dept: leave_rates[dept] for dept in sorted_depts}
            
            # Calculate company-wide average
            if leave_rates:
                company_avg = sum(leave_rates[dept]["leave_rate"] for dept in leave_rates) / len(leave_rates)
            else:
                company_avg = 0
            
            return {
                "message": "Retrieved department leave rates",
                "company_average": company_avg,
                "highest_department": sorted_depts[0] if sorted_depts else None,
                "lowest_department": sorted_depts[-1] if sorted_depts else None,
                "department_rates": sorted_leave_rates
            }
            
        except Exception as e:
            logger.error(f"Error retrieving department leave rates: {str(e)}")
            return {"error": f"Could not retrieve department leave rates: {str(e)}"} 