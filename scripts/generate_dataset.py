"""Generate the deterministic, deliberately dirty versalMotors BI dataset.

The generator uses only Python's standard library.  It builds a coherent clean
dataset first and then injects a documented set of data-quality defects before
writing CSV extracts to data/raw/.  Re-running the script replaces only the nine
CSV files and the private generator truth document that it owns.
"""

from __future__ import annotations

import csv
import hashlib
import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


SEED = 20250301
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 6, 30)
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
TRUTH_PATH = ROOT / "data" / "generator_truth.md"
RNG = random.Random(SEED)

BASE_COUNTS = {
    "branches": 15,
    "models": 54,
    "salespeople": 225,
    "inventory": 25_000,
    "sales": 20_500,
    "service_records": 48_000,
    "warranty_claims": 3_050,
    "complaints": 1_850,
    "satisfaction": 15_000,
}

FIELDS = {
    "branches": ["branch_id", "branch_code", "branch_name", "branch_type", "address_line", "city", "region", "country_code", "opened_date", "floor_capacity", "service_bay_count", "manager_name", "active_flag"],
    "models": ["model_id", "manufacturer", "model_name", "model_year", "trim_name", "vehicle_segment", "body_style", "powertrain", "transmission", "engine_size_l", "battery_capacity_kwh", "fuel_efficiency", "seating_capacity", "msrp", "currency_code", "launch_date", "discontinued_date", "active_flag"],
    "salespeople": ["salesperson_id", "employee_code", "branch_id", "first_name", "last_name", "gender", "hire_date", "termination_date", "job_title", "experience_years_at_hire", "monthly_target_units", "commission_rate", "active_flag"],
    "inventory": ["inventory_id", "vin", "model_id", "branch_id", "exterior_color", "interior_color", "manufacture_date", "acquisition_date", "arrival_date", "condition", "odometer_km", "acquisition_cost", "listed_price", "currency_code", "inventory_status", "sold_date", "days_in_inventory", "record_updated_at"],
    "sales": ["sale_id", "inventory_id", "branch_id", "salesperson_id", "customer_ref", "sale_date", "delivery_date", "sale_status", "sales_channel", "customer_type", "gross_price", "discount_amount", "net_sale_price", "tax_amount", "fees_amount", "total_sale_price", "currency_code", "payment_method", "finance_term_months", "trade_in_flag", "trade_in_value", "created_at"],
    "service_records": ["service_id", "inventory_id", "branch_id", "sale_id", "customer_ref", "service_open_date", "service_close_date", "service_type", "service_status", "odometer_km", "labor_hours", "labor_cost", "parts_cost", "misc_cost", "total_service_cost", "customer_pay_amount", "warranty_pay_amount", "currency_code", "technician_team", "repeat_repair_flag"],
    "warranty_claims": ["claim_id", "service_id", "inventory_id", "sale_id", "branch_id", "claim_date", "failure_category", "claim_description", "claim_amount", "approved_amount", "claim_status", "decision_date", "manufacturer_recovery_amount", "currency_code", "days_to_resolution", "repeat_claim_flag"],
    "complaints": ["complaint_id", "customer_ref", "branch_id", "sale_id", "service_id", "claim_id", "complaint_date", "complaint_channel", "complaint_category", "severity", "complaint_text", "resolution_status", "resolution_date", "resolution_cost", "currency_code", "escalated_flag", "days_to_resolution"],
    "satisfaction": ["survey_id", "customer_ref", "branch_id", "sale_id", "service_id", "complaint_id", "survey_date", "survey_type", "overall_score", "nps_score", "product_score", "staff_score", "timeliness_score", "value_score", "recommend_flag", "response_channel", "comment_text"],
}

PK = {
    "branches": "branch_id", "models": "model_id", "salespeople": "salesperson_id",
    "inventory": "inventory_id", "sales": "sale_id", "service_records": "service_id",
    "warranty_claims": "claim_id", "complaints": "complaint_id", "satisfaction": "survey_id",
}

DEFECT_TARGETS = {
    "name_variants": 140,
    "exact_duplicate_rows": 90,
    "near_duplicate_records": 65,
    "missing_prices_or_costs": 180,
    "invalid_dates": 110,
    "negative_costs_or_prices": 75,
    "orphan_foreign_keys": 85,
    "duplicate_vins": 28,
    "malformed_vins": 35,
    "inconsistent_category_labels": 135,
    "missing_required_descriptive_values": 100,
    "arithmetic_inconsistencies": 95,
    "invalid_satisfaction_scores": 45,
    "status_date_contradictions": 60,
    "implausible_mileage_or_labor_hours": 48,
}

FIRST_NAMES = ["Ama", "Kojo", "Akosua", "Kwame", "Abena", "Kofi", "Adwoa", "Yaw", "Efua", "Nana", "Esi", "Daniel", "Linda", "Michael", "Grace", "Samuel", "Priscilla", "Joseph", "Mabel", "David"]
LAST_NAMES = ["Mensah", "Owusu", "Boateng", "Asare", "Osei", "Addo", "Agyeman", "Appiah", "Darko", "Acheampong", "Arthur", "Antwi", "Sarpong", "Opoku", "Tetteh", "Quaye", "Amankwah", "Badu", "Frimpong", "Gyasi"]
CITIES = [
    ("Accra Central", "Accra", "Greater Accra"), ("Tema Harbour", "Tema", "Greater Accra"),
    ("East Legon", "Accra", "Greater Accra"), ("Kumasi Central", "Kumasi", "Ashanti"),
    ("Suame", "Kumasi", "Ashanti"), ("Takoradi", "Takoradi", "Western"),
    ("Cape Coast", "Cape Coast", "Central"), ("Tamale", "Tamale", "Northern"),
    ("Koforidua", "Koforidua", "Eastern"), ("Ho", "Ho", "Volta"),
    ("Sunyani", "Sunyani", "Bono"), ("Techiman", "Techiman", "Bono East"),
    ("Wa", "Wa", "Upper West"), ("Bolgatanga", "Bolgatanga", "Upper East"),
    ("Kasoa", "Kasoa", "Central"),
]
MODEL_LINES = [
    ("Aster", "Luma", "Sedan", "Sedan", 5, 185_000),
    ("Aster", "Luma Cross", "SUV", "Crossover", 5, 235_000),
    ("Aster", "Vela", "Hatchback", "Hatchback", 5, 155_000),
    ("Boreal", "Atlas", "SUV", "SUV", 7, 320_000),
    ("Boreal", "Atlas Sport", "SUV", "Crossover", 5, 285_000),
    ("Boreal", "Terra", "Pickup", "Double-cab pickup", 5, 345_000),
    ("Crest", "Metro", "Sedan", "Sedan", 5, 170_000),
    ("Crest", "Voyager", "Van", "Minivan", 8, 310_000),
    ("Crest", "Pulse", "Hatchback", "Hatchback", 5, 145_000),
    ("Dune", "Ranger", "Pickup", "Double-cab pickup", 5, 360_000),
    ("Dune", "Sahara", "SUV", "SUV", 7, 390_000),
    ("Dune", "Trail", "SUV", "Crossover", 5, 260_000),
    ("Elara", "Eon", "Sedan", "Sedan", 5, 265_000),
    ("Elara", "Eon X", "SUV", "Crossover", 5, 335_000),
    ("Elara", "Spark", "Hatchback", "Hatchback", 5, 215_000),
    ("Forge", "Cargo", "Van", "Panel van", 3, 295_000),
    ("Forge", "Workstar", "Pickup", "Single-cab pickup", 3, 275_000),
    ("Forge", "Familia", "Van", "Minivan", 8, 285_000),
]


def iso(value: date) -> str:
    return value.isoformat()


def money(value: float) -> str:
    return f"{value:.2f}"


def weighted(options: list[Any], weights: list[float]) -> Any:
    return RNG.choices(options, weights=weights, k=1)[0]


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=RNG.randint(0, (end - start).days))


def seasonal_date() -> date:
    months = []
    weights = []
    month_weight = {1: .84, 2: .96, 3: 1.10, 4: 1.14, 5: 1.00, 6: .96, 7: .91, 8: .95, 9: 1.00, 10: 1.04, 11: 1.10, 12: 1.31}
    cursor = date(2023, 1, 1)
    while cursor <= END_DATE:
        months.append((cursor.year, cursor.month))
        year_growth = {2023: 1.0, 2024: 1.08, 2025: 1.13}[cursor.year]
        weights.append(month_weight[cursor.month] * year_growth)
        cursor = date(cursor.year + (cursor.month == 12), cursor.month % 12 + 1, 1)
    year, month = weighted(months, weights)
    if month == 12:
        last = date(year, 12, 31)
    else:
        last = date(year, month + 1, 1) - timedelta(days=1)
    if last > END_DATE:
        last = END_DATE
    return date(year, month, RNG.randint(1, last.day))


def customer_ref(number: int) -> str:
    digest = hashlib.sha1(f"versal-{SEED}-{number}".encode()).hexdigest()[:10].upper()
    return f"CUS-{digest}"


def make_vin(number: int) -> str:
    alphabet = "ABCDEFGHJKLMNPRSTUVWXYZ0123456789"
    local = random.Random(SEED + number * 7919)
    return "VMG" + "".join(local.choice(alphabet) for _ in range(8)) + f"{number:06d}"[-6:]


def build_clean_data() -> dict[str, list[dict[str, Any]]]:
    data: dict[str, list[dict[str, Any]]] = {name: [] for name in FIELDS}

    # Branches: capacity drives downstream sales and service volume.
    branch_weights = [1.65, 1.35, 1.30, 1.25, 1.05, .90, .76, .72, .67, .61, .57, .52, .42, .39, .84]
    for i, (name, city, region) in enumerate(CITIES, 1):
        branch_type = "full_service" if i <= 10 else ("sales_only" if i <= 13 else "service_only")
        opened = date(2008, 1, 1) + timedelta(days=RNG.randint(0, 14 * 365))
        data["branches"].append({
            "branch_id": i, "branch_code": f"VM-B{i:02d}", "branch_name": f"versalMotors {name}",
            "branch_type": branch_type, "address_line": f"{RNG.randint(1, 220)} {city} Motor Road",
            "city": city, "region": region, "country_code": "GH", "opened_date": iso(opened),
            "floor_capacity": RNG.randint(18, 65), "service_bay_count": 0 if branch_type == "sales_only" else RNG.randint(4, 16),
            "manager_name": f"{RNG.choice(FIRST_NAMES)} {RNG.choice(LAST_NAMES)}", "active_flag": True,
        })

    # Three model years for eighteen product lines.
    for line_index, line in enumerate(MODEL_LINES):
        maker, model_name, segment, body, seats, base_price = line
        for model_year in (2023, 2024, 2025):
            model_id = line_index * 3 + model_year - 2022
            ev_line = line_index in {12, 13, 14}
            hybrid_line = line_index in {1, 4, 7}
            powertrain = "EV" if ev_line else ("Hybrid" if hybrid_line else weighted(["Petrol", "Diesel"], [4, 1]))
            trim = ["Core", "Comfort", "Premium"][(model_year + line_index) % 3]
            price = base_price * (1 + .075 * (model_year - 2023)) * ({"Core": .95, "Comfort": 1.0, "Premium": 1.12}[trim])
            data["models"].append({
                "model_id": model_id, "manufacturer": maker, "model_name": model_name, "model_year": model_year,
                "trim_name": trim, "vehicle_segment": segment, "body_style": body, "powertrain": powertrain,
                "transmission": "Single-speed" if ev_line else weighted(["Automatic", "CVT", "Manual"], [6, 2, 1]),
                "engine_size_l": "" if ev_line else weighted(["1.5", "1.8", "2.0", "2.5", "3.0"], [3, 3, 4, 2, 1]),
                "battery_capacity_kwh": weighted(["52.0", "64.0", "78.0"], [2, 4, 2]) if ev_line else "",
                "fuel_efficiency": money(RNG.uniform(13, 22) if not ev_line else RNG.uniform(5.2, 7.0)),
                "seating_capacity": seats, "msrp": money(price), "currency_code": "GHS",
                "launch_date": f"{model_year - 1}-09-01", "discontinued_date": "", "active_flag": model_year == 2025,
            })

    sales_branch_ids = list(range(1, 14))
    for i in range(1, BASE_COUNTS["salespeople"] + 1):
        branch_id = weighted(sales_branch_ids, branch_weights[:13])
        hire = random_date(date(2014, 1, 1), date(2025, 3, 31))
        terminated = RNG.random() < .18 and hire < date(2024, 10, 1)
        termination = random_date(max(hire + timedelta(days=180), START_DATE), END_DATE) if terminated else None
        title = weighted(["Sales Consultant", "Senior Sales Consultant", "Fleet Specialist", "Sales Supervisor"], [65, 20, 9, 6])
        data["salespeople"].append({
            "salesperson_id": i, "employee_code": f"VM-E{i:04d}", "branch_id": branch_id,
            "first_name": RNG.choice(FIRST_NAMES), "last_name": RNG.choice(LAST_NAMES),
            "gender": weighted(["Female", "Male"], [48, 52]), "hire_date": iso(hire),
            "termination_date": iso(termination) if termination else "", "job_title": title,
            "experience_years_at_hire": RNG.randint(0, 13), "monthly_target_units": RNG.randint(7, 15),
            "commission_rate": f"{RNG.uniform(.012, .035):.4f}", "active_flag": not terminated,
        })

    # Inventory arrivals are concentrated just ahead of seasonal sales peaks.
    model_weights = []
    for model in data["models"]:
        segment_factor = {"SUV": 1.45, "Sedan": 1.15, "Pickup": .92, "Hatchback": .85, "Van": .64}[model["vehicle_segment"]]
        year_factor = {2023: .85, 2024: 1.1, 2025: 1.28}[model["model_year"]]
        model_weights.append(segment_factor * year_factor)
    for i in range(1, BASE_COUNTS["inventory"] + 1):
        model = weighted(data["models"], model_weights)
        branch_id = weighted(sales_branch_ids, branch_weights[:13])
        acquisition = random_date(date(2022, 10, 1), date(2025, 6, 10))
        # Simulated Apr-May 2024 supply constraint lengthens lead times.
        lead = RNG.randint(12, 42) + (RNG.randint(18, 35) if date(2024, 4, 1) <= acquisition <= date(2024, 5, 31) else 0)
        arrival = min(acquisition + timedelta(days=lead), END_DATE)
        condition = weighted(["new", "demo", "used"], [88, 5, 7])
        odometer = RNG.randint(0, 75) if condition == "new" else (RNG.randint(150, 6_000) if condition == "demo" else RNG.randint(8_000, 95_000))
        msrp = float(model["msrp"])
        acquisition_cost = msrp * RNG.uniform(.76, .86)
        listed = msrp * RNG.uniform(.98, 1.055)
        data["inventory"].append({
            "inventory_id": i, "vin": make_vin(i), "model_id": model["model_id"], "branch_id": branch_id,
            "exterior_color": weighted(["White", "Black", "Silver", "Grey", "Blue", "Red", "Green", "Bronze"], [24, 18, 18, 15, 10, 8, 4, 3]),
            "interior_color": weighted(["Black", "Grey", "Tan", "Brown"], [55, 23, 15, 7]),
            "manufacture_date": iso(max(date(model["model_year"] - 1, 6, 1), acquisition - timedelta(days=RNG.randint(25, 150)))),
            "acquisition_date": iso(acquisition), "arrival_date": iso(arrival), "condition": condition,
            "odometer_km": odometer, "acquisition_cost": money(acquisition_cost), "listed_price": money(listed),
            "currency_code": "GHS", "inventory_status": "available", "sold_date": "",
            "days_in_inventory": (END_DATE - arrival).days, "record_updated_at": "2025-06-30T23:59:59",
        })

    # Select saleable stock and then order by a seasonal date to retain coherence.
    candidate_inventory = [r for r in data["inventory"] if date.fromisoformat(r["arrival_date"]) <= END_DATE - timedelta(days=2)]
    RNG.shuffle(candidate_inventory)
    sold_stock = candidate_inventory[:BASE_COUNTS["sales"]]
    salesperson_by_branch = defaultdict(list)
    for person in data["salespeople"]:
        salesperson_by_branch[person["branch_id"]].append(person)
    sale_dates = sorted(seasonal_date() for _ in range(BASE_COUNTS["sales"]))
    for i, (vehicle, proposed_date) in enumerate(zip(sold_stock, sale_dates), 1):
        arrival = date.fromisoformat(vehicle["arrival_date"])
        sale_date = max(proposed_date, arrival + timedelta(days=RNG.randint(1, 16)))
        if sale_date > END_DATE:
            sale_date = END_DATE
        people = salesperson_by_branch[vehicle["branch_id"]]
        person = RNG.choice(people)
        status = weighted(["completed", "cancelled", "returned"], [97, 2, 1])
        listed = float(vehicle["listed_price"])
        age_days = (sale_date - arrival).days
        discount_rate = min(.18, max(0, RNG.gauss(.035 + max(0, age_days - 75) * .00035, .018)))
        gross = listed * RNG.uniform(.985, 1.005)
        discount = gross * discount_rate
        net = gross - discount
        tax = net * .15
        fees = RNG.uniform(850, 2_600)
        total = net + tax + fees
        cust_number = RNG.randint(1, 15_800)
        delivery = sale_date + timedelta(days=RNG.randint(1, 12)) if status != "cancelled" else None
        has_trade_in = RNG.random() < .21
        data["sales"].append({
            "sale_id": i, "inventory_id": vehicle["inventory_id"], "branch_id": vehicle["branch_id"],
            "salesperson_id": person["salesperson_id"], "customer_ref": customer_ref(cust_number),
            "sale_date": iso(sale_date), "delivery_date": iso(min(delivery, END_DATE)) if delivery else "",
            "sale_status": status, "sales_channel": weighted(["showroom", "website_lead", "telephone", "fleet"], [62, 18, 7, 13]),
            "customer_type": weighted(["individual", "business", "government", "fleet"], [72, 15, 4, 9]),
            "gross_price": money(gross), "discount_amount": money(discount), "net_sale_price": money(net),
            "tax_amount": money(tax), "fees_amount": money(fees), "total_sale_price": money(total),
            "currency_code": "GHS", "payment_method": weighted(["cash", "finance", "lease"], [31, 60, 9]),
            "finance_term_months": weighted([24, 36, 48, 60], [10, 34, 37, 19]) if RNG.random() < .69 else "",
            "trade_in_flag": has_trade_in, "trade_in_value": money(RNG.uniform(22_000, 135_000)) if has_trade_in else "",
            "created_at": f"{iso(sale_date)}T{RNG.randint(8, 18):02d}:{RNG.randint(0, 59):02d}:00",
        })
        if status == "completed":
            vehicle["inventory_status"] = "sold"
            vehicle["sold_date"] = iso(sale_date)
            vehicle["days_in_inventory"] = max(0, (sale_date - arrival).days)

    completed_sales = [r for r in data["sales"] if r["sale_status"] == "completed"]
    inv_by_id = {r["inventory_id"]: r for r in data["inventory"]}
    service_sales = RNG.choices(completed_sales, weights=[max(1, (END_DATE - date.fromisoformat(s["sale_date"])).days) for s in completed_sales], k=BASE_COUNTS["service_records"])
    last_mileage: dict[int, int] = defaultdict(int)
    for i, sale in enumerate(service_sales, 1):
        sold = date.fromisoformat(sale["sale_date"])
        if sold >= END_DATE:
            opened = END_DATE
        else:
            days_after = min((END_DATE - sold).days, max(20, int(RNG.expovariate(1 / 240))))
            opened = sold + timedelta(days=days_after)
        service_type = weighted(["scheduled", "repair", "recall", "inspection", "bodywork"], [52, 27, 5, 11, 5])
        duration = RNG.randint(0, 2) if service_type in {"scheduled", "inspection"} else RNG.randint(1, 12)
        closed = min(opened + timedelta(days=duration), END_DATE)
        status = "open" if opened > END_DATE - timedelta(days=3) and RNG.random() < .35 else "completed"
        if status == "open":
            closed_value = ""
        else:
            closed_value = iso(closed)
        inventory_id = sale["inventory_id"]
        elapsed = max(1, (opened - sold).days)
        mileage = max(last_mileage[inventory_id] + RNG.randint(200, 2_500), int(elapsed * RNG.uniform(22, 58)))
        last_mileage[inventory_id] = mileage
        labor_hours = max(.5, RNG.lognormvariate(.55 if service_type == "repair" else .10, .65))
        labor = labor_hours * RNG.uniform(170, 290)
        parts = RNG.uniform(60, 650) if service_type in {"scheduled", "inspection"} else RNG.lognormvariate(7.2, .85)
        misc = RNG.uniform(15, 180)
        total = labor + parts + misc
        warranty_share = total if service_type in {"recall"} or (service_type == "repair" and RNG.random() < .18) else 0
        data["service_records"].append({
            "service_id": i, "inventory_id": inventory_id, "branch_id": weighted(list(range(1, 16)), branch_weights),
            "sale_id": sale["sale_id"], "customer_ref": sale["customer_ref"], "service_open_date": iso(opened),
            "service_close_date": closed_value, "service_type": service_type, "service_status": status,
            "odometer_km": mileage, "labor_hours": f"{labor_hours:.1f}", "labor_cost": money(labor),
            "parts_cost": money(parts), "misc_cost": money(misc), "total_service_cost": money(total),
            "customer_pay_amount": money(total - warranty_share), "warranty_pay_amount": money(warranty_share),
            "currency_code": "GHS", "technician_team": f"TEAM-{RNG.randint(1, 24):02d}",
            "repeat_repair_flag": service_type == "repair" and RNG.random() < .09,
        })

    # Claims deliberately overrepresent two reliability cohorts.
    service_weights = []
    for service in data["service_records"]:
        model_id = inv_by_id[service["inventory_id"]]["model_id"]
        elevated = model_id in {14, 15, 31, 32}
        service_weights.append(4.5 if elevated else (2.0 if service["service_type"] in {"repair", "recall"} else .45))
    # Weighted sampling without replacement is approximated by keys.
    claim_services = sorted(data["service_records"], key=lambda r: RNG.random() ** (1 / service_weights[r["service_id"] - 1]), reverse=True)[:BASE_COUNTS["warranty_claims"]]
    for i, service in enumerate(claim_services, 1):
        opened = date.fromisoformat(service["service_open_date"])
        claim_date = min(opened + timedelta(days=RNG.randint(0, 5)), END_DATE)
        category = weighted(["engine", "transmission", "electrical", "battery", "suspension", "infotainment", "body_hardware"], [17, 14, 24, 10, 12, 13, 10])
        amount = float(service["total_service_cost"]) * RNG.uniform(.85, 1.18)
        status = weighted(["approved", "partially_approved", "denied"], [65, 15, 20])
        approved = amount if status == "approved" else (amount * RNG.uniform(.35, .78) if status == "partially_approved" else 0)
        resolution_days = RNG.randint(3, 24) + (RNG.randint(10, 28) if category in {"transmission", "battery"} else 0)
        decision = min(claim_date + timedelta(days=resolution_days), END_DATE)
        data["warranty_claims"].append({
            "claim_id": i, "service_id": service["service_id"], "inventory_id": service["inventory_id"],
            "sale_id": service["sale_id"], "branch_id": service["branch_id"], "claim_date": iso(claim_date),
            "failure_category": category, "claim_description": f"Customer reported {category.replace('_', ' ')} failure; diagnosis completed.",
            "claim_amount": money(amount), "approved_amount": money(approved), "claim_status": status,
            "decision_date": iso(decision), "manufacturer_recovery_amount": money(approved * RNG.uniform(.82, 1.0)),
            "currency_code": "GHS", "days_to_resolution": (decision - claim_date).days,
            "repeat_claim_flag": RNG.random() < .075,
        })

    # Complaints are sampled from sales/service/claims with operational drivers.
    claims = data["warranty_claims"]
    services = data["service_records"]
    for i in range(1, BASE_COUNTS["complaints"] + 1):
        source = weighted(["sale", "service", "claim"], [38, 45, 17])
        sale_id: Any = ""; service_id: Any = ""; claim_id: Any = ""
        if source == "sale":
            sale = RNG.choice(data["sales"]); sale_id = sale["sale_id"]; base = date.fromisoformat(sale["sale_date"]); branch = sale["branch_id"]; cust = sale["customer_ref"]
            category = weighted(["delivery", "billing", "staff", "product"], [39, 19, 14, 28])
        elif source == "service":
            service = RNG.choice(services); service_id = service["service_id"]; sale_id = service["sale_id"]; base = date.fromisoformat(service["service_open_date"]); branch = service["branch_id"]; cust = service["customer_ref"]
            category = weighted(["service_delay", "billing", "staff", "product"], [38, 20, 15, 27])
        else:
            claim = RNG.choice(claims); claim_id = claim["claim_id"]; service_id = claim["service_id"]; sale_id = claim["sale_id"]; base = date.fromisoformat(claim["claim_date"]); branch = claim["branch_id"]
            service = services[int(service_id) - 1]; cust = service["customer_ref"]; category = "warranty"
        complaint_date = min(base + timedelta(days=RNG.randint(1, 35)), END_DATE)
        severity = weighted(["low", "medium", "high", "critical"], [32, 46, 18, 4])
        resolution_status = weighted(["resolved", "investigating", "open", "rejected"], [76, 9, 9, 6])
        resolution_days = RNG.randint(1, 8) + ({"low": 0, "medium": 3, "high": 10, "critical": 14}[severity])
        resolved_date = min(complaint_date + timedelta(days=resolution_days), END_DATE) if resolution_status in {"resolved", "rejected"} else None
        data["complaints"].append({
            "complaint_id": i, "customer_ref": cust, "branch_id": branch, "sale_id": sale_id, "service_id": service_id,
            "claim_id": claim_id, "complaint_date": iso(complaint_date),
            "complaint_channel": weighted(["phone", "email", "website", "in_person", "social"], [38, 27, 17, 13, 5]),
            "complaint_category": category, "severity": severity,
            "complaint_text": f"Customer raised a {severity} concern regarding {category.replace('_', ' ')}.",
            "resolution_status": resolution_status, "resolution_date": iso(resolved_date) if resolved_date else "",
            "resolution_cost": money(RNG.uniform(0, 800) * {"low": .4, "medium": 1, "high": 2.5, "critical": 5}[severity]),
            "currency_code": "GHS", "escalated_flag": severity in {"high", "critical"} and RNG.random() < .72,
            "days_to_resolution": (resolved_date - complaint_date).days if resolved_date else "",
        })

    # Responses over-sample both unhappy and very happy interactions.
    complaints = data["complaints"]
    for i in range(1, BASE_COUNTS["satisfaction"] + 1):
        survey_type = weighted(["post_sale", "post_service", "complaint_follow_up"], [40, 48, 12])
        sale_id: Any = ""; service_id: Any = ""; complaint_id: Any = ""
        if survey_type == "post_sale":
            source = RNG.choice(data["sales"]); sale_id = source["sale_id"]; branch = source["branch_id"]; cust = source["customer_ref"]; base = date.fromisoformat(source["sale_date"])
            center = 8.2 - (1.4 if source["sale_status"] != "completed" else 0)
        elif survey_type == "post_service":
            source = RNG.choice(services); service_id = source["service_id"]; branch = source["branch_id"]; cust = source["customer_ref"]; base = date.fromisoformat(source["service_close_date"] or source["service_open_date"])
            center = 7.8 - (1.7 if source["repeat_repair_flag"] else 0) - (.8 if source["service_status"] == "open" else 0)
        else:
            source = RNG.choice(complaints); complaint_id = source["complaint_id"]; branch = source["branch_id"]; cust = source["customer_ref"]; base = date.fromisoformat(source["resolution_date"] or source["complaint_date"])
            center = 7.1 if source["resolution_status"] == "resolved" else 4.7
        if base >= date(2024, 10, 1):
            center += .35  # Process improvement.
        overall = max(1, min(10, round(RNG.gauss(center, 1.55))))
        nps = max(0, min(10, round(RNG.gauss(overall, 1.0))))
        score5 = lambda offset=0: max(1, min(5, round((overall + offset) / 2 + RNG.gauss(0, .55))))
        survey_date = min(base + timedelta(days=RNG.randint(1, 18)), END_DATE)
        data["satisfaction"].append({
            "survey_id": i, "customer_ref": cust, "branch_id": branch, "sale_id": sale_id,
            "service_id": service_id, "complaint_id": complaint_id, "survey_date": iso(survey_date),
            "survey_type": survey_type, "overall_score": overall, "nps_score": nps,
            "product_score": score5() if survey_type == "post_sale" else "", "staff_score": score5(),
            "timeliness_score": score5(-1 if survey_type == "complaint_follow_up" else 0), "value_score": score5(),
            "recommend_flag": nps >= 7, "response_channel": weighted(["sms", "email", "web", "phone"], [42, 33, 18, 7]),
            "comment_text": "Very positive experience." if overall >= 9 else ("Service did not meet expectations." if overall <= 4 else ""),
        })
    return data


def inject_defects(data: dict[str, list[dict[str, Any]]]) -> list[dict[str, str]]:
    defects: list[dict[str, str]] = []
    used: dict[str, set[tuple[int, str]]] = defaultdict(set)

    def record(kind: str, table: str, row: dict[str, Any], field: str, detail: str) -> None:
        defects.append({"type": kind, "table": table, "record_id": str(row[PK[table]]), "field": field, "detail": detail})

    def select(table: str, count: int, field: str, predicate=lambda row: True) -> list[dict[str, Any]]:
        candidates = [r for r in data[table] if predicate(r) and (id(r), field) not in used[table]]
        chosen = RNG.sample(candidates, count)
        used[table].update((id(r), field) for r in chosen)
        return chosen

    # 140 name variants: 10 branch, 40 model, 90 salesperson fields.
    for table, count, field in [("branches", 10, "branch_name"), ("models", 40, "model_name"), ("salespeople", 90, "last_name")]:
        for index, row in enumerate(select(table, count, field)):
            original = str(row[field])
            variants = [original.upper(), original.lower(), original.replace(" ", "-"), original + " ", original.replace("versalMotors", "Versal Motors")]
            row[field] = variants[index % len(variants)]
            record("name_variants", table, row, field, f"{original!r} -> {row[field]!r}")

    # Missing numeric amounts.
    missing_plan = [("inventory", "listed_price", 35), ("inventory", "acquisition_cost", 30), ("sales", "total_sale_price", 55), ("service_records", "total_service_cost", 40), ("warranty_claims", "claim_amount", 20)]
    for table, field, count in missing_plan:
        for row in select(table, count, field, lambda r, f=field: r[f] != ""):
            old = row[field]; row[field] = ""; record("missing_prices_or_costs", table, row, field, f"removed {old}")

    # Invalid but parseable chronological dates plus ten malformed calendar strings.
    date_plan = [
        ("sales", "sale_date", 35, lambda r: (date.fromisoformat(next(x["arrival_date"] for x in data["inventory"] if x["inventory_id"] == r["inventory_id"])) - timedelta(days=10)).isoformat(), "sale before inventory arrival"),
        ("service_records", "service_close_date", 30, lambda r: (date.fromisoformat(r["service_open_date"]) - timedelta(days=4)).isoformat(), "close before open"),
        ("warranty_claims", "claim_date", 20, lambda r: "2022-12-15", "claim before dataset transaction period"),
        ("complaints", "resolution_date", 15, lambda r: (date.fromisoformat(r["complaint_date"]) - timedelta(days=3)).isoformat(), "resolution before complaint"),
    ]
    for table, field, count, transform, detail in date_plan:
        for row in select(table, count, field):
            row[field] = transform(row); record("invalid_dates", table, row, field, detail)
    for row in select("satisfaction", 10, "survey_date"):
        row["survey_date"] = "2025-02-30"; record("invalid_dates", "satisfaction", row, "survey_date", "nonexistent calendar date")

    negative_plan = [("inventory", "acquisition_cost", 20), ("sales", "net_sale_price", 15), ("service_records", "parts_cost", 20), ("warranty_claims", "approved_amount", 10), ("complaints", "resolution_cost", 10)]
    for table, field, count in negative_plan:
        for row in select(table, count, field, lambda r, f=field: r[f] not in {"", "0.00"}):
            row[field] = money(-abs(float(row[field]))); record("negative_costs_or_prices", table, row, field, "positive amount made negative")

    orphan_plan = [("salespeople", "branch_id", 8, 9001), ("inventory", "model_id", 12, 9002), ("inventory", "branch_id", 10, 9003), ("sales", "salesperson_id", 15, 9004), ("service_records", "inventory_id", 15, 9005), ("warranty_claims", "service_id", 10, 9006), ("complaints", "claim_id", 8, 9007), ("satisfaction", "complaint_id", 7, 9008)]
    for table, field, count, bad_key in orphan_plan:
        predicate = (lambda r, f=field: r[f] != "") if field in {"claim_id", "complaint_id"} else (lambda r: True)
        for row in select(table, count, field, predicate):
            row[field] = bad_key; record("orphan_foreign_keys", table, row, field, f"set to nonexistent key {bad_key}")

    inv_rows = select("inventory", 28, "vin")
    donors = RNG.sample([r for r in data["inventory"] if r not in inv_rows], 28)
    for row, donor in zip(inv_rows, donors):
        row["vin"] = donor["vin"]; record("duplicate_vins", "inventory", row, "vin", f"duplicates inventory_id {donor['inventory_id']}")
    malformed = ["BADVIN", "1I0OQ234567890123", "TOO-LONG-VIN-000001", "", "1234567890123456"]
    for index, row in enumerate(select("inventory", 35, "vin")):
        row["vin"] = malformed[index % len(malformed)]; record("malformed_vins", "inventory", row, "vin", "invalid VIN length or characters")

    category_plan = [("branches", "branch_type", 8), ("inventory", "inventory_status", 25), ("sales", "sales_channel", 30), ("service_records", "service_type", 30), ("complaints", "complaint_category", 22), ("satisfaction", "response_channel", 20)]
    for table, field, count in category_plan:
        for index, row in enumerate(select(table, count, field)):
            original = str(row[field]); variants = [original.upper(), original.title(), original + " ", original.replace("_", "-"), original[:3]]
            row[field] = variants[index % len(variants)]; record("inconsistent_category_labels", table, row, field, f"variant of {original!r}")

    description_plan = [("branches", "manager_name", 8), ("models", "manufacturer", 12), ("salespeople", "job_title", 20), ("inventory", "exterior_color", 15), ("sales", "customer_type", 15), ("service_records", "technician_team", 15), ("warranty_claims", "claim_description", 8), ("complaints", "complaint_category", 7)]
    for table, field, count in description_plan:
        for row in select(table, count, field):
            row[field] = ""; record("missing_required_descriptive_values", table, row, field, "required descriptive value removed")

    arithmetic_plan = [("sales", 50), ("service_records", 30), ("warranty_claims", 15)]
    for table, count in arithmetic_plan:
        field = {"sales": "net_sale_price", "service_records": "total_service_cost", "warranty_claims": "approved_amount"}[table]
        for row in select(table, count, field, lambda r, f=field: r[f] != ""):
            row[field] = money(float(row[field]) + 777.77); record("arithmetic_inconsistencies", table, row, field, "component total offset by GHS 777.77")

    score_fields = ["overall_score", "nps_score", "product_score", "staff_score", "timeliness_score", "value_score"]
    for index, row in enumerate(select("satisfaction", 45, "overall_score")):
        field = score_fields[index % len(score_fields)]
        if row[field] == "": field = "overall_score"
        row[field] = [0, -1, 11, 99, 6][index % 5]
        record("invalid_satisfaction_scores", "satisfaction", row, field, "outside field's permitted range")

    contradiction_plan = [("inventory", 20), ("complaints", 20), ("warranty_claims", 20)]
    for table, count in contradiction_plan:
        if table == "inventory":
            rows = select(table, count, "inventory_status", lambda r: r["sold_date"] != "")
            for row in rows: row["inventory_status"] = "available"; record("status_date_contradictions", table, row, "inventory_status", "available despite sold_date")
        elif table == "complaints":
            rows = select(table, count, "resolution_date")
            for row in rows: row["resolution_status"] = "resolved"; row["resolution_date"] = ""; record("status_date_contradictions", table, row, "resolution_date", "resolved without resolution date")
        else:
            rows = select(table, count, "decision_date")
            for row in rows: row["claim_status"] = "approved"; row["decision_date"] = ""; record("status_date_contradictions", table, row, "decision_date", "approved without decision date")

    for index, row in enumerate(select("service_records", 48, "odometer_km")):
        if index < 24:
            row["odometer_km"] = -RNG.randint(1, 50_000); field = "odometer_km"; detail = "negative odometer"
        else:
            row["labor_hours"] = money(RNG.uniform(120, 400)); field = "labor_hours"; detail = "implausibly high labor hours"
        record("implausible_mileage_or_labor_hours", "service_records", row, field, detail)

    # Near duplicates get new surrogate keys, while exact duplicates preserve all values including PK.
    near_plan = [("sales", 20), ("service_records", 25), ("warranty_claims", 8), ("complaints", 5), ("satisfaction", 7)]
    for table, count in near_plan:
        pk = PK[table]; next_id = max(int(r[pk]) for r in data[table]) + 1
        already_dirty = {d["record_id"] for d in defects if d["table"] == table}
        clean_sources = [r for r in data[table][:BASE_COUNTS[table]] if str(r[pk]) not in already_dirty]
        sources = RNG.sample(clean_sources, count)
        for offset, source in enumerate(sources):
            clone = source.copy(); clone[pk] = next_id + offset
            mutable = "created_at" if table == "sales" else ("comment_text" if table == "satisfaction" else FIELDS[table][-1])
            clone[mutable] = str(clone[mutable]) + " "
            data[table].append(clone); record("near_duplicate_records", table, clone, mutable, f"near duplicate of {source[pk]}")

    exact_plan = [("sales", 20), ("service_records", 35), ("warranty_claims", 12), ("complaints", 8), ("satisfaction", 15)]
    for table, count in exact_plan:
        pk = PK[table]
        already_dirty = {d["record_id"] for d in defects if d["table"] == table}
        clean_sources = [r for r in data[table][:BASE_COUNTS[table]] if str(r[pk]) not in already_dirty]
        sources = RNG.sample(clean_sources, count)
        for source in sources:
            data[table].append(source.copy()); record("exact_duplicate_rows", table, source, "entire_row", "second byte-equivalent CSV row added")

    actual = Counter(d["type"] for d in defects)
    if actual != Counter(DEFECT_TARGETS):
        raise AssertionError(f"Defect count mismatch: expected {DEFECT_TARGETS}, got {dict(actual)}")
    return defects


def write_csvs(data: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for table, rows in data.items():
        path = RAW_DIR / f"{table}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS[table], extrasaction="raise", lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        hashes[table] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def validate_generated_data(data: dict[str, list[dict[str, Any]]], defects: list[dict[str, str]]) -> None:
    """Fail fast if generation drifts from the documented contract."""
    exact_by_table = Counter(d["table"] for d in defects if d["type"] == "exact_duplicate_rows")
    near_by_table = Counter(d["table"] for d in defects if d["type"] == "near_duplicate_records")
    for table, rows in data.items():
        expected_rows = BASE_COUNTS[table] + exact_by_table[table] + near_by_table[table]
        if len(rows) != expected_rows:
            raise AssertionError(f"{table}: expected {expected_rows} output rows, got {len(rows)}")
        if any(set(row) != set(FIELDS[table]) for row in rows):
            raise AssertionError(f"{table}: row does not match declared CSV fields")
        serialized = Counter(tuple(str(row[field]) for field in FIELDS[table]) for row in rows)
        duplicate_extras = sum(count - 1 for count in serialized.values() if count > 1)
        if duplicate_extras != exact_by_table[table]:
            raise AssertionError(
                f"{table}: expected {exact_by_table[table]} exact duplicate rows, got {duplicate_extras}"
            )


def write_truth(data: dict[str, list[dict[str, Any]]], defects: list[dict[str, str]], hashes: dict[str, str]) -> None:
    counts = Counter(d["type"] for d in defects)
    by_table_type = Counter((d["type"], d["table"]) for d in defects)
    lines = [
        "# versalMotors generator truth", "",
        "> **PRIVATE QA ARTIFACT.** Do not expose this file to application code, dashboards, prompts, or end users.", "",
        f"- Fixed random seed: `{SEED}`", f"- Clean generation window: `{START_DATE}` through `{END_DATE}` (30 months)",
        "- Currency and market: `GHS`, Ghana", "- CSV encoding/newlines: UTF-8, LF", "",
        "## Output inventory", "", "| Table | Clean base rows | Dirty output rows | SHA-256 |", "|---|---:|---:|---|",
    ]
    for table in FIELDS:
        lines.append(f"| `{table}` | {BASE_COUNTS[table]:,} | {len(data[table]):,} | `{hashes[table]}` |")
    lines += ["", "Dirty output exceeds the clean base by 90 exact duplicate rows and 65 near-duplicate rows.", "", "## Seeded business patterns", "",
        "1. Branch footprint: 15 Ghana locations; branches 1-10 are full-service, 11-13 sales-only, and 14-15 service-only. Branch selection is capacity-weighted, creating persistent size differences.",
        "2. Product catalogue: 18 fictional product lines across model years 2023-2025, producing 54 model/trim rows. SUVs are most popular; vans are lowest volume.",
        "3. Sales seasonality multipliers: Jan .84, Feb .96, Mar 1.10, Apr 1.14, May 1.00, Jun .96, Jul .91, Aug .95, Sep 1.00, Oct 1.04, Nov 1.10, Dec 1.31.",
        "4. Sales trend multipliers: 2023 1.00, 2024 1.08, 2025 H1 1.13. The data therefore contains trend plus random variation, not fixed monthly targets.",
        "5. Apr-May 2024 supply constraint: inventory acquired in these months receives an extra 18-35 arrival lead days.",
        "6. Inventory aging: sale discounts increase after 75 days in stock and are capped at 18%; outgoing/older stock therefore tends to have lower realized prices.",
        "7. Channel mix: showroom dominates; website leads are second; fleet business is concentrated indirectly through the seasonal sales distribution.",
        "8. Service behavior: service likelihood is weighted by vehicle exposure time; scheduled work dominates and repair/body work has longer duration and higher parts cost.",
        "9. Reliability signal: model_ids 14, 15, 31, and 32 have 4.5x warranty-claim selection weight; repair/recall visits have 2x weight and ordinary service .45x.",
        "10. Warranty outcomes: seeded weights are 65% approved, 15% partially approved, and 20% denied; transmission and battery claims receive 10-28 extra resolution days.",
        "11. Complaint drivers: service-delay complaints are common after workshop interactions; warranty-source complaints are explicitly categorized as warranty complaints.",
        "12. Satisfaction drivers: cancelled/returned sales, open or repeat service work, and unresolved complaints lower scores. Interactions from 2024-10-01 gain a +0.35 process-improvement effect.",
        "13. Survey response mix is 40% post-sale, 48% post-service, and 12% complaint follow-up by generation weight; randomness makes realized counts vary.",
        "", "## Injected defect totals", "", "| Defect type | Exact count | Tables affected |", "|---|---:|---|",
    ]
    for kind, expected in DEFECT_TARGETS.items():
        table_bits = [f"{table}: {by_table_type[(kind, table)]}" for table in FIELDS if by_table_type[(kind, table)]]
        lines.append(f"| `{kind}` | {counts[kind]} | {', '.join(table_bits)} |")
    lines += ["", f"Total injected defect instances: **{sum(counts.values()):,}**.", "",
              "Counts are defect instances, not necessarily distinct rows. Exact duplicates share a primary key with their source row; near duplicates have new surrogate keys.", "",
              "## Complete injected-defect ledger", "",
              "Every intentional corruption is listed below. Record IDs refer to the dirty CSV value in that table's primary-key column.", "",
              "| # | Defect type | Table | Record ID | Field | Detail |", "|---:|---|---|---:|---|---|"]
    for number, defect in enumerate(defects, 1):
        safe_detail = defect["detail"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {number} | `{defect['type']}` | `{defect['table']}` | `{defect['record_id']}` | `{defect['field']}` | {safe_detail} |")
    lines += ["", "## Intended relational keys", "",
              "- `salespeople.branch_id -> branches.branch_id`",
              "- `inventory.model_id -> models.model_id`; `inventory.branch_id -> branches.branch_id`",
              "- `sales.inventory_id -> inventory.inventory_id`; `sales.branch_id -> branches.branch_id`; `sales.salesperson_id -> salespeople.salesperson_id`",
              "- `service_records.inventory_id -> inventory.inventory_id`; `service_records.branch_id -> branches.branch_id`; `service_records.sale_id -> sales.sale_id`",
              "- `warranty_claims.service_id -> service_records.service_id`; `inventory_id -> inventory.inventory_id`; `sale_id -> sales.sale_id`; `branch_id -> branches.branch_id`",
              "- `complaints.branch_id -> branches.branch_id`; nullable transaction keys point to sales, service records, and warranty claims",
              "- `satisfaction.branch_id -> branches.branch_id`; nullable source keys point to sales, service records, and complaints",
              "", "The orphan-key entries in the ledger are the only intentionally injected referential-integrity violations; duplicate rows can create repeated PK values by design.", ""]
    TRUTH_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRUTH_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    data = build_clean_data()
    defects = inject_defects(data)
    validate_generated_data(data, defects)
    hashes = write_csvs(data)
    write_truth(data, defects, hashes)
    print(f"Generated {sum(len(rows) for rows in data.values()):,} CSV rows in {RAW_DIR}")
    print(f"Recorded {len(defects):,} injected defect instances in {TRUTH_PATH}")


if __name__ == "__main__":
    main()
