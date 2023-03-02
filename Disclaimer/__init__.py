from otree.api import *
import sys
sys.path.append("..")
from experiment.settings import SESSION_CONFIG_DEFAULTS


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'Disclaimer'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    DISCLAIMER_TEMPLATE = 'Disclaimer/Disclaimer_Text.html'
    NEXT_APP = "TheEnd"
    conversion_rate = SESSION_CONFIG_DEFAULTS["real_world_currency_per_point"]
    participation_fee = SESSION_CONFIG_DEFAULTS["participation_fee"]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    q_agree = models.IntegerField(widget=widgets.RadioSelect,
                                  label="How do you wish to proceed?",
                                  choices=[[1, "I agree and want to participate"],
                                           [0, "I disagree and do not want to participate"]])

# FUNCTIONS
def set_continue(player: Player):
    player.participant.vars["continue"] = bool(player.q_agree)
    if player.participant.vars["continue"] is True:
        player.participant.vars["finished"] = -1

# PAGES
class Disclaimer(Page):
    form_model = 'player'
    form_fields = ['q_agree']

    def vars_for_template(player: Player):
        return {
            "conversion_rate": '{:.2f}'.format(C.conversion_rate),
            "participation_fee": '{:.2f}'.format(C.participation_fee),
        }

    def app_after_this_page(player: Player, upcoming_apps):
        set_continue(player)

        if player.participant.vars["continue"] is True:
            return player.session.config["app_sequence"][1]
        else:
            return "TheEnd"

page_sequence = [Disclaimer]
