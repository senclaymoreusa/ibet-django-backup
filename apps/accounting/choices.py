# This file holds all the ChoiceField options for accounting/models.py

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
TYPE_CHOICES = (
    (0, 'Deposit'),
    (1, 'Withdrawal'),
    (2, 'Bet Placed'),
    (3, 'Bet Settled'),
    (4, 'Transfer In'),
    (5, 'Transfer Out'),
    (6, 'Bonus'),
    (7, 'Adjustment'),
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