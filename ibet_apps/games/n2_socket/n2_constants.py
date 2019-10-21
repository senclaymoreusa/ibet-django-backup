from collections import defaultdict

DESC_MAP = defaultdict(lambda: 'None', {
    103: "ERROR_SQL_OPERATION_EXCEPTION",
    105: "ERROR_INVALID_AUTHENTICATION",
    106: "ERROR_INVALID_MESSAGE",
    119: "ERROR_INSUFFICIENT_FUND"
})

CURRENCY_MAP = defaultdict(lambda: '1111', {
    'CNY': '156',
    'THB': '764',
    'VND': '7041',
    'TTC': '1111'
})

OUTCOME_MAP = defaultdict(lambda: '1111', {
    'win': 0,
    'lose': 1,
    'tie': 2,
    'void': 3
})

GAMECODE_MAP = defaultdict(lambda: 'Roulette', {
    '50002': 'Roulette - Live Casino',
    '51002': 'Roulette - Virtual Casino',
    '52002': 'Roulette - Virtual Casino',
    '60001': 'Sicbo',
    '61001': 'Sicbo - Virtual Casino',
    '62001': 'Sicbo - Virtual Casino',
    '90091': 'Baccarat - Live Casino', # commission
    '90092': 'Baccarat - Live Casino', # non-comm
    '91091': 'Baccarat - Virtual Casino',
    '91092': 'Baccarat - Virtual Casino',
    '110001': 'Blackjack - Virtual Casino',
    '110002': 'Free Bet Blackjack - Virtual Casino',
    '110003': 'Blackjack Switch - Virtual Casino', 
})