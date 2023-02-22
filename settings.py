from os import environ

SESSION_CONFIGS = [
    dict(
        name='Greater_Fool_Game_BASELINE',
        display_name="Greater Fool Game: BASELINE",
        num_demo_participants=3,
        app_sequence=['gf_game'],
        treatment='BASELINE'  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
    ),
    dict(
        name='Greater_Fool_Game_AMBI_SYM',
        display_name="Greater Fool Game: AMBI_SYM",
        num_demo_participants=3,
        app_sequence=['gf_game'],
        treatment='AMBI_SYM'  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
    ),
    dict(
        name='Greater_Fool_Game_RISK_SYM',
        display_name="Greater Fool Game: RISK_SYM",
        num_demo_participants=3,
        app_sequence=['gf_game'],
        treatment='RISK_SYM'  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
    ),
    dict(
        name='Greater_Fool_Game_AMBI_ASYM',
        display_name="Greater Fool Game: AMBI_ASYM",
        num_demo_participants=3,
        app_sequence=['gf_game'],
        treatment='AMBI_ASYM'  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
    ),
    dict(
        name='Greater_Fool_Game_RISK_ASYM',
        display_name="Greater Fool Game: RISK_ASYM",
        num_demo_participants=3,
        app_sequence=['gf_game'],
        treatment='RISK_ASYM'  # treatment is either BASELINE, AMBI_SYM, RISK_SYM, AMBI_ASYM, RISK_ASYM
    ),

    dict(
        name='questionnaire',
        display_name="Questionnaire",
        num_demo_participants=3,
        app_sequence=['questionnaire'],
    ),
    dict(
        name='guess_two_thirds',
        display_name="Guess 2/3 of the Average",
        num_demo_participants=3,
        app_sequence=['guess_two_thirds', 'payment_info'],
    ),

]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as session.config,
# e.g. session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
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

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""

# don't share this with anybody.
SECRET_KEY = '6lertt4wlb09zj@4wyuy-p-6)i$vh!ljwx&r9bti6kgw54k-h8'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

# inactive session configs
