import unittest
from unittest.mock import patch
from utils import process_daily_meds, get_meds

class ScraperTests(unittest.TestCase):

    def test_process_daily_meds(self):
        med_elements = [
            "<td>8:00 AM - Medication A (10 mg)</td>",
            "<td>12:00 PM - Medication B (20 mg)</td>",
            "<td>4:00 PM - Medication C (30 mg)</td>"
        ]
        expected_meds = [
            Medication(name="Medication A", modality="", dosage="10", dosage_unit="mg", time="8:00 AM"),
            Medication(name="Medication B", modality="", dosage="20", dosage_unit="mg", time="12:00 PM"),
            Medication(name="Medication C", modality="", dosage="30", dosage_unit="mg", time="4:00 PM")
        ]
        actual_meds = process_daily_meds(med_elements)
        self.assertEqual(actual_meds, expected_meds)

    @patch("scraper.auth_session")
    def test_get_meds(self, mock_session):
        mock_session.get.return_value.content.decode.return_value = "<html>...</html>"
        mock_session.get.return_value.status_code = 200
        url = "https://mychart.emoryhealthcare.org/MyChart-prd/inside.asp?mode=itinerary&tod=1&cat=999&dat=66878"
        get_meds(mock_session, url)
        mock_session.get.assert_called_once_with(url)

if __name__ == "__main__":
    unittest.main()