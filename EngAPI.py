import requests


class Translate:
    def __init__(self):
        self.hostname = "https://ftapi.pythonanywhere.com"\


    def get_translation(self, word):
        params = {
            "sl": "ru",
            "dl": "en",
            "text": word
        }

        response = requests.get(f'{self.hostname}/translate', params=params)
        response.raise_for_status()
        data = response.json()

        translated_data = {
            "source_text": data.get('source-text'),
            "destination_text": data.get('destination-text')
        }

        return translated_data

    def show_text(self, word):
        translated_data = self.get_translation(word)
        return translated_data

    def check_answer(self, word, user_answer):
        correct_translation = self.get_translation(word)['destination_text']
        return user_answer.lower() == correct_translation.lower()
