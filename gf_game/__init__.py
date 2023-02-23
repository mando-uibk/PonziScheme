from otree.api import *
import random


doc = """
Subjects are endowed with an earned endowment 12 Euro cash balance. The warming up real-effort task is a beauty contest 
(⅔ of the average), for which the winner receives an additional gain of 5€. The outcome of the contest is revealed only 
at the end of the experiment. However, the endowment is offered to everyone following the beauty contest. 
10 rounds of auctioning, with prices starting at 1 cent, doubling each round to 2, 4, 8, 16, etc. with last round 
5,12 euros (not higher as initial endowment is €10).
"""


class C(BaseConstants):
    NAME_IN_URL = 'gf_game'
    PLAYERS_PER_GROUP = 3
    TREATMENTS = [
        "BASELINE",  # Value of the token is always zero and everybody knows that
        "AMBI_SYM",  # token value is zero or h with unknown probability and everybody has same information set
        "RISK_SYM",  # toke value is zero or h with known probability and everybody has same information
        "AMBI_ASYM",  # token value is zero or h with unknown probability and holder of the token knows true value
        "RISK_ASYM",  # token value is zero or h with known probability and holder of the token knows true value
    ]
    # Number of periods played in each market round (also called stages)
    NUM_STAGES = 11
    # Number of markets (a market round consists of periods or stages)
    NUM_MARKETS = 5
    # Totaling in a number of rounds where the game is played
    NUM_ROUNDS = NUM_STAGES * NUM_MARKETS
    INSTRUCTIONS_TEMPLATE = 'gf_game/instructions.html'
    GAMESTART_TEMPLATE = 'gf_game/GameStart_template.html'
    BID_MIN = cu(0)
    BID_MAX = cu(10)
    # Error margin for the value estimates shown to the players
    BID_NOISE = cu(1)
    # Endowment at each of the beginning market rounds
    ENDOWMENT = cu(12)
    # Start value for the token
    START_VALUE = cu(0.01)
    # Initiate list for token bids
    token_bid_list = [START_VALUE]
    for i in range(0,NUM_STAGES-1):
        token_bid_list.append(token_bid_list[i]*2)
    token_value_list = [cu(10),cu(20),cu(50),cu(100),cu(0)]



class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    treatment = models.StringField(
        doc="""treatment the group is in"""
    )
    uncertainty = models.StringField(
        doc="""uncertainty in the treatment; AMBIGUITY OR RISK"""
    )
    information = models.StringField(
        doc="""information in the treatment; SYMMTERIC OR ASYMMETRIC"""
    )
    token_value = models.CurrencyField(
        doc="""Common value of the token in the current round"""
    )
    token_bid=models.CurrencyField(
        doc="""The value to which players can bid"""
    )
    current_market = models.IntegerField(
        doc="""Current market the group is in"""
    )
    current_stage = models.IntegerField(
        doc="""Current stage (period of the market round) the group is in """
    )
    number_bidders = models.IntegerField(
        doc="""Number of bidders in the round"""
    )
    protocol = models.StringField(
        doc="""protocol what happens in each round"""
    )


class Player(BasePlayer):
    got_token = models.BooleanField(initial=False,
        doc="""Whether player is the owner of the token in the group at the beginning of this stage or not"""
    )
    pocket = models.CurrencyField(
        doc="""The pocket money the player has left at the beginning of the stage"""
    )
    time_spent = models.FloatField(
        doc="""Track time spent on the decision page using javascript"""
    )
    bid = models.BooleanField(
        doc="""Whether player wants to buy(hold if got token) in this stage or not"""
    )
    gets_token = models.BooleanField(initial=False,
        doc="""Whether player gets the token at the end of the stage"""
    )
    belief_other_value = models.IntegerField(
        doc="""Belief of the player that the token value is another value (in all treatments other 
        than BASELINE, that the value is H"""
    )
    belief_bidders_current = models.IntegerField(
        doc="""Belief of the player how manny bidders were in this stage"""
    )
    belief_bidders_following = models.IntegerField(
        doc="""Belief of the player how manny bidders will be in the next stage. Not elicited in the last stage"""
    )

# FUNCTIONS
def creating_session(subsession: Subsession):

    if subsession.round_number == 1:
        print('###############################################')
        print('Creating session: token bid list:',C.token_bid_list)
        print('###############################################')

    # assing values which all groups have in common
    for g in subsession.get_groups():
        g.current_market = int(g.round_number/(C.NUM_STAGES+0.1))+1
        g.current_stage = (lambda x: x % C.NUM_STAGES if x % C.NUM_STAGES !=0 else C.NUM_STAGES) (g.round_number)
        g.token_bid = C.token_bid_list[g.current_stage-1]

        for p in g.get_players():
            if g.current_stage == 1:
                p.pocket = C.ENDOWMENT
                p.participant.vars["payoffs"] = [] # initialize a list for payoffs


def set_winner(group: Group):
    import random

    players = group.get_players()
    group.highest_bid = max([p.bid_amount for p in players])
    players_with_highest_bid = [p for p in players if p.bid_amount == group.highest_bid]
    winner = random.choice(
        players_with_highest_bid
    )  # if tie, winner is chosen at random
    winner.is_winner = True
    for p in players:
        set_payoff(p)


def set_payoff(player: Player):
    group = player.group

    if player.is_winner:
        player.payoff = group.item_value - player.bid_amount
        if player.payoff < 0:
            player.payoff = 0
    else:
        player.payoff = 0

def treatment_setup(group: Group): # randomize treatment for the group
    if group.round_number == 1:
        group.treatment = group.session.config['treatment']
        # RANDOMIZATION: PARAMETER IN SESSION CONFIGS
        if group.session.config['randomize_treatments']:
            group.treatment = random.choice(C.TREATMENTS)
        if group.treatment != "BASELINE":
            group.uncertainty = (lambda x: "AMBIGUITY" if x in ["AMBI_SYM", "AMBI_ASYM"] else "RISK")(group.treatment)
            group.information = (lambda x: "SYMMETRIC" if x in ["AMBI_SYM", "RISK_SYM"] else "ASYMMETRIC")(
                group.treatment)

    # group.treatment = group.in_round(1).treatment
    group.current_market = int(group.round_number / (C.NUM_STAGES + 0.1)) + 1
    group.current_stage = (lambda x: x % C.NUM_STAGES if x % C.NUM_STAGES != 0 else C.NUM_STAGES)(group.round_number)
    group.token_bid = C.token_bid_list[group.current_stage - 1]

    # forward treatment and common values to upcoming rounds
    for i in range(2, C.NUM_ROUNDS + 1):
        group.in_round(i).treatment = group.in_round(1).treatment
        group.in_round(i).uncertainty = group.in_round(1).uncertainty
        group.in_round(i).information = group.in_round(1).information
        group.in_round(i).current_market = int(group.in_round(i).round_number / (C.NUM_STAGES + 0.1)) + 1
        group.in_round(i).current_stage = (lambda x: x % C.NUM_STAGES if x % C.NUM_STAGES != 0 else C.NUM_STAGES)(
            group.in_round(i).round_number)
        group.in_round(i).token_bid = C.token_bid_list[group.in_round(i).current_stage - 1]

def setup_market(group: Group): # setup the token value

    # if BASELINE treatment the token value is always zero in every market
    if group.treatment == "BASELINE":
        group.token_value = 0

        for i in range(1, 11):  # transfer token value across the whole market
            group.in_round(group.round_number + i).token_value = group.in_round(group.round_number).token_value

    else:
        dice_1 = random.choice(range(1,7))
        dice_2 = random.choice(range(1,7))
        dice_3 = random.choice(range(1,7))


        if (dice_1 + dice_2 + dice_3) == 18:
            group.token_value = C.token_value_list[group.current_stage]
        else:
            group.token_value = 0

        print("Group ID", group.id_in_subsession, "Dice_1:", dice_1, "Dice_2:", dice_2, "Dice_3", dice_3)

        for i in range(1,11): # transfer token value across the whole market
            group.in_round(group.round_number+i).token_value = group.in_round(group.round_number).token_value

    # setup for pocket for each player
    for p in group.get_players():
        p.pocket = C.ENDOWMENT
        p.got_token = 0
        p.participant.vars["once_got_token"] = False
        if p.group.treatment != "BASELINE":
            p.participant.vars["dice_rolls"] = [dice_1,dice_2,dice_3]
        else:
            p.participant.vars["dice_rolls"] = False


def set_buyer(group: Group):

    # collect the id of players who bid
    bidders = [p.id_in_group for p in group.get_players() if p.bid == True]
    print("Bidders ID:", bidders)

    # Number of bidders
    group.number_bidders = len(bidders)

    # Check: if nobody bids, market is over
    if group.number_bidders == 0:
        group.protocol = "MARKET ENDS IN T = " + str(group.current_stage)
        # print("MARKET BREAKDOWN!!!!!")
        for p in group.get_players():
            p.participant.vars["market_continue"] = False # set market conitune variable to false
            if p.got_token == 1: # if any player got the token and the round ends, pocket + token value
                p.participant.vars["payoffs"].append(p.pocket + cu(group.token_value))
            else: # others get the pocket
                p.participant.vars["payoffs"].append(p.pocket)

            print(p.participant.vars["payoffs"])

    # Else: in first round, randomly determine one winner and
    # in other rounds make a transfer or let the token holder keep
    else:
        # in first round determine buyer
        if group.current_stage == 1:
            # get the buyer and save variables, also set got token and pocket for next round
            winner_id = random.choice(bidders)
            group.protocol = "Player ID " + str(winner_id) +" buys"
            winner = group.get_player_by_id(winner_id)
            winner.gets_token = 1
            winner.in_round(winner.round_number + 1).got_token = 1
            winner.in_round(winner.round_number + 1).pocket = winner.pocket - group.token_bid
            winner.participant.vars["once_got_token"] = True

            # set the variables for the other players in the group
            for p in winner.get_others_in_group():
                p.in_round(p.round_number + 1).got_token = 0
                p.in_round(p.round_number + 1).pocket = p.pocket

            # variables for continuing the market
            for p in group.get_players():
                p.participant.vars["market_continue"] = True

        # in other rounds let the transfer happen or let the token holder keep the token
        else:
            # first get the player with the token and the other players
            prior_winner = [p for p in group.get_players() if p.got_token == 1][0]
            other_players = prior_winner.get_others_in_group()

            # Now check whether the player who got the token bids again
            # In this case, the player will keep the token and variables(got_token and pocket) will be transferred to next round
            if prior_winner.bid == 1 or group.number_bidders == 0:
                prior_winner.gets_token = 1
                prior_winner.in_round(prior_winner.round_number + 1).got_token = 1

                for p in other_players:
                    p.gets_token = 0
                    p.in_round(p.round_number + 1).got_token = 0

                # set pocket in next round; will stay the same
                for p in group.get_players():
                    p.in_round(p.round_number + 1).pocket = p.pocket

                # store it in group variable
                group.protocol = "TOKEN KEPT BY PLAYER ID " + str(prior_winner.id_in_group)

            # Else (non token holders bid and the one who got the token bids not) draw one random player to receive the token
            # and make the transfer in their pockets
            else:
                winner_id = random.choice(bidders)
                group.protocol = "TRANSFER - BUYER: ID " + str(winner_id) + "; SELLER: ID " + str(prior_winner.id_in_group)
                winner = group.get_player_by_id(winner_id)
                winner.gets_token = 1
                winner.in_round(winner.round_number + 1).got_token = 1
                winner.in_round(winner.round_number + 1).pocket = winner.pocket - group.token_bid

                # add sell to prior winner pocket for the next round
                prior_winner.in_round(prior_winner.round_number + 1).pocket = prior_winner.pocket + group.token_bid

                # set variable that winner once got the token
                winner.participant.vars["once_got_token"] = True

                # for every other player transfer the pocket into the next round
                others = [p for p in group.get_players() if p.got_token == 0 and p.gets_token == 0]
                for p in others:
                    p.in_round(p.round_number + 1).pocket = p.pocket

            # safe payoff (pocket which would result in the round after the endround)
            # if market ends, the pocket will be again setup for new market in next round (see setup market function)
            if group.current_stage == C.NUM_STAGES:
                group.protocol = "MARKET FINISHED"
                for p in group.get_players():
                    if p.gets_token == 1: # the one who gets the token in the end gets the pocket plus token value
                        p.participant.vars["payoffs"].append(cu(p.in_round(p.round_number + 1).pocket) + cu(group.token_value))
                    else: # others get the pocket value
                        p.participant.vars["payoffs"].append(cu(p.in_round(p.round_number + 1).pocket))

                    print(p.participant.vars["payoffs"])

# PAGES
class Introduction(Page):
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True

    def vars_for_template(player: Player):
        return {
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "bid_list": list(zip(range(1,12),C.token_bid_list))
        }

    def before_next_page(player: Player, timeout_happened):
        # initialize a list to collec the beliefs over the course of the game
        player.participant.vars["belief_collection"] = []




class GroupingWaitPage(WaitPage):

    def is_displayed(player: Player):
        if player.round_number == 1:
            return True

    group_by_arrival_time = True
    title_text = "Wait for the other players to arrive."

    def after_all_players_arrive(group: Group): treatment_setup(group)


class Marketbeginning(Page):
    def is_displayed(player: Player):
        if player.group.current_stage == 1:
            return True

    def vars_for_template(player: Player):
        return {
            "round_number": player.round_number,
            "market": player.group.current_market,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "bid_list": list(zip(range(1,12),C.token_bid_list))
        }

class Marketsetup(WaitPage):

    title_text = "Setting up the Market"

    def is_displayed(player: Player):
        if player.group.current_stage == 1:
            player.participant.vars["market_continue"] = True
            player.participant.vars["market_ends_shown"] = False # set continue variable
            player.participant.vars["early_end_got_token"] = False
            return True

    def after_all_players_arrive(group: Group):  setup_market(group)


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid']

    def is_displayed(player: Player):
        if player.participant.vars["market_continue"] == True:
            return True

    def vars_for_template(player: Player):

        # calculate variables for progress bar
        task_progress = 50#player.participant.vars["task_number"]/2
        market_progress = player.group.current_market/C.NUM_MARKETS*100
        stage_progress = player.group.current_stage/C.NUM_STAGES*100

        bought = False
        sold = False
        previous_bid = False
        token_kept_previous = False
        previous_token_bid = False

        # variable if player has bid in previous round and one for player keeping the token in previous round
        if player.group.current_stage != 1:
            if player.in_round(player.round_number - 1).got_token == 0 and player.in_round(player.round_number - 1).gets_token == 1:
                bought = True
            elif player.in_round(player.round_number - 1).got_token == 1 and player.in_round(player.round_number - 1).gets_token == 0:
                sold = True
            previous_bid = player.in_round(player.round_number-1).bid
            # token_kept_previous = "KEPT" in player.in_round(player.round_number-1).group.protocol
            token_kept_previous = player.in_round(player.round_number-1).got_token and player.in_round(player.round_number-1).gets_token
            previous_token_bid = player.in_round(player.round_number - 1).group.token_bid


        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "market": player.group.current_market,
            "market_progress": market_progress,
            "stage": player.group.current_stage,
            "stage_progress": stage_progress,
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "token_bid": player.group.token_bid,
            "bid_list": list(zip(range(1, 12), C.token_bid_list)),
            "token_value": player.group.token_value,
            "got_token": player.got_token,
            "pocket": player.pocket,
            "H_value": C.token_value_list[player.group.current_market-1],
            "var_name": 'bid',
            "once_got_token": player.participant.vars["once_got_token"],
            "previous_bid": previous_bid,
            "token_kept_previous": token_kept_previous,
            "bought": bought,
            "sold": sold,
            "previous_token_bid":previous_token_bid
        }

class Belief(Page):
    form_model = 'player'

    # condition that in the last round the following belief is not elicited
    def get_form_fields(player: Player):
        if player.group.current_stage != 11:
            return ['belief_other_value','belief_bidders_current','belief_bidders_following']
        else:
            return ['belief_other_value','belief_bidders_current']


    def is_displayed(player: Player):
        if player.participant.vars["market_continue"] == True:
            return True

    def vars_for_template(player: Player):

        # calculate variables for progress bar
        task_progress = 50#player.participant.vars["task_number"]/2
        market_progress = player.group.current_market/C.NUM_MARKETS*100
        stage_progress = player.group.current_stage/C.NUM_STAGES*100

        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "market": player.group.current_market,
            "market_progress": market_progress,
            "stage": player.group.current_stage,
            "stage_progress": stage_progress,
            "round_number": player.round_number,
            "bid_list": list(zip(range(1, 12), C.token_bid_list)),
            "treatment": player.group.treatment,
            "belief_other_value":"belief_other_value",
            "belief_bidders_current":  "belief_bidders_current",
            "belief_bidders_following": "belief_bidders_following",
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "H_value": C.token_value_list[player.group.current_market-1],
        }

    def before_next_page(player: Player, timeout_happened):
        # store beliefs in a list for the end
        if player.group.current_stage != 11:
            last_belief = player.belief_bidders_following
        else:
            last_belief = None


        player.participant.vars["belief_collection"].append([player.group.current_market, player.group.current_stage,
                                                            (player.belief_other_value,player.belief_bidders_current,
                                                             last_belief)])

class ResultsWaitPage(WaitPage):

    def is_displayed(player: Player):
        if player.participant.vars["market_continue"] == True:
            return True

    def after_all_players_arrive(group: Group): set_buyer(group)



class MarketEarlyEnd(Page):
    timeout_seconds = 10

    def is_displayed(player: Player):
        if player.participant.vars["market_continue"] == False and player.participant.vars["market_ends_shown"] is not True:
            return True



    def vars_for_template(player: Player):
        # calculate variables for progress bar
        task_progress = 50  # player.participant.vars["task_number"]/2
        market_progress = player.group.current_market / C.NUM_MARKETS * 100
        stage_progress = player.group.current_stage / C.NUM_STAGES * 100

        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "market": player.group.current_market,
            "market_progress": market_progress,
            "stage": player.group.current_stage,
            "stage_progress": stage_progress,
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "final_market": player.group.current_market == C.NUM_MARKETS,
        }

    def before_next_page(player: Player, timeout_happened):
        player.participant.vars["market_ends_shown"] = True
        player.participant.vars["early_end_got_token"] = player.got_token



class Result(Page):
    form_model = 'player'
    form_fields = []

    timeout_seconds = 10

    def is_displayed(player: Player):
        if player.group.current_stage == 11:
            return True

    def vars_for_template(player: Player):
        # calculate variables for progress bar
        task_progress = 50  # player.participant.vars["task_number"]/2
        market_progress = player.group.current_market / C.NUM_MARKETS * 100
        stage_progress = player.group.current_stage / C.NUM_STAGES * 100

        # determine who got token - when market regularly ends it is the one who buys it (who gets it)
        # if not: it is the one who got it in the early end screen
        if player.participant.vars["market_continue"]:
            got_token = player.gets_token
        else:
            got_token = player.participant.vars["early_end_got_token"]


        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "market": player.group.current_market,
            "market_progress": market_progress,
            "stage": player.group.current_stage,
            "stage_progress": stage_progress,
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "token_value": player.group.token_value,
            "payoff": player.participant.vars["payoffs"][player.group.current_market - 1],
            "dice_rolls": player.participant.vars["dice_rolls"],
            "got_token": got_token,
            "final_market": player.group.current_market == C.NUM_MARKETS,
            "belief_collection": player.participant.vars["belief_collection"]
        }


page_sequence = [
    GroupingWaitPage,
    Introduction,
    Marketbeginning,
    Marketsetup,
    Bid,
    Belief,
    ResultsWaitPage,
    MarketEarlyEnd,
    Result]
