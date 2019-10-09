from collections import defaultdict

DESC_MAP = defaultdict(lambda: None, {
    105: "ERROR_INVALID_AUTHENTICATION",
    106: "ERROR_INVALID_MESSAGE",
    119: "ERROR_INSUFFICIENT_FUND"
})
CURRENCY_MAP = defaultdict(lambda: None, {
    'CNY': '156',
    'THB': '764',
    'VND': '7041'
})