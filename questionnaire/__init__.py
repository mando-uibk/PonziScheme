from otree.api import *
import random


doc = """
Questionnaire at the end of the experiment
"""


class C(BaseConstants):
    NAME_IN_URL = 'questionnaire'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 3
    QUESTIONS = ["FOMO","FINLIT_SOEP"] # Demographics (and belief) always in the end
    FOMO_QUESTIONS = [
        'I fear others make more money than me in this experiment ',
        "It bothers me when I miss an opportunity to make money.",
        "Investing in a new project is most beneficial if I invest early.",
        "When my friends tell me about an exciting investment, I want to invest immediately.",
        "When I see celebrities making an investment, I want to invest immediately.",
        "When I see asset prices skyrocketing, I want to invest immediately.",
        "When asset prices are plummeting, I wish to invest immediately.",
    ]
    FOMO_FORMFIELDS = [
        'fomo_fear_experiment',
        "fomo_miss_opportunity",
        "fomo_early_invest",
        "fomo_friends_exciting",
        "fomo_celebrities",
        "fomo_skyrocketing",
        "fomo_plummeting",
    ]

    FOMO_LIKERT = [
        "0 <br> strongly disagree",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10 <br> strongly agree"
    ]

    FINLIT_QUESTIONS = [
        "Suppose you had €100 in a savings account and the interest rate was 2% per year. After 5 years, how much do you think you "
        "would have in the account if you let the money grow?",
        "Imagine that the interest rate on your savings account was 1% per year and inflation was 2% per year. After 1 year, "
        "with the money in this account, you would be able to buy...",
        "Do you think the following statement is true or false? Buying a single company stock usually provides a safer return "
        "than a stock mutual fund."
    ]

    FINLIT_ANSWERS = [
        ["More than €102", "Exactly €102", "Less than €102", "Don't know", "Refuse to answer"],
        ["More than today", "Exactly the same as today", "Less than today", "Don't know", "Refuse to answer"],
        ["True","False","Don't know", "Refuse to answer"]
    ]

    FINLIT_FORMFIELDS = [
        "finlit_interest",
        "finlit_inflation",
        "finlit_diversification"
    ]

    SOEP_QUESTIONS = [
        "How do you see yourself: Are you a person who is fully prepared to take risks or do you try to avoid taking risks when doing investments?"
    ]

    SOEP_FORMFIELDS = [
        "soep_investments"
    ]

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # Page order
    page_order = models.StringField()

    # FOMO
    fomo_fear_experiment = models.IntegerField()
    fomo_miss_opportunity = models.IntegerField()
    fomo_early_invest = models.IntegerField()
    fomo_friends_exciting = models.IntegerField()
    fomo_celebrities = models.IntegerField()
    fomo_skyrocketing = models.IntegerField()
    fomo_plummeting = models.IntegerField()
    fomo_order = models.StringField()

    # FINLIT
    finlit_questions_order = models.StringField()
    finlit_interest = models.StringField()
    finlit_order_interest = models.StringField()
    finlit_inflation = models.StringField()
    finlit_order_inflation = models.StringField()
    finlit_diversification = models.StringField()
    finlit_order_diversification = models.StringField()
    finlit_score = models.IntegerField()

    # SOEP
    soep_investments = models.IntegerField()

    # DEMOGRAPHICS
    age = models.IntegerField()
    gender = models.StringField()
    math_proficiency = models.IntegerField()


# FUNCTIONS
def creating_session(subsession: Subsession):
    if subsession.round_number == 1:
        for p in subsession.get_players():

            fomo_list = list(zip(C.FOMO_QUESTIONS,C.FOMO_FORMFIELDS)) # combine question with formfields, belief is always the last one
            random.shuffle(fomo_list) # randomize it


            finlit_answer = C.FINLIT_ANSWERS # make a copy of the finlity answers
            for i in range(0,3): # randomize the answers within each questions
                random.shuffle(finlit_answer[i])
            finlit_list = list(zip(C.FINLIT_QUESTIONS,C.FINLIT_ANSWERS,C.FINLIT_FORMFIELDS)) # zip questions with answers and formfields
            random.shuffle(finlit_list) # randomize the finlit questions, soep follows after that and is not randomized

            # safe randomized stuff
            p.participant.vars["fomo_list"] = fomo_list
            p.participant.vars["finlit_list"] = finlit_list
            p.participant.vars["soep_list"] = list(zip(C.SOEP_QUESTIONS,C.SOEP_FORMFIELDS))

            # randomize fomo and finlit page sequence
            round_numbers = list(range(1,C.NUM_ROUNDS))
            random.shuffle(round_numbers)
            questions_rounds = dict(zip(C.QUESTIONS, round_numbers))
            p.participant.vars["questions_rounds"] = questions_rounds
            p.page_order = str(dict(sorted(questions_rounds.items(), key=lambda item: item[1])).keys())[11:-2]



# PAGES

class Fomo(Page):
    def is_displayed(player: Player):
        participant = player.participant
        return player.round_number == participant.vars["questions_rounds"]["FOMO"]

    form_model = 'player'
    form_fields = C.FOMO_FORMFIELDS

    def vars_for_template(player: Player):

        progress = player.round_number/(C.NUM_ROUNDS)*100

        return {
            "progress": progress,
            "fomo_list": player.participant.vars["fomo_list"],
            "round_number": player.round_number,
            "likert_labels": C.FOMO_LIKERT,
        }

    def before_next_page(player: Player, timeout_happened):
        # store order of fomo questions
         player.fomo_order = str([question[1] for question in player.participant.vars["fomo_list"]])

class Finlit_soep(Page):
    def is_displayed(player: Player):
        participant = player.participant
        return player.round_number == participant.vars["questions_rounds"]["FINLIT_SOEP"]

    form_model = 'player'
    form_fields = C.FINLIT_FORMFIELDS + C.SOEP_FORMFIELDS

    def vars_for_template(player: Player):
        progress = player.round_number / (C.NUM_ROUNDS) * 100

        return {
            "progress": progress,
            "finlit_list": player.participant.vars["finlit_list"],
            "soep_list": player.participant.vars["soep_list"],
            "round_number": player.round_number,
            "finlit_order": str([question[2] for question in player.participant.vars["finlit_list"]]),
            "finlit_order_interest": str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_interest']),
            "finlit_order_inflation": str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_inflation']),
            "finlit_order_diversification": str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_diversification'])
        }

    def before_next_page(player: Player, timeout_happened):
        # calculate financial literacy score
        player.finlit_score = sum([
            player.finlit_interest == 'More than €102',
            player.finlit_inflation == 'Less than today',
            player.finlit_diversification == 'False'
        ])

        # store order of questions
        player.finlit_questions_order = str([question[2] for question in player.participant.vars["finlit_list"]])

        # store order of answers in each question
        player.finlit_order_interest = str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_interest'])
        player.finlit_order_inflation = str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_inflation'])
        player.finlit_order_diversification = str([question[1] for question in player.participant.vars["finlit_list"] if question[2] == 'finlit_diversification'])

class Demographics(Page):
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    form_model = 'player'
    form_fields = ['age','gender','math_proficiency']

page_sequence = [
    Fomo,
    Finlit_soep,
    Demographics,
]

