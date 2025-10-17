import json
import os
from datetime import datetime
from model.predict import predict_flood  # import your function

def handler(request):
    try:
        # Parse JSON body
        body = request.json()
        start_date = body.get("startDate")
        end_date = body.get("endDate")
        latitude = body.get("latitude")
        longitude = body.get("longitude")

        if not all([start_date, end_date, latitude, longitude]):
            return {
                "status": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }

        # ✅ Call your model function
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
