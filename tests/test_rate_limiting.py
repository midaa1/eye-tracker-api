import json


def test_health_endpoint_is_exempt_from_rate_limiting(client):
    """Health check should never be rate-limited."""
    for _ in range(300):
        resp = client.get("/api/session/health")
        assert resp.status_code == 200


def test_calib_validation_rate_limit(client):
    """calib_validation allows 10 requests/minute, then returns 429."""
    for i in range(10):
        resp = client.post("/api/session/calib_validation", data={})
        # May be 400/500 due to missing data, but NOT 429
        assert resp.status_code != 429, f"Request {i+1} was rate-limited too early"

    resp = client.post("/api/session/calib_validation", data={})
    assert resp.status_code == 429


def test_batch_predict_rate_limit(client):
    """batch_predict allows 30 requests/minute, then returns 429."""
    payload = json.dumps({
        "iris_tracking_data": [],
        "screen_width": 1920,
        "screen_height": 1080,
    })
    for i in range(30):
        resp = client.post(
            "/api/session/batch_predict",
            data=payload,
            content_type="application/json",
        )
        assert resp.status_code != 429, f"Request {i+1} was rate-limited too early"

    resp = client.post(
        "/api/session/batch_predict",
        data=payload,
        content_type="application/json",
    )
    assert resp.status_code == 429


def test_rate_limit_response_body(client):
    """429 responses should indicate rate limiting."""
    for _ in range(10):
        client.post("/api/session/calib_validation", data={})

    resp = client.post("/api/session/calib_validation", data={})
    assert resp.status_code == 429
    assert b"Too Many Requests" in resp.data or b"rate limit" in resp.data.lower()
