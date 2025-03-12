import json
import requests
from include.utils.config import API_KEY, CONV_TYPE_ID, API_URL
from .logger import log

def send_customer_journeys_to_api(customer_journeys):
    """Sends customer journeys to the API in batches of 199."""
    chunk_size = 199  
    chunks = [customer_journeys[i:i + chunk_size] for i in range(0, len(customer_journeys), chunk_size)]

    results = []
    partial_errors = []

    for i, chunk in enumerate(chunks):
        log.info(f"🚀🚀 Sending batch {i+1} with {len(chunk)} customer journeys 🚀🚀")
        body = {"customer_journeys": chunk}

        try:
            response = requests.post(
                API_URL,
                data=json.dumps(body),
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": API_KEY,
                },
            )

            response_data = response.json()
            if response.status_code in [200, 206]:
                results.extend(response_data.get("value", []))
                if "partialFailureErrors" in response_data:
                    partial_errors.extend(response_data["partialFailureErrors"])
                log.info(f"✅ Batch {i+1} processed successfully!")

            else:
                log.error(f" ❌ Batch {i+1} failed: {response.status_code} - {response.text}")

        except Exception as e:
            log.error(f"Error in batch {i+1}: {e}")

    return results, partial_errors
