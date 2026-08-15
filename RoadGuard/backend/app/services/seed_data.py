from app.core.config import get_settings

settings = get_settings()

# Seed cost rates (used when the table is empty).
SEED_COST_RATES: list[dict] = [
    {"rate_key": "ASPHALT_PER_SQM", "name": "Asphalt rate", "unit": "INR/sqm", "value": 2200.0,
     "description": "Material cost of asphalt per square metre."},
    {"rate_key": "CONCRETE_PER_SQM", "name": "Concrete rate", "unit": "INR/sqm", "value": 1800.0,
     "description": "Material cost of concrete per square metre."},
    {"rate_key": "LABOR_PER_SQM", "name": "Labor rate", "unit": "INR/sqm", "value": 600.0,
     "description": "Labor cost per square metre of repair."},
    {"rate_key": "EQUIPMENT_PER_SQM", "name": "Equipment rate", "unit": "INR/sqm", "value": 400.0,
     "description": "Machinery/equipment cost per square metre."},
    {"rate_key": "TRANSPORT_PER_JOB", "name": "Transport rate", "unit": "INR/job", "value": 2000.0,
     "description": "Fixed transport cost per repair job."},
    {"rate_key": "CONTINGENCY_PERCENT", "name": "Contingency percentage", "unit": "%", "value": 5.0,
     "description": "Contingency added on the sub-total."},
    {"rate_key": "REPAIR_MARGIN_PERCENT", "name": "Repair margin percentage", "unit": "%", "value": 20.0,
     "description": "Extra area recommended beyond the detected pothole area."},
]
