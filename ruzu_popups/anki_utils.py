# Copyright 2020 Charles Henry
import aqt


class AnkiUtils:

    def main_window(self):
        return aqt.mw

    def reviewer(self):
        reviewer = self.main_window().reviewer
        if reviewer is None:
            raise Exception('There was an issue getting the reviewer')
        else:
            return reviewer

    def collection(self):
        collection = self.main_window().col
        if collection is None:
            raise Exception('There was an issue getting the collection')
        else:
            return collection

    def selected_deck(self):
        return self.main_window()._selectedDeck()['name']

    def get_decks(self):
        decks = self.collection().decks
        if decks is None:
            raise Exception('There was an issue getting the decks')
        else:
            return decks.all_names_and_ids()

    def scheduler(self):
        scheduler = self.collection().sched
        if scheduler is None:
            raise Exception('There was an issue getting the scheduler')
        else:
            return scheduler

    def review_is_active(self):
        return self.reviewer().card is not None and self.main_window().state == 'review'

    def show_question(self):
        if self.review_is_active():
            self.reviewer()._showQuestion()
            return True
        else:
            return False

    def show_answer(self):
        if self.review_is_active():
            self.main_window().reviewer._showAnswer()
            return True
        else:
            return False

    def answer_card(self, ease):
        if not self.review_is_active():
            return False

        reviewer = self.reviewer()
        if reviewer.state != 'answer':
            return False
        if ease <= 0 or ease > self.scheduler().answerButtons(reviewer.card):
            return False

        reviewer._answerCard(ease)
        return True

    def move_to_overview_state(self, name):
        collection = self.collection()
        if collection is not None:
            deck = collection.decks.by_name(name)
            if deck is not None:
                collection.decks.select(deck['id'])
                try:
                    self.main_window().onOverview()
                except AttributeError:
                    pass
                return True

        return False

    def move_to_review_state(self, name):
        if self.move_to_overview_state(name):
            self.main_window().moveToState('review')
            return True
        else:
            return False

    def get_question(self, card):
        if getattr(card, 'question', None) is None:
            question = card._getQA()['q']
        else:
            question = card.question(),
        return question

    def get_answer(self, card):
        if getattr(card, 'answer', None) is None:
            answer = card._getQA()['a']
        else:
            answer = card.answer()
        return answer

    def get_current_card(self):
        if not self.review_is_active():
            raise Exception('There was an issue getting the current card because review is not currently active.')

        reviewer = self.reviewer()
        card = reviewer.card
        note_type = card.note_type()

        if card is not None:
            button_list = reviewer._answerButtonList()
            response = {
                'card_id': card.id,
                'question': self.get_question(card)[0],  # TODO - Look into why a tuple is returned here...
                'answer': self.get_answer(card),
                'css': note_type['css'],
                'button_list': button_list
            }

        return response

    def get_config(self):
        # Do some checks to ensure the config is valid
        config = self.main_window().addonManager.getConfig(__name__.split('.')[0])
        if not config:
            raise Exception('Config file seems to be invalid, correct or restore default config to resolve this issue.')
        return config

    def set_config(self, config):
        self.main_window().addonManager.writeConfig(__name__.split('.')[0], config)
