from otree.api import *
import random


doc = """
Subjects are endowed with an earned endowment 12 Euro cash balance. 11 periods of auctioning, with prices starting 
at 1 cent, doubling each round to 2, 4, 8, 16, etc. with last round 10,24 euros.
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
    NUM_PERIODS = 11
    # Number of markets (a market round consists of periods or stages)
    NUM_MARKETS = 5
    # Totaling in a number of rounds where the game is played
    NUM_ROUNDS = NUM_PERIODS * NUM_MARKETS
    INSTRUCTIONS_TEMPLATE = 'gf_game/instructions.html'
    GAMESTART_TEMPLATE = 'gf_game/GameStart_template.html'
    # Endowment at each of the beginning market rounds
    ENDOWMENT = cu(12)
    # Start value for the token
    START_VALUE = cu(0.01)
    # Initiate list for token bids
    token_bid_list = [START_VALUE]
    for i in range(0,NUM_PERIODS-1):
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
    current_period = models.IntegerField(
        doc="""Current period (stage of the market round) the group is in """
    )
    number_bidders = models.IntegerField(
        doc="""Number of bidders in the round"""
    )
    protocol = models.StringField(
        doc="""protocol what happens in each round"""
    )


class Player(BasePlayer):
    got_token = models.BooleanField(initial=False,
        doc="""Whether player is the owner of the token in the group at the beginning of this period or not"""
    )
    pocket = models.CurrencyField(
        doc="""The pocket money the player has left at the beginning of the period"""
    )
    time_spent = models.IntegerField(
        doc="""Track time spent on the decision page using javascript"""
    )
    bid = models.BooleanField(
        doc="""Whether player wants to buy(hold if got token) in this period or not"""
    )
    gets_token = models.BooleanField(initial=False,
        doc="""Whether player gets the token at the end of the period"""
    )
    belief_other_value = models.IntegerField(
        doc="""Belief of the player that the token value is another value (in all treatments other 
        than BASELINE, that the value is H"""
    )
    belief_bidders_current = models.IntegerField(
        doc="""Belief of the player how manny bidders were in this period"""
    )
    belief_bidders_following = models.IntegerField(
        doc="""Belief of the player how manny bidders will be in the next period. Not elicited in the last period"""
    )

# FUNCTIONS
def creating_session(subsession: Subsession):

    if subsession.round_number == 1:
        print('############CREATING SUBSESSION###################')
        print('Number of markets: ', C.NUM_MARKETS,"Number of periods: ", C.NUM_PERIODS)
        print("Number of participants per group: ", C.PLAYERS_PER_GROUP)
        print('Token bid list: ',C.token_bid_list)
        print('Randomization of treatments: ', subsession.session.config["randomize_treatments"])
        print("Group by arrival time method: ", subsession.session.config["groups_constant"])
        print('###############################################')


    # assign values which all groups have in common
    for g in subsession.get_groups():
        g.current_market = int(g.round_number/(C.NUM_PERIODS+0.1))+1
        g.current_period = (lambda x: x % C.NUM_PERIODS if x % C.NUM_PERIODS !=0 else C.NUM_PERIODS) (g.round_number)
        g.token_bid = C.token_bid_list[g.current_period-1]

        for p in g.get_players():
            if g.current_period == 1:
                p.pocket = C.ENDOWMENT
                p.participant.vars["gf_payoffs"] = [] # initialize a list for payoffs in each markets
                p.participant.vars["gf_predictions"] = [] # initialize list for the chosen rounds for each market for predictions
                p.participant.vars["gf_predictions_payoffs"] = []  # initialize list for the chosen rounds for each market for predictions


def group_by_arrival_time_method(subsession: Subsession, waiting_players):
    if subsession.session.config["groups_constant"] == True:
        print("ENTERING GROUP BY ARRIVAL METHOD")
        # we now place users into different baskets, according to their group in the previous app.
        # the dict 'd' will contain all these baskets. (source: otree hub)
        d = {}
        for p in waiting_players:
            group_id = p.participant.vars["guess_group_id"][0] # declare the group id assigned in previous app; in this case the guessing game
            if group_id not in d:
                # since 'd' is initially empty, we need to initialize an empty list (basket)
                # each time we see a new group ID.
                d[group_id] = []
            players_in_my_group = d[group_id]
            players_in_my_group.append(p)
            if len(players_in_my_group) == C.PLAYERS_PER_GROUP:
                print("Forming group with previous group id:", group_id)
                return players_in_my_group
            print('d is', d)
    else:
        # just put the first N players together in one group
        print("NOT ENTERING GROUP BY ARRIVAL METHOD")
        if len(waiting_players) == C.PLAYERS_PER_GROUP:
            return [waiting_players[0],waiting_players[1],waiting_players[2]]
        pass


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
    group.current_market = int(group.round_number / (C.NUM_PERIODS + 0.1)) + 1
    group.current_period = (lambda x: x % C.NUM_PERIODS if x % C.NUM_PERIODS != 0 else C.NUM_PERIODS)(group.round_number)
    group.token_bid = C.token_bid_list[group.current_period - 1]

    # forward treatment and common values to upcoming rounds
    for i in range(2, C.NUM_ROUNDS + 1):
        group.in_round(i).treatment = group.in_round(1).treatment
        group.in_round(i).uncertainty = group.in_round(1).uncertainty
        group.in_round(i).information = group.in_round(1).information
        group.in_round(i).current_market = int(group.in_round(i).round_number / (C.NUM_PERIODS + 0.1)) + 1
        group.in_round(i).current_period = (lambda x: x % C.NUM_PERIODS if x % C.NUM_PERIODS != 0 else C.NUM_PERIODS)(
            group.in_round(i).round_number)
        group.in_round(i).token_bid = C.token_bid_list[group.in_round(i).current_period - 1]

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
            group.token_value = C.token_value_list[group.current_period]
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
        group.protocol = "MARKET ENDS IN T = " + str(group.current_period)
        # print("MARKET BREAKDOWN!!!!!")
        for p in group.get_players():
            p.participant.vars["market_continue"] = False # set market conitune variable to false
            if p.got_token == 1: # if any player got the token and the round ends, pocket + token value
                p.participant.vars["gf_payoffs"].append(p.pocket + cu(group.token_value))
            else: # others get the pocket
                p.participant.vars["gf_payoffs"].append(p.pocket)

            print(p.participant.vars["gf_payoffs"])

    # Else: in first round, randomly determine one winner and
    # in other rounds make a transfer or let the token holder keep
    else:
        # in first round determine buyer
        if group.current_period == 1:
            # get the buyer and save variables, also set got token and pocket for next round
            winner_id = random.choice(bidders)
            group.protocol = "Player ID " + str(winner_id) +" buys"
            winner = group.get_player_by_id(winner_id)
            winner.gets_token = 1
            winner.in_round(winner.round_number + 1).got_token = 1
            winner.in_round(winner.round_number + 1).pocket = winner.pocket - group.token_bid
            #winner.participant.vars["once_got_token"] = True

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
            if prior_winner.bid == 1:
                prior_winner.gets_token = 1

                # check for the ultimate last round
                if prior_winner.round_number < C.NUM_ROUNDS:
                    prior_winner.in_round(prior_winner.round_number + 1).got_token = 1

                for p in other_players:
                    p.gets_token = 0
                    if p.round_number < C.NUM_ROUNDS:
                        p.in_round(p.round_number + 1).got_token = 0

                # set pocket in next round; will stay the same
                for p in group.get_players():
                    if p.round_number < C.NUM_ROUNDS:
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
                if winner.round_number < C.NUM_ROUNDS:
                    winner.in_round(winner.round_number + 1).got_token = 1
                    winner.in_round(winner.round_number + 1).pocket = winner.pocket - group.token_bid

                    # add sell to prior winner pocket for the next round
                    prior_winner.in_round(prior_winner.round_number + 1).pocket = prior_winner.pocket + group.token_bid

                # set variable that winner once got the token
                #winner.participant.vars["once_got_token"] = True

                # for every other player transfer the pocket into the next round
                others = [p for p in group.get_players() if p.got_token == 0 and p.gets_token == 0]
                for p in others:
                    if p.round_number < C.NUM_ROUNDS:
                        p.in_round(p.round_number + 1).pocket = p.pocket

            # save payoff (pocket which would result in the round after the endround)
            # if market ends, the pocket will be again setup for new market in next round (see setup market function)
            if group.current_period == C.NUM_PERIODS:
                group.protocol = "MARKET FINISHED"
                for p in group.get_players():
                    if p.round_number < C.NUM_ROUNDS:
                        if p.gets_token == 1: # the one who gets the token in the end gets the pocket plus token value
                            p.participant.vars["gf_payoffs"].append(cu(p.in_round(p.round_number + 1).pocket) + cu(group.token_value))
                        else: # others get the pocket value
                            p.participant.vars["gf_payoffs"].append(cu(p.in_round(p.round_number + 1).pocket))

                    # special case for last period in last market
                    elif p.round_number == C.NUM_ROUNDS:
                        if p.gets_token == 1:
                            p.participant.vars["gf_payoffs"].append(cu(p.in_round(p.round_number).pocket) - group.token_bid + cu(group.token_value))
                        else:
                            p.participant.vars["gf_payoffs"].append(cu(p.in_round(p.round_number).pocket))

                    print(p.participant.vars["gf_payoffs"])

def set_ending(group: Group):
    # determine chosen market and chosen period for the group in the last period in the last market
    if group.current_market == C.NUM_MARKETS:
        chosen_market = random.choice(range(1,C.NUM_MARKETS+1))
        for player in group.get_players():
            # collect the beliefs in the chosen market
            beliefs_in_chosen_market = [belief_list for belief_list in
                                        player.participant.vars["gf_belief_collection"] if
                                        belief_list[0] == chosen_market]
            # assign one random period
            chosen_period = random.choice(range(1, len(beliefs_in_chosen_market) + 1))
            # determine the round to collect the data in the corresponding round
            chosen_round = (chosen_market - 1) * C.NUM_PERIODS + chosen_period

            # assign that to participant variables
            player.participant.vars["gf_chosen_market"] = chosen_market
            player.participant.vars["gf_chosen_period"] = chosen_period
            player.participant.vars["gf_chosen_round"] = chosen_round # save for check purposes
            player.participant.vars["gf_number_of_markets"] = C.NUM_MARKETS # for next app


            prediction = beliefs_in_chosen_market[chosen_period - 1][2]  # take the three beliefs of the chosen periods
            # determine three beliefs (what actually happened in this round
            my_belief_other_value = prediction[0]
            my_belief_current_bidders = prediction[1]
            my_protocol = player.group.in_round(chosen_round).protocol  # protocol what happened

            # Get the values in the chosen round
            # Number of others who bid: subtract own bid because player should not count himself (hence a number between 0 and 5)
            my_number_bidders_current = player.group.in_round(chosen_round).number_bidders - player.in_round(chosen_round).bid
            my_token_not_zero = player.group.token_value != 0.00  # if token is any other value


            # If chosen period is not final period or period chosen is not early end period: make three checks, else only two (excl. following bidders)
            if chosen_period != C.NUM_PERIODS and "MARKET ENDS" not in my_protocol:

                # participant's belief of bidders in the following round
                my_belief_following_round = prediction[2]

                # Number of  others who bid in the following round (hence round +1): subtract own bid
                my_number_bidders_following = player.group.in_round(chosen_round + 1).number_bidders - player.in_round(chosen_round + 1).bid

                # collect the conditions for getting the predictions right
                my_conditions = [
                    # if belief other value is right; 50 is assumed to be wrong
                    round(my_belief_other_value / 100) == my_token_not_zero if my_belief_other_value != 50 else False,
                    # if number of bidders in that period was correct
                    my_belief_current_bidders == my_number_bidders_current,
                    # if number of bidders in following period was correct
                    my_belief_following_round == my_number_bidders_following
                ]

                # if all three are correct: get bonus payoff, else nothing
                if sum(my_conditions) == 3:
                    player.participant.vars["gf_predictions_payoffs"].append(cu(1.00))
                else:
                    player.participant.vars["gf_predictions_payoffs"].append(cu(0.00))

                # collect everything for checks
                player.participant.vars["gf_predictions"].append([
                    (# market, period and the metrics in the period
                    chosen_market, chosen_period, player.group.token_value,
                     my_number_bidders_current, my_number_bidders_following),
                    # what the participant predicted
                    prediction])

            # If round chosen is final or early end: only check first two metrics
            else:
                my_conditions = [
                    # if belief other value is right
                    round(my_belief_other_value / 100) == my_token_not_zero if my_belief_other_value != 50 else False,
                    # if number of bidders in that period was correct
                    my_belief_current_bidders == my_number_bidders_current,
                ]
                # if all two are correct add payoff to predictions payoff
                if sum(my_conditions) == 2:
                    player.participant.vars["gf_predictions_payoffs"].append(cu(1.00))
                else:
                    player.participant.vars["gf_predictions_payoffs"].append(cu(0.00))

                # collect again everything
                player.participant.vars["gf_predictions"].append([
                    (# market, period and the metrics in the period
                    chosen_market, chosen_period, player.group.token_value,
                     my_number_bidders_current, None),
                    # what participant predicted
                    prediction])

            # print for sanity check
            print(player.participant.vars["gf_predictions_payoffs"])


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
            "bid_list": list(zip(range(1,12),C.token_bid_list)),
            "number_others": C.PLAYERS_PER_GROUP - 1,
        }

    def before_next_page(player: Player, timeout_happened):
        # initialize a list to collect the beliefs over the course of the game
        player.participant.vars["gf_belief_collection"] = []


class GroupingWaitPage(WaitPage):

    def is_displayed(player: Player):
        if player.round_number == 1:
            return True

    group_by_arrival_time = True
    title_text = "Wait for the other players to arrive."

    def after_all_players_arrive(group: Group): treatment_setup(group)


class Marketbeginning(Page):
    timeout_seconds = 10

    def is_displayed(player: Player):
        if player.group.current_period == 1:
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
        if player.group.current_period == 1:
            player.participant.vars["market_continue"] = True
            player.participant.vars["market_ends_shown"] = False # set continue variable
            player.participant.vars["early_end_got_token"] = False
            return True

    def after_all_players_arrive(group: Group):  setup_market(group)


class Bid(Page):
    form_model = 'player'
    form_fields = ['bid','time_spent']

    def is_displayed(player: Player):
        if player.participant.vars["market_continue"] == True:
            return True

    def vars_for_template(player: Player):

        # calculate variables for progress bar
        task_progress = 50#player.participant.vars["task_number"]/2
        market_progress = player.group.current_market/C.NUM_MARKETS*100
        period_progress = player.group.current_period/C.NUM_PERIODS*100

        bought = False
        sold = False
        previous_bid = False
        token_kept_previous = False
        previous_token_bid = False

        # variable if player has bid in previous round and one for player keeping the token in previous round
        if player.group.current_period != 1:
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
            "period": player.group.current_period,
            "period_progress": period_progress,
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "token_bid": player.group.token_bid,
            "bid_list": list(zip(range(1, C.NUM_PERIODS+1), C.token_bid_list)),
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
            "previous_token_bid":previous_token_bid,
            "number_others": C.PLAYERS_PER_GROUP - 1,
            "time_spent": 'time_spent'
        }

    def before_next_page(player: Player, timeout_happened):
        if player.got_token == True:
            player.participant.vars["once_got_token"] = True

class Belief(Page):
    form_model = 'player'

    # condition that in the last round the following belief is not elicited
    def get_form_fields(player: Player):
        if player.group.current_period != 11:
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
        period_progress = player.group.current_period/C.NUM_PERIODS*100

        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "market": player.group.current_market,
            "market_progress": market_progress,
            "period": player.group.current_period,
            "period_progress": period_progress,
            "round_number": player.round_number,
            "bid_list": list(zip(range(1, C.NUM_PERIODS+1), C.token_bid_list)),
            "treatment": player.group.treatment,
            "belief_other_value":"belief_other_value",
            "belief_bidders_current":  "belief_bidders_current",
            "belief_bidders_following": "belief_bidders_following",
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "H_value": C.token_value_list[player.group.current_market-1],
            "number_others": C.PLAYERS_PER_GROUP - 1,
            "number_others_list": list(range(0,C.PLAYERS_PER_GROUP)),
            "once_got_token": player.participant.vars["once_got_token"],
        }

    def before_next_page(player: Player, timeout_happened):
        # store beliefs in a list for the end
        if player.group.current_period != 11:
            belief_following = player.belief_bidders_following
        else:
            belief_following = None

        # Store belief values: Current market, Current stage, belief of the other value, belief of current bidders and
        # belief of following bidders
        player.participant.vars["gf_belief_collection"].append([player.group.current_market, player.group.current_period,
                                                            (player.belief_other_value,player.belief_bidders_current,
                                                             belief_following)])

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
        period_progress = player.group.current_period / C.NUM_PERIODS * 100

        return {
            "market_continue": player.participant.vars["market_continue"],
            "task_progress": task_progress,
            "bid_list": list(zip(range(1, C.NUM_PERIODS + 1), C.token_bid_list)),
            "market": player.group.current_market,
            "market_progress": market_progress,
            "period": player.group.current_period,
            "period_progress": period_progress,
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
        if player.group.current_period == C.NUM_PERIODS:
            return True

    def vars_for_template(player: Player):
        # calculate variables for progress bar
        task_progress = 50  # player.participant.vars["task_number"]/2
        market_progress = player.group.current_market / C.NUM_MARKETS * 100
        period_progress = player.group.current_period / C.NUM_PERIODS * 100

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
            "period": player.group.current_period,
            "period_progress": period_progress,
            "round_number": player.round_number,
            "treatment": player.group.treatment,
            "uncertainty": player.group.field_maybe_none('uncertainty'),
            "information": player.group.field_maybe_none('information'),
            "token_value": player.group.token_value,
            "payoff": player.participant.vars["gf_payoffs"][player.group.current_market - 1],
            "dice_rolls": player.participant.vars["dice_rolls"],
            "got_token": got_token,
            "final_market": player.group.current_market == C.NUM_MARKETS,
            "belief_collection": player.participant.vars["gf_belief_collection"]
        }



class EndingWaitPage(WaitPage):

    title_text = "Wrapping everything up"

    def is_displayed(player: Player):
        if player.group.current_market == C.NUM_MARKETS and player.group.current_period == C.NUM_PERIODS:
            return True


    def after_all_players_arrive(group: Group): set_ending(group)


page_sequence = [
    GroupingWaitPage,
    Introduction,
    Marketbeginning,
    Marketsetup,
    Bid,
    Belief,
    ResultsWaitPage,
    MarketEarlyEnd,
    Result,
    EndingWaitPage]
