import json
from model.predict import predict_flood

def handler(request):
    try:
        body = request.json()
        start_date = body.get("startDate")
        end_date = body.get("endDate")
        latitude = float(body.get("latitude"))
        longitude = float(body.get("longitude"))

        if not all([start_date, end_date, latitude, longitude]):
            return {
                "status": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }

        result = predict_flood(start_date, end_date, latitude, longitude)

        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "status": 500,
            "body": json.dumps({"error": str(e)})
        }
