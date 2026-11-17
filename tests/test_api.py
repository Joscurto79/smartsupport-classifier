import unittest
from app import create_app


class TestSmartSupportAPI(unittest.TestCase):
    def setUp(self):
        """Runs automatically before EACH test method to spin up a fresh test client."""
        self.app = create_app()
        self.client = self.app.test_client()

    def test_01_polite_critical_outage(self):
        """Scenario 1: Polite outage must override neutral sentiment and auto-escalate."""
        payload = {
            "ticket_id": "TCK-101",
            "text": "Hello team, our production payment gateway is completely down.",
        }
        response = self.client.post("/api/v1/classify", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["routing_queue"], "Critical_Escalations")
        self.assertFalse(data["requires_manual_triage"])
        self.assertGreaterEqual(data["urgency_score"], 0.80)

    def test_02_grey_zone_manual_triage(self):
        """Scenario 2: Moderate negative issue (0.60 - 0.79) must route to manual triage."""
        payload = {
            "ticket_id": "TCK-102B",
            "text": "The dashboard is slow today and shows a timeout error.",
        }
        response = self.client.post("/api/v1/classify", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["routing_queue"], "Triage_Queue")
        self.assertTrue(data["requires_manual_triage"])
        self.assertLess(data["urgency_score"], 0.80)
        self.assertGreaterEqual(data["urgency_score"], 0.60)

    def test_03_invalid_short_text_guardrail(self):
        """Scenario 3: Text shorter than 5 chars must return HTTP 400 VALIDATION_ERROR."""
        payload = {
            "ticket_id": "TCK-103",
            "text": "hi",
        }
        response = self.client.post("/api/v1/classify", json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["error"], "VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()