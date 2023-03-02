from otree.api import *



doc = """
App summarizing the performance and payoffs of the apps used in the experiment. Additionally, 
the option to leave bank credentials is included, which saves entries into an external Form.
"""


class C(BaseConstants):
    NAME_IN_URL = 'payment_info'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# FUNCTIONS
# PAGES
class PaymentInfo(Page):
    @staticmethod
    def vars_for_template(player: Player):

        player.participant.payoff = 0

        # build up payoff

        # initialize a dictionary which is built up dynamically, depending on which apps are in the session
        d = {}
        d["participant_code"] = player.participant.code # participant code
        d["guess_two_thirds"] = False
        d["gf_game"] = False
        task_number = 0
        d["external"] = player.subsession.session.config["external_payment"]

        if "guess_two_thirds" in player.session.config["app_sequence"]:
            task_number = task_number + 1
            # IMPORTANT: Guess game saves participant vars in tuple, so a subscript is needed here
            d["guess_two_thirds"] = True
            d["guess_two_thirds_task_number"] = task_number
            d["guess_group_id"] = player.participant.vars["guess_group_id"][0]
            d["guess_group_my_id"] = player.participant.vars["guess_group_my_id"][0]
            d["guess_my_guess"] = player.participant.vars["guess_my_guess"][0]
            d["guess_group_guesses"] = player.participant.vars["guess_group_guesses"][0]
            d["guess_group_two_thirds"] = player.participant.vars["guess_group_two_thirds"][0]
            d["guess_best_guess"] = player.participant.vars["guess_best_guess"][0]
            d["guess_is_winner"] = player.participant.vars["guess_is_winner"][0]
            d["guess_my_payoff"] = player.participant.vars["guess_my_payoff"][0]

            # payoff
            player.participant.payoff = player.participant.payoff + d["guess_my_payoff"]

        if "gf_game" in player.session.config["app_sequence"]:
            # Results of the market
            task_number = task_number + 1
            d["gf_task_number"] = task_number
            d["gf_game"] = True
            d["gf_chosen_market"] = player.participant.vars["gf_chosen_market"]
            d["gf_chosen_period"] = player.participant.vars["gf_chosen_period"]
            d["gf_chosen_round"] = player.participant.vars["gf_chosen_round"]
            d["gf_number_of_markets"] = list(range(1,5+1)) #player.participant.vars["gf_number_of_markets"]
            d["gf_payoffs"] = list(zip(d["gf_number_of_markets"],player.participant.vars["gf_payoffs"]))
            d["gf_my_payoff"] = player.participant.vars["gf_payoffs"][d["gf_chosen_market"]-1]
            d["gf_predictions"] = player.participant.vars["gf_predictions"][0]
            d["gf_predictions_payoffs"] = player.participant.vars["gf_predictions_payoffs"][0]
            d["gf_token_value"] = d["gf_predictions"][0][2]
            d["gf_number_bidders_current"] = d["gf_predictions"][0][3]
            d["gf_number_bidders_following"] = d["gf_predictions"][0][4]
            d["gf_my_token_value"] = d["gf_predictions"][1][0]
            d["gf_my_number_bidders_current"] = d["gf_predictions"][1][1]
            d["gf_my_number_bidders_following"] = d["gf_predictions"][1][2]
            d["gf_market_plus_prediction"] = d["gf_my_payoff"] + d["gf_predictions_payoffs"]

            # payoff
            player.participant.payoff = player.participant.payoff + d["gf_market_plus_prediction"]

        d["participant_total_payoff"] = player.participant.payoff


        return d

    def js_vars(player: Player):

        d = {}

        if "gf_game" in player.session.config["app_sequence"]:
            d["chosen_market"] = player.participant.vars["gf_chosen_market"]

        return d

class External(Page):

    def is_displayed(player: Player):
        if player.subsession.session.config["external_payment"]:
            return True

    def vars_for_template(player: Player):
        return {
            "participant_code": player.participant.code,
            "total_payoff": player.participant.payoff,

        }

page_sequence = [PaymentInfo,External]
