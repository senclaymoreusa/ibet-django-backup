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
    (2, 'PHP'),
    (3, 'IDR'),
)
STATE_CHOICES = (
    (0, 'SUCCESS'),
    (1, 'FAILED'),
    (2, 'PENDING'),
    (3, 'APPROVED'),
    (4, 'REJECTED'),
)
REVIEW_STATE_CHOICES = (
    (0, 'Approved'),
    (1, 'Pending'),
    (2, 'Rejected'),
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