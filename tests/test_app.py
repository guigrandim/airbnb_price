import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
    def test_app_uses_saved_model_after_form_submission(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app_test = AppTest.from_file(str(app_path), default_timeout=30).run()

        self.assertEqual(len(app_test.exception), 0)
        self.assertTrue(any("Seu imóvel" in item.value for item in app_test.subheader))
        self.assertGreater(len(app_test.number_input), 15)
        self.assertEqual(len(app_test.selectbox(key="neighbourhood_choice").options), 22)
        self.assertFalse(any(item.label in ["Latitude", "Longitude"] for item in app_test.number_input))
        app_test.selectbox(key="neighbourhood_choice").set_value("Bijlmer-Oost")

        app_test.number_input(key="price_announced_eur").set_value(150.0)
        app_test.button[0].click().run()
        self.assertEqual(len(app_test.exception), 0)
        self.assertEqual(len(app_test.error), 0)
        self.assertIn("price_comparison", app_test.session_state)
        self.assertTrue(any("Como está o preço?" in item.value for item in app_test.subheader))
        self.assertTrue(any("Barra menor = preço menor" in item.value for item in app_test.subheader))
        self.assertGreaterEqual(len(app_test.metric), 3)
        self.assertEqual(len(app_test.radio), 0)
        reference = app_test.session_state["price_comparison"]["result"]["price_reference_eur"]
        for multiplier, expected in [(0.7, "Muito abaixo"), (0.85, "Abaixo"), (1, "Perto"), (1.2, "Acima"), (1.4, "Muito acima")]:
            app_test.number_input(key="price_announced_eur").set_value(reference * multiplier)
            app_test.button[0].click().run()
            self.assertEqual(len(app_test.exception), 0)
            messages = list(app_test.success) + list(app_test.info) + list(app_test.warning)
            self.assertTrue(any(expected in message.value for message in messages))



if __name__ == "__main__":
    unittest.main()
