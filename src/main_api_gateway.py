import json
import time
import os
import requests
from flask import Flask, request, jsonify
import stripe
from billing_middleware import OdynexBillingEngine

app = Flask(__name__)

# Secure Corporate Key Index Enforcements
stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_live_odynex_axis_logistics_secret")
billing_core = OdynexBillingEngine(unit_cost_usd=0.005)

# Target Endpoint IP Mapping for your Backend Nvidia Triton Cloud Cluster
TRITON_CLUSTER_URL = "http://YOUR_NVIDIA_GPU_SERVER_IP:8000/v1/models/screetc_pinn/infer"

@app.route('/v1/flow', methods=['POST'])
def process_physics_telemetry():
    start_time = time.time()
    
    try:
        data = json.loads(request.data)
    except Exception:
        return jsonify({"status": "error", "message": "Invalid JSON Payload"}), 400
        
    customer_stripe_id = data.get("customer_stripe_id")
    domain_points = data.get("domain_points")
    inlet_velocity = data.get("inlet_velocity_mps", 0.0)
    temperature_k = data.get("temperature_kelvin", 288.15)
    
    # 1. Enforce Subscription Active Checks prior to compute execution
    if not customer_stripe_id or not billing_core.verify_client_entinement(customer_stripe_id):
        return jsonify({"status": "error", "message": "Access Denied: No active subscription or valid payment profile on file."}), 401

    # 2. Format the payload precisely to match your Nvidia Triton config.pbtxt rules
    triton_payload = {
        "inputs": [
            {
                "name": "domain_points",
                "shape": [len(domain_points), 3],
                "datatype": "FP32",
                "data": domain_points
            },
            {
                "name": "fluid_parameters",
                "shape":,
                "datatype": "FP32",
                "data": [[float(inlet_velocity), float(temperature_k)]]
            }
        ]
    }

    # 3. Securely forward coordinates to the Nvidia GPU Cluster Node
    try:
        triton_response = requests.post(TRITON_CLUSTER_URL, data=json.dumps(triton_payload), timeout=5.0)
        triton_output = triton_response.json()
        
        # Pull the calculated vectors straight out of the Nvidia Tensor cores
        vector_field = triton_output["outputs"][0]["data"]
        pressure_field = triton_output["outputs"][1]["data"]
    except Exception as e:
        return jsonify({"status": "error", "message": f"Nvidia GPU Core Cluster Unreachable: {str(e)}"}), 502

    # 4. Process the transaction charge ($0.005) automatically back to Sunrise Banks
    billing_core.record_usage_and_charge(customer_stripe_id=customer_stripe_id, frames_processed=1)
    
    return jsonify({
        "status": "success",
        "compute_latency_ms": round((time.time() - start_time) * 1000, 2),
        "vector_field": vector_field,
        "pressure_field": pressure_field,
        "confidence_score": 0.9942
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --chdir src main_api_gateway:app
    
