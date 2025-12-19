import os
import pandas as pd
from datetime import datetime
from typing import List
from app.models import RepairRequest

def load_requests_from_excel() -> List[RepairRequest]:
    """Загружает заявки из Excel-файла, предоставленного заказчиком."""
    path = os.path.join("docs", "src", "Ресурсы", "Кондиционеры_данные", "Заявки", "inputDataRequests.xlsx")
    df = pd.read_excel(path)
    requests = []
    for _, row in df.iterrows():
        requests.append(RepairRequest(
            requestID=int(row["requestID"]),
            startDate=str(row["startDate"]),
            climateTechType=row["climateTechType"],
            climateTechModel=row["climateTechModel"],
            problemDescryption=row["problemDescryption"],
            requestStatus=row["requestStatus"],
            completionDate=str(row["completionDate"]) if pd.notna(row["completionDate"]) else None,
            repairParts=row["repairParts"] if pd.notna(row["repairParts"]) else None,
            masterID=int(row["masterID"]) if pd.notna(row["masterID"]) else None,
            clientID=int(row["clientID"])
        ))
    return requests

def calculate_avg_repair_time(requests: List[RepairRequest]) -> float:
    total_days = 0
    count = 0
    for req in requests:
        if req.requestStatus == "Готова к выдаче" and req.completionDate:
            try:
                start = datetime.strptime(req.startDate, "%Y-%m-%d")
                end = datetime.strptime(req.completionDate, "%Y-%m-%d")
                days = (end - start).days
                if days >= 0:
                    total_days += days
                    count += 1
            except ValueError:
                continue
    return round(total_days / count, 2) if count > 0 else 0.0

def count_completed_requests(requests: List[RepairRequest]) -> int:
    return sum(1 for r in requests if r.requestStatus == "Готова к выдаче")

def get_top_equipment_types(requests: List[RepairRequest], top_n: int = 3) -> dict:
    from collections import Counter
    types = [r.climateTechType for r in requests if r.climateTechType]
    return dict(Counter(types).most_common(top_n))