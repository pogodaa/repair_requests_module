from app.services.statistics import load_requests_from_excel, calculate_avg_repair_time

def test_avg_repair_time():
    requests = load_requests_from_excel()
    avg = calculate_avg_repair_time(requests)
    assert avg == 178.0  # (2023-01-01 - 2022-07-07) = 178 дней