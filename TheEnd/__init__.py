from otree.api import *


doc = """
TheEnd
"""


class C(BaseConstants):
    NAME_IN_URL = 'TheEnd'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES

class TheEnd(Page):
    pass


page_sequence = [TheEnd]
