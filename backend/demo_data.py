"""
Demo data fallback — realistic Skylark Drones sample data
Used when monday.com API is unavailable or not authenticated
"""

DEMO_DEALS = [
    {"id": "1", "name": "NTPC Solar Drone Survey", "status": "Proposal Sent", "sector": "Energy", "deal_value": 4500000, "close_date": "2026-09-15", "owner": "Ravi Kumar"},
    {"id": "2", "name": "Adani Port Inspection", "status": "Won", "sector": "Infrastructure", "deal_value": 8200000, "close_date": "2026-08-01", "owner": "Priya Singh"},
    {"id": "3", "name": "ONGC Pipeline Mapping", "status": "Negotiation", "sector": "Energy", "deal_value": 12000000, "close_date": "2026-09-30", "owner": "Arjun Mehta"},
    {"id": "4", "name": "Army Base Security Survey", "status": "Won", "sector": "Defence", "deal_value": 18500000, "close_date": "2026-07-20", "owner": "Ravi Kumar"},
    {"id": "5", "name": "Mahindra Farm Analytics", "status": "Demo Scheduled", "sector": "Agriculture", "deal_value": 3200000, "close_date": "2026-10-10", "owner": "Sneha Patel"},
    {"id": "6", "name": "Coal India Mine Survey", "status": "Proposal Sent", "sector": "Mining", "deal_value": 6800000, "close_date": "2026-09-20", "owner": "Arjun Mehta"},
    {"id": "7", "name": "Reliance Refinery Inspection", "status": "Lost", "sector": "Energy", "deal_value": 9500000, "close_date": "2026-07-15", "owner": "Priya Singh"},
    {"id": "8", "name": "NHAI Highway Survey", "status": "Won", "sector": "Infrastructure", "deal_value": 5500000, "close_date": "2026-08-10", "owner": "Ravi Kumar"},
    {"id": "9", "name": "Punjab Crop Health Monitoring", "status": "Negotiation", "sector": "Agriculture", "deal_value": 2800000, "close_date": "2026-10-01", "owner": "Sneha Patel"},
    {"id": "10", "name": "Tata Steel Plant Survey", "status": "Proposal Sent", "sector": "Infrastructure", "deal_value": 7200000, "close_date": "2026-09-25", "owner": "Arjun Mehta"},
    {"id": "11", "name": "Indian Navy Base Mapping", "status": "Demo Scheduled", "sector": "Defence", "deal_value": 22000000, "close_date": "2026-11-01", "owner": "Ravi Kumar"},
    {"id": "12", "name": "Vedanta Zinc Mine Inspection", "status": "Lost", "sector": "Mining", "deal_value": 4100000, "close_date": "2026-07-05", "owner": "Priya Singh"},
    {"id": "13", "name": "BPCL Refinery Drone Survey", "status": "Proposal Sent", "sector": "Energy", "deal_value": 5900000, "close_date": "2026-10-15", "owner": "Arjun Mehta"},
    {"id": "14", "name": "MP State Forest Mapping", "status": "Won", "sector": "Agriculture", "deal_value": 3800000, "close_date": "2026-08-20", "owner": "Sneha Patel"},
    {"id": "15", "name": "Hindustan Zinc Mine Survey", "status": "Negotiation", "sector": "Mining", "deal_value": 8800000, "close_date": "2026-10-20", "owner": "Arjun Mehta"},
]

DEMO_WORK_ORDERS = [
    {"id": "101", "name": "NTPC Vindhyachal Survey", "status": "In Progress", "client": "NTPC", "budget": 4200000, "start_date": "2026-08-01", "end_date": "2026-08-31", "assigned_to": "Team Alpha"},
    {"id": "102", "name": "Adani Mundra Port Phase 1", "status": "Completed", "client": "Adani Ports", "budget": 8000000, "start_date": "2026-07-01", "end_date": "2026-08-05", "assigned_to": "Team Beta"},
    {"id": "103", "name": "Army Northern Command Survey", "status": "In Progress", "client": "Indian Army", "budget": 17000000, "start_date": "2026-07-15", "end_date": "2026-09-15", "assigned_to": "Team Gamma"},
    {"id": "104", "name": "NHAI NH-44 Mapping", "status": "Completed", "client": "NHAI", "budget": 5200000, "start_date": "2026-07-20", "end_date": "2026-08-10", "assigned_to": "Team Alpha"},
    {"id": "105", "name": "MP Forest Department Phase 2", "status": "Delayed", "client": "MP Forest Dept", "budget": 3600000, "start_date": "2026-08-05", "end_date": "2026-08-25", "assigned_to": "Team Beta"},
    {"id": "106", "name": "ONGC Rajasthan Pipeline", "status": "In Progress", "client": "ONGC", "budget": 11500000, "start_date": "2026-08-10", "end_date": "2026-09-30", "assigned_to": "Team Gamma"},
    {"id": "107", "name": "Coal India Jharia Survey", "status": "On Hold", "client": "Coal India", "budget": 6500000, "start_date": "2026-08-15", "end_date": "2026-09-20", "assigned_to": "Team Alpha"},
    {"id": "108", "name": "Punjab Kharif Crop Survey", "status": "In Progress", "client": "Punjab Agri Dept", "budget": 2600000, "start_date": "2026-08-18", "end_date": "2026-09-05", "assigned_to": "Team Beta"},
    {"id": "109", "name": "Tata Steel Jamshedpur Inspection", "status": "Delayed", "client": "Tata Steel", "budget": 7000000, "start_date": "2026-08-01", "end_date": "2026-08-20", "assigned_to": "Team Gamma"},
    {"id": "110", "name": "Navy Visakhapatnam Mapping", "status": "In Progress", "client": "Indian Navy", "budget": 20000000, "start_date": "2026-08-20", "end_date": "2026-10-31", "assigned_to": "Team Alpha"},
]
