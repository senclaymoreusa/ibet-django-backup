from collections import defaultdict

DESC_MAP = defaultdict(lambda: 'None', {
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

GAME_CODE_MAP = defaultdict(lambda: 'Roulette', {
    '90092': 'Baccarat',
    'THB': '764',
    'VND': '7041',
    'TTC': '1111'
})