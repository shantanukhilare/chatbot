import os
import requests
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool

# Base API Configuration
API_BASE_URL = os.getenv("ERP_API_BASE_URL", "https://teqoosapi.mahindrateqo.com")


def _get_headers() -> Dict[str, str]:
    """Helper to retrieve standard headers including Bearer token."""
    token = os.getenv("ERP_BEARER_TOKEN", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }


# =====================================================================
# 1. MAINTENANCE SCHEDULE READ & LOOKUP TOOLS
# =====================================================================

@tool
def get_maintenance_types() -> str:
    """Retrieve all available maintenance types (e.g., breakdown, preventive, calibration).
    Useful to fetch valid category/type IDs before filtering or creating schedules.
    """
    url = f"{API_BASE_URL}/api/MaintenanceType/getList"
    response = requests.get(url, headers=_get_headers())
    if response.status_code == 200:
        return response.text
    return f"Error fetching maintenance types: HTTP {response.status_code} - {response.text}"


@tool
def get_maintenance_schedule_by_id(schedule_id: int) -> str:
    """Look up full details of a specific maintenance schedule entry by its schedule ID."""
    url = f"{API_BASE_URL}/api/MaintenanceSchedule/get/{schedule_id}"
    response = requests.get(url, headers=_get_headers())
    if response.status_code == 200:
        return response.text
    return f"Error fetching schedule {schedule_id}: HTTP {response.status_code} - {response.text}"


@tool
def get_maintenance_calendar_data(
    site_id: int,
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    filter_status: Optional[str] = None,
    maintenance_type: int = 0
) -> str:
    """Fetch calendar-view maintenance events across a site for a given date range.
    
    Args:
        site_id: Unique identifier of the solar/wind site.
        user_id: ID of the querying user.
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        filter_status: Optional status string (e.g., 'Open', 'Completed').
        maintenance_type: Maintenance type identifier (0 for all).
    """
    url = f"{API_BASE_URL}/api/MaintenanceSchedule/getPlannerCalenderData"
    payload = {
        "siteID": site_id,
        "userID": user_id,
        "startDate": start_date,
        "endDate": end_date,
        "filterStatus": filter_status,
        "maintenanceType": maintenance_type
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return response.text
    return f"Error retrieving planner calendar: HTTP {response.status_code} - {response.text}"


@tool
def get_user_assigned_maintenance_tasks(
    user_id: int,
    site_id: int,
    row_index: int = 0,
    row_count: int = 20,
    maintenance_category: int = 1
) -> str:
    """Query scheduled maintenance tasks assigned to a specific user across a site."""
    url = f"{API_BASE_URL}/api/MaintenanceSchedule/getUserAssignedTask"
    payload = {
        "userID": user_id,
        "siteID": site_id,
        "rowIndex": row_index,
        "rowCount": row_count,
        "maintenanceCategory": maintenance_category
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return response.text
    return f"Error retrieving assigned tasks for user {user_id}: HTTP {response.status_code} - {response.text}"


# =====================================================================
# 2. MAINTENANCE SCHEDULE WRITE & STATUS TOOLS
# =====================================================================

@tool
def create_maintenance_schedule(
    site_id: int,
    maintenance_type: int,
    maintenance_category: int,
    asset_ids: List[str],
    assigned_to: List[str],
    scheduled_by: int,
    description: str,
    schedule_date_from: str,
    schedule_date_to: str,
    schedule_time_from: str = "09:00:00",
    schedule_time_to: str = "17:00:00",
    priority: int = 1,
    is_work_permit_required: bool = False
) -> str:
    """Create a new maintenance schedule entry for assets on a site.
    
    Args:
        site_id: Numerical ID of the plant or site.
        maintenance_type: Type ID (Preventive, Corrective, Predictive, etc.).
        maintenance_category: Category ID of the maintenance activity.
        asset_ids: List of asset ID strings (e.g., ['INV-01', 'SMB-03']).
        assigned_to: List of user IDs or usernames tasked with execution.
        scheduled_by: User ID of the person creating the schedule.
        description: Summary of maintenance work to perform.
        schedule_date_from: Start date (ISO format YYYY-MM-DDTHH:MM:SS).
        schedule_date_to: End date (ISO format YYYY-MM-DDTHH:MM:SS).
        schedule_time_from: Daily window start time (e.g., '09:00:00').
        schedule_time_to: Daily window end time (e.g., '17:00:00').
        priority: Priority level (e.g., 1=Low, 2=Medium, 3=High).
        is_work_permit_required: Whether an HSE PTW (Permit to Work) is mandatory.
    """
    url = f"{API_BASE_URL}/api/MaintenanceSchedule/Post"
    payload = {
        "siteid": site_id,
        "maintenancetype": maintenance_type,
        "maintenancecategory": maintenance_category,
        "assetids": asset_ids,
        "assignedto": assigned_to,
        "scheduledby": scheduled_by,
        "description": description,
        "scheduledatefrom": schedule_date_from,
        "scheduledateto": schedule_date_to,
        "scheduletimefrom": schedule_time_from,
        "scheduletimeto": schedule_time_to,
        "priority": priority,
        "isworkpermitrequired": is_work_permit_required,
        "isactive": 1,
        "status": 1
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return f"Maintenance schedule created successfully. Response: {response.text}"
    return f"Failed to create schedule: HTTP {response.status_code} - {response.text}"


@tool
def complete_maintenance_task(task_id: int, status_id: int, comment: Optional[str] = None) -> str:
    """Update and complete a maintenance task execution status with closure comments.
    
    Args:
        task_id: ID of the schedule/task to update.
        status_id: Numeric target status ID (e.g., 3=Completed, 4=Cancelled).
        comment: Remarks or observations upon completing the task.
    """
    url = f"{API_BASE_URL}/api/MaintenanceSchedule/Completetask"
    payload = {
        "taskId": task_id,
        "statusId": status_id,
        "comment": comment or "Task marked completed via Agent."
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return f"Task {task_id} status updated successfully. Response: {response.text}"
    return f"Failed to complete task {task_id}: HTTP {response.status_code} - {response.text}"


# =====================================================================
# 3. WORK ORDER & CHECKLIST TOOLS
# =====================================================================

@tool
def submit_work_order_request(
    site_id: int,
    project_code: str,
    wbs_code: str,
    vendor_id: int,
    requested_by: int,
    order_type: int,
    product_service_id: int,
    quantity: float,
    unit_rate: float
) -> str:
    """Submit a formal Work Order request for maintenance vendor services and line items."""
    url = f"{API_BASE_URL}/api/WorkOrderRequest/Insert"
    payload = {
        "siteid": site_id,
        "projectcode": project_code,
        "wbscode": wbs_code,
        "vendorid": vendor_id,
        "requestedby": requested_by,
        "ordertype": order_type,
        "isactive": 1,
        "workorderrequests": [
            {
                "productserviceid": product_service_id,
                "quantity": quantity,
                "unitrate": unit_rate
            }
        ]
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return f"Work Order request submitted successfully. Response: {response.text}"
    return f"Failed to create work order request: HTTP {response.status_code} - {response.text}"


@tool
def save_maintenance_checklist_entry(
    schedule_id: int,
    site_id: int,
    asset_id: str,
    event_code: str,
    checklist_name: str,
    json_data: str,
    work_permit_id: int = 0,
    comment: Optional[str] = None
) -> str:
    """Save completed digital checklist form data for an asset under a maintenance schedule."""
    url = f"{API_BASE_URL}/api/DynamicForm/saveChecklistFormData"
    payload = {
        "scheduleId": schedule_id,
        "siteId": site_id,
        "assetId": asset_id,
        "eventCode": event_code,
        "checkListName": checklist_name,
        "jsonData": json_data,
        "workPermitId": work_permit_id,
        "comment": comment or ""
    }
    response = requests.post(url, json=payload, headers=_get_headers())
    if response.status_code == 200:
        return f"Checklist data saved successfully. Response: {response.text}"
    return f"Failed to save checklist data: HTTP {response.status_code} - {response.text}"

# maintenance_tools = [
#     get_maintenance_types,
#     get_maintenance_schedule_by_id,
#     get_maintenance_calendar_data,
#     get_user_assigned_maintenance_tasks,
#     create_maintenance_schedule,
#     complete_maintenance_task,
#     submit_work_order_request,
#     save_maintenance_checklist_entry,
# ]

# Bind tools to your LLM
# llm_with_tools = llm.bind_tools(maintenance_tools)