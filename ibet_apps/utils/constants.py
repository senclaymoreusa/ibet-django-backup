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
    ('AUD', 'AUD'),
    ('THB','THB'),
    ('MYR', 'MYR'),
    ('VND', 'VND'),
    ('MMK', 'MMK'),
    ('XBT', 'XBT')

)

USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

CHANNEL_CHOICES = (
    (0, 'Help2pay'),
    (1, 'LINEpay'),
    (2, 'Astropay'),
    (3, 'Qaicash'),
    (4, 'Asia Pay'),
    (5, 'Paypal'),
    (6,'fgate'),
)
CURRENCY_CHOICES = (
    (0, 'CNY'),
    (1, 'USD'),
    (2, 'THB'),
    (3, 'IDR'),
    (4, 'HKD'),
    (5, 'AUD'),
    (6,'THB'),
    (7, 'MYR'),
    (8, 'VND'),
    (9, 'MMK'),
    (10, 'XBT')
)
STATE_CHOICES = (
    (0, 'SUCCESS'), 
    (1, 'FAILED'),
    (2, 'CREATED'),
    (3, 'PENDING'),
    (4, 'APPROVED'),
    (5, 'CANCELED'),
    (6, 'COMPLETED'),
    (7, 'RESEND'),
    (8, 'REJECTED'),

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

PERMISSION_GROUP = 0
OTHER_GROUP = 1

GROUP_TYPE = (
    (PERMISSION_GROUP, 'Permission'),
    (OTHER_GROUP, 'other')
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
LIMIT_TYPE_BLOCK = 5
LIMIT_TYPE_UNBLOCK = 6

LIMIT_TYPE = (
    (LIMIT_TYPE_BET, 'Bet'),
    (LIMIT_TYPE_LOSS, 'Loss'),
    (LIMIT_TYPE_DEPOSIT, 'Deposit'),
    (LIMIT_TYPE_WITHDRAW, 'Withdraw'),
    (LIMIT_TYPE_ACCESS_DENY, 'Access Deny'),
    (LIMIT_TYPE_BLOCK, 'Block'),
    (LIMIT_TYPE_UNBLOCK, 'Unblock')
)

GAME_PRODUCT_GB_SPORTS         = 0
GAME_PRODUCT_EZ_SPORTS         = 1
GAME_PRODUCT_GAMES             = 2
GAME_PRODUCT_LOTTO             = 3
GAME_PRODUCT_LIVE_CASINO       = 4

GAME_PRODUCT = (
    (GAME_PRODUCT_GB_SPORTS, 'GB SPORTS'),
    (GAME_PRODUCT_EZ_SPORTS, 'EZ SPORTS'),
    (GAME_PRODUCT_GAMES, 'GAMES'),
    (GAME_PRODUCT_LOTTO, 'LOTTO'),
    (GAME_PRODUCT_LIVE_CASINO, 'LIVE CASINO')
)


RISK_LEVEL_A = 0
RISK_LEVEL_E1 = 1
RISK_LEVEL_E2 = 2
RISK_LEVEL_F = 3

RISK_LEVEL = (
    (RISK_LEVEL_A, 'A'),
    (RISK_LEVEL_E1, 'E1'),
    (RISK_LEVEL_E2, 'E2'),
    (RISK_LEVEL_F, 'F'),
)

INTERVAL_PER_DAY = 0
INTERVAL_PER_WEEK = 1
INTERVAL_PER_MONTH = 2
INTERVAL_PER_SIX_MONTH = 3
INTERVAL_PER_ONE_YEAR = 4
INTERVAL_PER_THREE_YEAR = 5
INTERVAL_PER_FIVE_YEAR = 6

INTERVAL = (
    (INTERVAL_PER_DAY, 'per day'),
    (INTERVAL_PER_WEEK, 'per week'),
    (INTERVAL_PER_MONTH, 'per month'),
    (INTERVAL_PER_SIX_MONTH, 'per six months'),
    (INTERVAL_PER_ONE_YEAR, 'per one year'),
    (INTERVAL_PER_THREE_YEAR, 'per three years'),
     (INTERVAL_PER_FIVE_YEAR, 'per five years'),
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
    ('47','银联支付'),
    ('49','京东支付'),
    ('201', '比特币')
)
ASIAPAY_PAYWAY_CHOICES = (
    ('90','比特币'),
    ('41', '仅支持固定存入金额'),
    ('42', 'QRCode'),
    ('44', '收银台'),
    ('30', '在线支付'),
    ('31','另开视窗'),
    ('10', '工行网银转账'),
    ('11', '工行手机支付'),

)
ASIAPAY_CMDTYPE = (
    ('01', '查询存款订单'),
    ('02', '查询提款订单'),
)
ASIAPAY_CASHOUTMETHOD_CHOICES = (
    ('CashSCBatch', '加密货币'),
    ('cashifacebatch', '代付'),
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

#astroPay sandbox url
ASTROPAY_URL = 'https://sandbox-api.astropaycard.com/'


#astroPay sandbox key:
ASTROPAY_X_LOGIN = '1PboDQ2FySeUK8YmaJTkfVlFzy0zTMvQ' 
ASTROPAY_X_TRANS_KEY = 'sQaDolJOA4cvlPoBwLXQjDAEnOO1XCjX'
ASTROPAY_SECRET = "RJLuSCDcd6mj7SoinVzkH7g2ueJRlScH"

#astroPay sandbod WEBPAYSTATUS:
ASTROPAY_WP_LOGIN = 'f1b1d639c5'
ASTROPAY_WP_TRANS_KEY = '738e34417a'

#aisa-pay
ASIAPAY_API_URL = "http://gw.wave-pay.com"
ASIAPAY_CID = "BRANDCQNGHUA3"
ASIAPAY_DEPOSITKEY = "A49E448121886D7C857B39C3467EC117"
ASIAPAY_CASHKEY = "C0076184165A61B3B0CCA4BDC21DE0D9"
ASIAPAY_CPASS = "6aC3a873Qp2cCGpQ7pDgTg58CH57cQS6"
ASIAPAY_KEY1 = "f6b451943fb44a38"
ASIAPAY_UNITEKEY = "Ki3CgDAz"
ASIAPAY_R1 = "C1aym0re"
ASIAPAY_R2 = "C1aym0re"
ASIAPAY_QRPAYWAY = "42"

#help2pay

HELP2PAY_URL = "http://api.besthappylife.biz/MerchantTransfer"
HELP2PAY_MERCHANT = "M0130"
HELP2PAY_SECURITY = "aw4uHGgeUCLrhF8"
BackURI = "http://128dbbc7.ngrok.io/accounting/api/help2pay/deposit_result"
REDIRECTURL = "http://128dbbc7.ngrok.io/accounting/api/help2pay/deposit_success"

#fgate
FGATE_URL = "https://api.fgate247.com/charge_card/"
FGATE_PARTNERID = "75"
FGATE_PARTNERKEY = "6tDJkb"
FGATE_TYPE = "fgo"