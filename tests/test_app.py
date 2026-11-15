import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class StreamlitAppTests(unittest.TestCase):
    def test_app_uses_saved_model_after_form_submission(self):
        app_path = Path(__file__).resolve().parents[1] / "app.py"
        app_test = AppTest.from_file(str(app_path), default_timeout=30).run()

        self.assertEqual(len(app_test.exception), 0)
        self.assertTrue(any("Dados do anúncio" in item.value for item in app_test.subheader))
        self.assertGreater(len(app_test.number_input), 15)

        app_test.button[0].click().run()

        self.assertEqual(len(app_test.exception), 0)
        self.assertEqual(len(app_test.error), 0)
        self.assertTrue(
            any("Resultado para o snapshot histórico" in item.value
                for item in app_test.subheader)
        )
        self.assertGreaterEqual(len(app_test.metric), 3)


if __name__ == "__main__":
    unittest.main()
