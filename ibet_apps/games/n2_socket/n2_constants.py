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
    '90091': 'Baccarat - Live Casino',
    '90092': 'Baccarat - Live Casino',
    '110001': 'Blackjack - Virtual Casino'
})