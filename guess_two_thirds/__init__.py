from otree.api import *


doc = """
a.k.a. Keynesian beauty contest.
Players all guess a number; whoever guesses closest to
2/3 of the average wins.
See https://en.wikipedia.org/wiki/Guess_2/3_of_the_average
"""


class C(BaseConstants):
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 1
    NAME_IN_URL = 'guess_two_thirds'
    JACKPOT = Currency(5)
    ENDOWMENT_UPCOMING_APP = Currency(12)
    GUESS_MAX = 100
    INSTRUCTIONS_TEMPLATE = 'guess_two_thirds/instructions.html'
    GAMESTART_TEMPLATE = 'guess_two_thirds/GameStart_template.html'


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    two_thirds_avg = models.FloatField()
    best_guess = models.IntegerField()
    num_winners = models.IntegerField()


class Player(BasePlayer):
    guess = models.IntegerField(
        min=0, max=C.GUESS_MAX, label="Please pick a number from 0 to 100:"
    )
    is_winner = models.BooleanField(initial=False)


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    guesses = [p.guess for p in players]
    two_thirds_avg = (2 / 3) * sum(guesses) / len(players)
    group.two_thirds_avg = round(two_thirds_avg, 2)
    group.best_guess = min(guesses, key=lambda guess: abs(guess - group.two_thirds_avg))
    winners = [p for p in players if p.guess == group.best_guess]
    group.num_winners = len(winners)
    for p in winners:
        p.is_winner = True
        p.payoff = C.JACKPOT / group.num_winners

    # store everything for upcoming apps
    for p in group.get_players():
        p.participant.vars["guess_group_id"] = p.group.id_in_subsession,
        p.participant.vars["guess_group_my_id"] = p.id_in_group,
        p.participant.vars["guess_my_guess"] = p.guess,
        p.participant.vars["guess_group_guesses"] = sorted([p.guess for p in group.get_players()]),
        p.participant.vars["guess_group_two_thirds"] = group.two_thirds_avg,
        p.participant.vars["guess_best_guess"] = group.best_guess,
        p.participant.vars["guess_is_winner"] = p.guess == group.best_guess,
        p.participant.vars["guess_my_payoff"] = p.payoff,



def two_thirds_avg_history(group: Group):
    return [g.two_thirds_avg for g in group.in_previous_rounds()]


# PAGES

class GroupingWaitePage(WaitPage):
    group_by_arrival_time = True

class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



class Guess(Page):
    form_model = 'player'
    form_fields = ['guess']

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        return {
            "two_thirds_avg_history": two_thirds_avg_history(group),
        }




class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(group: Group): set_payoffs(group)




class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        sorted_guesses = sorted(p.guess for p in group.get_players())
        return {
            "sorted_guesses":sorted_guesses,
        }


page_sequence = [GroupingWaitePage,Introduction, Guess, ResultsWaitPage]
