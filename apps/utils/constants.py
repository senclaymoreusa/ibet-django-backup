GENDER_CHOICES = (
    ('Male','Male'),
    ('Female', 'Female')
)

CONTACT_OPTIONS = (
    ('Email', 'Email'),
    ('SMS', 'SMS'),
    ('OMS', 'OMS'),
    ('Push_Notification', 'Push Notification')
)

CURRENCY_TYPES = (
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('JPY', 'JPY'),
    ('CNY', 'CNY'),
    ('HKD', 'HKD'),
    ('AUD', 'AUD')
)

USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

CHANNEL_CHOICES = (
    (0, 'Alipay'),
    (1, 'Wechat'),
    (2, 'Card'),
    (3, 'Qaicash'),
    (4, 'Asia Pay'),
    (5, 'Paypal')
)
CURRENCY_CHOICES = (
    (0, 'CNY'),
    (1, 'USD'),
    (2, 'THB'),
    (3, 'IDR'),
)
STATE_CHOICES = (
    (0, 'SUCCESS'), 
    (1, 'FAILED'),
    (2, 'CREATED'),
    (3, 'PENDING'),
    (4, 'APPROVED'),
    (5, 'REJECTED'),
    (6, 'COMPLETED')
)
REVIEW_STATE_CHOICES = (
    (0, 'Approved'),
    (1, 'Pending'),
    (2, 'Rejected'),
)

DEPOSIT_METHOD_CHOICES = (
    (0, "LBT_ONLINE"),
    (1, "LBT_ATM"),
    (2, "LBT_OTC"),
    (3, "DIRECT_PAYMENT"),
    (4, "BANK_TRANSFER"),
    (5, "IBT")
)

TRANSACTION_TYPE_CHOICES = (
    (0, 'Deposit'),
    (1, 'Withdrawal'),
    (2, 'Bet Placed'),
    (3, 'Bet Settled'),
    (4, 'Transfer In'),
    (5, 'Transfer Out'),
    (6, 'Bonus'),
    (7, 'Adjustment'),
    (8, 'Commission')
)
LANGUAGE_CHOICES = (
    ('en-Us', 'English – United States'),
    ('zh-Hans', 'Chinese Simplified'),
    ('th', 'Thai'),
    ('vi', 'Vietnamese'),
    ('ko', 'Korean'),
    ('ja', 'Japanese'),
)
GAME_TYPE_CHOICES = (
    (0, 'Sports'),
    (1, 'Games'),
    (2, 'Live Casino'),
    (3, 'Financial'),
    (4, 'General'),
)

COUNTRY_CHOICES = (
    ('US', 'United States'),
    ('CN', 'China'),
    ('TH', 'Thailand'),
    ('JP', 'Japan'),
)

ACTIVITY_TYPE = (
    (0, 'Operation'),
    (1, 'Remark'),
    (2, 'Chat'),
    (3, 'Note'),
)

AGENT_LEVEL = (
    ('Premium', 'Premium'),
    ('Invalid', 'Invalid'),
    ('Normal', 'Normal'),
    ('Negative', 'Negative'),
)

AGENT_STATUS = (
    ('Normal', 'Normal'),
    ('Block', 'Block'),
)

   
BANK_LIST_CHOICES = (
    ("OOO6CN", "China UnionPay"),
    ("ABOCCN", "Agricultural Bank of China"),
    ("BEASCN", "Bank of East Asia"),
    ("BJCNCN", "Bank of Beijing"),
    ("BKCHCN", "Bank of China"),
    ("BKNBCN", "Bank of Ningbo"),
    ("BKSHCN", "Bank Of Hebei"),
    ("BOSHCN", "Bank of Shanghai"),
    ("BRCBCN", "Beijing Rural Commercial Bank"),
    ("CBOCCN", "Bank of Chengdu"),
    ("CHBHCN", "China Bohai Bank"),
    ("CIBKCN", "China Citic Bank"),
    ("CMBCCN", "China Merchants Bank"),
    ("CN01CN", "Zhongshan Rural Credit Union"),
)

LIMIT_TYPE_BET         = 0
LIMIT_TYPE_LOSS        = 1
LIMIT_TYPE_DEPOSIT     = 2
LIMIT_TYPE_WITHDRAW    = 3
LIMIT_TYPE_ACCESS_DENY = 4

LIMIT_TYPE = (
    (LIMIT_TYPE_BET, 'Bet'),
    (LIMIT_TYPE_LOSS, 'Loss'),
    (LIMIT_TYPE_DEPOSIT, 'Deposit'),
    (LIMIT_TYPE_WITHDRAW, 'Withdraw'),
    (LIMIT_TYPE_ACCESS_DENY, 'Access Deny')
)

GAME_PRODUCT_GB_SPORTS         = 0
GAME_PRODUCT_EZ_SPORTS        = 1
GAME_PRODUCT_GAMES     = 2
GAME_PRODUCT_LOTTO    = 3
GAME_PRODUCT_LIVE_CASINO = 4

GAME_PRODUCT = (
    (GAME_PRODUCT_GB_SPORTS, 'GB SPORTS'),
    (GAME_PRODUCT_EZ_SPORTS, 'EZ SPORTS'),
    (GAME_PRODUCT_GAMES, 'GAMES'),
    (GAME_PRODUCT_LOTTO, 'LOTTO'),
    (GAME_PRODUCT_LIVE_CASINO, 'LIVE CASINO')
)