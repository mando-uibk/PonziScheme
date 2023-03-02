from os import environ

SESSION_CONFIGS = [
    dict(
        name='Disclaimer_and_End',
        display_name="Disclaimer and End",
        num_demo_participants=3,
        app_sequence=['Disclaimer', 'TheEnd'],
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        num_demo_participants=3,
        external_payment = False, # show external page for bank credentials or not
        app_sequence=['guess_two_thirds', 'payment_info'],
    ),
    dict(
        name='Greater_Fool_Game_BASELINE',
        display_name="Greater Fool Game: BASELINE",
        num_demo_participants=3,
        app_sequence=['gf_game', 'payment_info'],
        randomize_treatments = False, # if randomization is on treatment is randomly assigned
        treatment='BASELINE',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant=False,  # if groups over both apps are kept constant
        external_payment = False, # show external page for bank credentials or not

    ),
    dict(
        name='Greater_Fool_Game_AMBI_SYM',
        display_name="Greater Fool Game: AMBI_SYM",
        num_demo_participants=3,
        app_sequence=['gf_game', 'payment_info'],
        randomize_treatments = False, # if randomization is on treatment is randomly assigned
        treatment='AMBI_SYM',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant=False,  # if groups over both apps are kept constant
        external_payment = False, # show external page for bank credentials or not
    ),
    dict(
        name='Greater_Fool_Game_RISK_SYM',
        display_name="Greater Fool Game: RISK_SYM",
        num_demo_participants=3,
        app_sequence=['gf_game', 'payment_info'],
        randomize_treatments = False, # if randomization is on treatment is randomly assigned
        treatment='RISK_SYM',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant=False,  # if groups over both apps are kept constant
        external_payment = False, # show external page for bank credentials or not
    ),
    dict(
        name='Greater_Fool_Game_AMBI_ASYM',
        display_name="Greater Fool Game: AMBI_ASYM",
        num_demo_participants=3,
        app_sequence=['gf_game', 'payment_info'],
        randomize_treatments = False, # if randomization is on treatment is randomly assigned
        treatment='AMBI_ASYM',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant=False,  # if groups over both apps are kept constant
        external_payment = False, # show external page for bank credentials or not
    ),
    dict(
        name='Greater_Fool_Game_RISK_ASYM',
        display_name="Greater Fool Game: RISK_ASYM",
        num_demo_participants=3,
        app_sequence=['gf_game', 'payment_info'],
        randomize_treatments = False, # if randomization is on treatment is randomly assigned
        treatment='RISK_ASYM',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant=False,  # if groups over both apps are kept constant
        external_payment = False, # show external page for bank credentials or not
    ),

    dict(
        name='questionnaire',
        display_name="Questionnaire",
        num_demo_participants=3,
        app_sequence=['questionnaire'],
    ),
    dict(
        name='Full_Demo',
        display_name="Full demo of the experiment",
        num_demo_participants=3,
        app_sequence=['Disclaimer','guess_two_thirds', 'gf_game','questionnaire',"payment_info",'TheEnd'],
        randomize_treatments = True, # if randomization is on treatment is randomly assigned
        treatment='BASELINE',  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
        groups_constant = True, # if groups over both apps are kept constant
        external_payment = True, # show external page for bank credentials or not
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as session.config,
# e.g. session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="", randomize_treatments = True,
    groups_constant = True, external_payment = True,
)


# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

PARTICIPANT_FIELDS = [
    'payoffs',
    'chosen_market',
    'chosen_period',
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = 'Demos for Greater Fool Game. For Demo the group size is set to 3 to enable split screen.'


# don't share this with anybody.
SECRET_KEY = '6lertt4wlb09zj@4wyuy-p-6)i$vh!ljwx&r9bti6kgw54k-h8'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# inactive session configs
