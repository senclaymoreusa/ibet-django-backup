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
    (0, 'Xpay'),
    (1, 'LINEpay'),
    (2, 'Astropay'),
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

ASIAPAY_BANK_CHOICES = (
    ('1','工商银行'),
    ('2','建设银行'),
    ('3','农业银行'),
    ('4','招商银行'),
    ('6','广发银行'),
    ('7','中国银行'),
    ('9','中国邮政储蓄银行'),
    ('10','中信银行'),
    ('11','光大银行'),
    ('12','民生银行'),
    ('16','兴业银行'),
    ('17','华夏银行'),
    ('23','平安银行'),
    ('38','微信支付'),
    ('39','快捷支付'),
    ('41','支付宝'),
    ('49','京东支付'),
    ('201', '比特币')
)
ASIAPAY_PAYWAY_CHOICES = (
    ('90','比特币'),
    ('42', 'QRCode'),
    ('44', '收银台'),
    ('30', '在线支付'),

)

GAME_PROVIDERS = (
    (0, 'SPORTS_1'),
    (1, 'SPORTS_2'),
    (2, 'CASINO_1'),
    (3, 'CASINO_2'),
    (4, 'SLOT_1'),
    (5, 'SLOT_2'),
)


#qaicash-payment
QAICASH_URL = 'https://public-services.mekong-300.com/ago/integration/'
MERCHANTID = '39'
MERCHANTAPIKEY = '70PsPAH!Z7l18ZuVo8^c'
APIVERSION = 'v2.0'
DEPOSIT_URL = '/deposit/routing/'
PAYOUT_URL = '/payout/routing/'

#paypal-payment
PAYPAL_MODE = 'sandbox'   # sandbox or live
PAYPAL_CLIENT_ID = 'AXoM7FKTdT8rfh-SI66SlAWd_P85YSsNfTvm0zjB0-AhJhUhUHTuXi4L87DcgkxLSLPYKCMO5DVl2pDD'
PAYPAL_CLIENT_SECRET = 'ENKmcu7Sci-RHW2gHvzmeUbZvSaCuwRiEirKH0_TkYo4AZWbVnfevS-hxq6cS6sevLU5TB3SMfq85wSB'
PAYPAL_SANDBOX_URL = 'https://api.sandbox.paypal.com/'
#astroPay sandbox urls
ASTROPAY_URL = 'https://sandbox.astropaycard.com/api_curl/streamline/newinvoice'
ASTROPAY_WPS = 'https://sandbox.astropaycard.com/apd/webpaystatus'
ASTROPAY_WCE = 'https://sandbox.astropaycard.com/apd/webcurrencyexchange'
ASTROPAY_GBC = 'https://sandbox.astropaycard.com/api_curl/apd/get_banks_by_country'
#astroPay sandbox key:
ASTROPAY_X_LOGIN = '32db4899eb' 
ASTROPAY_X_TRANS_KEY = '92afc1561b'
ASTROPAY_SECREATE = 'dc2c63c426412128fc6e3c3ef74876f26'
#astroPay sandbod WEBPAYSTATUS:
ASTROPAY_WP_LOGIN = 'f1b1d639c5'
ASTROPAY_WP_TRANS_KEY = '738e34417a'

#aisa-pay
ASIAPAY_API_URL = "http://gw.wave-pay.com"
ASIAPAY_CID = "BRANDCQNGHUA3"
COMDEPOSITKET = "A49E448121886D7C857B39C3467EC117"
ASIAPAY_KEY1 = "f6b451943fb44a38"
ASIAPAY_UNITEKEY = "Ki3CgDAz"
ASIAPAY_R1 = "randomStr"
ASIAPAY_R2 = "randomStr"

