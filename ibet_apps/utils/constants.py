import os
import datetime
import boto3
import json

from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
import utils.aws_helper
from django.utils.translation import ugettext_lazy as _



AWS_S3_ADMIN_BUCKET = ""
keys = {}
load_dotenv()
print("[" + str(datetime.datetime.now()) + "] Using constants file for " + os.getenv("ENV") + " env.")

if os.getenv("ENV") != "local":
    AWS_S3_ADMIN_BUCKET = "ibet-admin-"+os.environ["ENV"]
    keys = utils.aws_helper.getThirdPartyKeys(AWS_S3_ADMIN_BUCKET, 'config/thirdPartyKeys.json')
else:
    AWS_S3_ADMIN_BUCKET = "ibet-admin-dev"
    keys = utils.aws_helper.getThirdPartyKeys(AWS_S3_ADMIN_BUCKET, 'config/thirdPartyKeys.json')

GENDER_CHOICES = (
    ('Male', 'Male'),
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
    ('THB', 'THB'),
    ('MYR', 'MYR'),
    ('VND', 'VND'),
    ('MMK', 'MMK'),
    ('XBT', 'XBT')
)

USERNAME_REGEX = '^[a-zA-Z0-9.+-]*$'

HELP2PAY    =   0
LINEPAY     =   1
ASTROPAY    =   2
QAICASH     =   3
ASIAPAY     =   4
PAYPAL      =   5
PAYZOD      =   6
CIRCLEPAY   =   7
FGATE       =   8
SCRATCHCARD =   9
PAYMENTIQ   =   10

CHANNEL_CHOICES = (
    (HELP2PAY, 'Help2Pay'),
    (LINEPAY, 'LINEpay'),
    (ASTROPAY, 'AstroPay'),
    (QAICASH, 'Qaicash'),
    (ASIAPAY, 'AsiaPay'),
    (PAYPAL, 'Paypal'),
    (PAYZOD, 'Payzod'),
    (CIRCLEPAY, 'CirclePay'),
    (FGATE, 'Fgate'),
    (SCRATCHCARD, 'ScratchCard'),
    (PAYMENTIQ, 'PaymentIQ')
)

CURRENCY_CNY = 0
CURRENCY_USD = 1
CURRENCY_THB = 2
CURRENCY_IDR = 3
CURRENCY_HKD = 4
CURRENCY_AUD = 5
CURRENCY_MYR = 6
CURRENCY_VND = 7
CURRENCY_MMK = 8
CURRENCY_XBT = 9
CURRENCY_EUR = 10
CURRENCY_NOK = 11
CURRENCY_GBP = 12

CURRENCY_CHOICES = (
    (CURRENCY_CNY, 'CNY'),
    (CURRENCY_USD, 'USD'),
    (CURRENCY_THB, 'THB'),
    (CURRENCY_IDR, 'IDR'),
    (CURRENCY_HKD, 'HKD'),
    (CURRENCY_AUD, 'AUD'),
    (CURRENCY_MYR, 'MYR'),
    (CURRENCY_VND, 'VND'),
    (CURRENCY_MMK, 'MMK'),
    (CURRENCY_XBT, 'XBT'),
    (CURRENCY_EUR, 'EUR'),
    (CURRENCY_NOK, 'NOK'),
    (CURRENCY_GBP, 'GBP')
)

TRAN_SUCCESS_TYPE = 0
TRAN_FAIL_TYPE = 1
TRAN_CREATE_TYPE = 2
TRAN_PENDING_TYPE = 3
TRAN_APPROVED_TYPE = 4
TRAN_CANCEL_TYPE = 5
TRAN_COMPLETED_TYPE = 6
TRAN_RESEND_TYPE = 7
TRAN_REJECTED_TYPE = 8
TRAN_HELD_TYPE = 9

STATE_CHOICES = (
    (TRAN_SUCCESS_TYPE, 'SUCCESS'), 
    (TRAN_FAIL_TYPE, 'FAILED'),
    (TRAN_CREATE_TYPE, 'CREATED'),
    (TRAN_PENDING_TYPE, 'PENDING'),
    (TRAN_APPROVED_TYPE, 'APPROVED'),
    (TRAN_CANCEL_TYPE, 'CANCELED'),
    (TRAN_COMPLETED_TYPE, 'COMPLETED'),
    (TRAN_RESEND_TYPE, 'RESEND'),
    (TRAN_REJECTED_TYPE, 'REJECTED'),
    (TRAN_HELD_TYPE, 'HELD'),
)

REVIEW_APP = 0
REVIEW_PEND = 1
REVIEW_REJ = 2
REVIEW_SUCCESS = 3
REVIEW_FAIL = 4
REVIEW_RESEND = 5

REVIEW_STATE_CHOICES = (
    (REVIEW_APP, 'APPROVED'),
    (REVIEW_PEND, 'PENDING'),
    (REVIEW_REJ, 'REJECTED'),
    (REVIEW_SUCCESS, 'SUCCESSFUL'),
    (REVIEW_FAIL, 'FAILED'),
    (REVIEW_RESEND, 'RESEND'),
)

DEPOSIT_METHOD_CHOICES = (
    (0, "ONLINE_DEBIT"),
    (1, "ALIPAY"),
    (2, "WECHAT_PAY"),
    (3, "CUP_QR"),
    (4, "BANK_TRANSFER"),
    (5, "ALIPAY_H5"),
    (6, "WECHAT_PAY_H5"),
    (7, "CUP"),
    (8, "CUP_MOBILE"),
    (9, "JDWALLET"),

)

# transaction_deposit = 0
# transaction_withdrawl = 1
TRANSACTION_DEPOSIT = 0
TRANSACTION_WITHDRAWAL = 1
TRANSACTION_BET_PLACED = 2
TRANSACTION_SETTLED = 3
TRANSACTION_TRANSFER_IN = 4
TRANSACTION_TRANSFER_OUT = 5
TRANSACTION_BONUS = 6
TRANSACTION_ADJUSTMENT = 7
TRANSACTION_COMMISSION = 8

TRANSACTION_TYPE_CHOICES = (
    (TRANSACTION_DEPOSIT, 'Deposit'),
    (TRANSACTION_WITHDRAWAL, 'Withdrawal'),
    (TRANSACTION_BET_PLACED, 'Bet Placed'),
    (TRANSACTION_SETTLED, 'Bet Settled'),
    (TRANSACTION_TRANSFER_IN, 'Transfer in'),
    (TRANSACTION_TRANSFER_OUT, 'Transfer out'),
    (TRANSACTION_BONUS, 'Bonus'),
    (TRANSACTION_ADJUSTMENT, 'Adjustment'),
    (TRANSACTION_COMMISSION, 'Commission')
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

ACTIVE_STATE = 0
DISABLED_STATE = 1

THIRDPARTY_STATUS_CHOICES = (
    (ACTIVE_STATE, "ACTIVE"), 
    (DISABLED_STATE, "DISABLED")
)

VIP_1 = 1
VIP_2 = 2
VIP_3 = 3
VIP_4 = 4
VIP_5 = 5
VIP_6 = 6

VIP_CHOICES = (
    (VIP_1, "VIP_1"),
    (VIP_2, "VIP_2"),
    (VIP_3, "VIP_3"),
    (VIP_4, "VIP_4"),
    (VIP_5, "VIP_5"),
    (VIP_6, "VIP_6"),
)

ibetVN = 0
ibetTH = 1

MARKET_CHOICES = (
    (ibetVN, "ibet-VN"),
    (ibetTH, "ibet-TH"),
)

COUNTRY_CHOICES = (
    ('US', 'United States'),
    ('CN', 'China'),
    ('TH', 'Thailand'),
    ('JP', 'Japan'),
)

ACTIVITY_SYSTEM = 0     # System Change
ACTIVITY_REMARK = 1     # Remark in form
ACTIVITY_MESSAGE = 2    # Inbox message
ACTIVITY_NOTE= 3        # Note in activity

ACTIVITY_TYPE = (
    (0, 'System'),
    (1, 'Remark'),
    (2, 'Message'),
    (3, 'Note'),
)

AFFILIATE_STATUS = (
    ('Active', 'Active'),
    ('VIP', 'VIP'),
    ('Negative', 'Negative'),
    ('Deactivated', 'Deactivated'),
)

AGENT_STATUS = (
    ('Normal', 'Normal'),
    ('Block', 'Block'),
)

PERMISSION_GROUP = 0
OTHER_GROUP = 1
MESSAGE_GROUP = 2

GROUP_TYPE = (
    (PERMISSION_GROUP, 'Permission'),
    (MESSAGE_GROUP, 'message'),
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

TEMPORARY_INTERVAL = (
    (INTERVAL_PER_DAY, 'day'),
    (INTERVAL_PER_WEEK, 'week'),
    (INTERVAL_PER_MONTH, 'month'),
)

PERMANENT_INTERVAL = (
    (INTERVAL_PER_SIX_MONTH, 'six months'),
    (INTERVAL_PER_ONE_YEAR, 'one year'),
    (INTERVAL_PER_THREE_YEAR, 'three years'),
    (INTERVAL_PER_FIVE_YEAR, 'five years'),
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
    ('10', '网银转账'),
    ('11', '工行手机支付'),

)

GAME_PROVIDER_NETENT = 0
GAME_PROVIDER_PLAY_GO = 1
GAME_PROVIDER_BIG_TIME_GAMING = 2
GAME_PROVIDER_MICROGAMING = 3
GAME_PROVIDER_QUICKSPIN = 4
GAME_PROVIDER_PRAGMATIC_PLAY = 5
GAME_PROVIDER_BLUEPRINT = 6
GAME_PROVIDER_NOVOMATIC = 7
GAME_PROVIDER_IGT = 8
GAME_PROVIDER_ELK_STUDIOS = 9
GAME_PROVIDER_GENESIS = 10
GAME_PROVIDER_HIGH5 = 11
GAME_PROVIDER_IRON_DOG = 12
GAME_PROVIDER_JUST_FOR_THE_WIN = 13
GAME_PROVIDER_KALAMBA = 14
GAME_PROVIDER_LEANDER = 15
GAME_PROVIDER_LIGHTNING_BOX = 16
GAME_PROVIDER_NEXTGON = 17
GAME_PROVIDER_RED7= 18
GAME_PROVIDER_RED_TIGET_GAMING= 19
GAME_PROVIDER_SCIENTIFIC_GAMES= 20
GAME_PROVIDER_THUNDERKICK = 21
GAME_PROVIDER_YGGDRASIL = 22


GAME_PROVIDERS = (
    (GAME_PROVIDER_NETENT, 'Netent'),
    (GAME_PROVIDER_PLAY_GO, 'Play\'n Go'),
    (GAME_PROVIDER_BIG_TIME_GAMING, 'Big Time Gaming'),
    (GAME_PROVIDER_MICROGAMING, 'Microgaming'),
    (GAME_PROVIDER_QUICKSPIN, 'Quickspin'),
    (GAME_PROVIDER_PRAGMATIC_PLAY, 'Progmatic Play'),
    (GAME_PROVIDER_BLUEPRINT, 'Blueprint'),
    (GAME_PROVIDER_NOVOMATIC, 'Novomatic'),
    (GAME_PROVIDER_IGT, 'IGT'),
    (GAME_PROVIDER_ELK_STUDIOS, 'Elk Studio'),
    (GAME_PROVIDER_GENESIS, 'Genesis'),
    (GAME_PROVIDER_HIGH5, 'High5'),
    (GAME_PROVIDER_IRON_DOG, 'Iron Dog'),
    (GAME_PROVIDER_JUST_FOR_THE_WIN, 'Just For The Win'),
    (GAME_PROVIDER_KALAMBA, 'Kalamba'),
    (GAME_PROVIDER_LEANDER, 'Leander'),
    (GAME_PROVIDER_LIGHTNING_BOX, 'Lightning Box'),
    (GAME_PROVIDER_NEXTGON, 'Nextgen'),
    (GAME_PROVIDER_RED7, 'Red7'),
    (GAME_PROVIDER_RED_TIGET_GAMING, 'Red Tiger Gaming'),
    (GAME_PROVIDER_SCIENTIFIC_GAMES, 'Scientific Games'),
    (GAME_PROVIDER_THUNDERKICK, 'Thunderkick'),
    (GAME_PROVIDER_YGGDRASIL, 'Yggdrasil'),
)

CATEGORY_TYPES_SPORTS = 0
CATEGORY_TYPES_LIVE_CASINO = 1
CATEGORY_TYPES_SLOTS = 2
CATEGORY_TYPES_LOTTERY = 3



CATEGORY_TYPES = (
    (CATEGORY_TYPES_SPORTS, 'SPORTS'),
    (CATEGORY_TYPES_LIVE_CASINO, 'LIVE CASINO'),
    (CATEGORY_TYPES_SLOTS, 'SLOTS'),
    (CATEGORY_TYPES_LOTTERY, 'LOTTERY'),
)

GAME_ATTRIBUTES_GAME_CATEGORY = 0
GAME_ATTRIBUTES_JACKPOT = 1
GAME_ATTRIBUTES_PROVIDER = 2
GAME_ATTRIBUTES_FEATURES = 3
GAME_ATTRIBUTES_THEME = 4

GAME_ATTRIBUTES = (
    (GAME_ATTRIBUTES_GAME_CATEGORY, 'Games Category'),
    (GAME_ATTRIBUTES_JACKPOT, 'Jackpot'),
    (GAME_ATTRIBUTES_PROVIDER, 'Provider'),
    (GAME_ATTRIBUTES_FEATURES, 'Features'),
    (GAME_ATTRIBUTES_THEME, 'Theme'),
)

ACTIVITY_CHECK_FIVE_MIN = 0
ACTIVITY_CHECK_HALF_HOUR = 1
ACTIVITY_CHECK_ONE_HOUR = 2
ACTIVITY_CHECK_TWO_HOURS = 3

ACTIVITY_CHECK = (
    (ACTIVITY_CHECK_FIVE_MIN, '5 minutes'),
    (ACTIVITY_CHECK_HALF_HOUR, '30 minutes'),
    (ACTIVITY_CHECK_ONE_HOUR, '60 minutes'),
    (ACTIVITY_CHECK_TWO_HOURS, '120 minutes'),
)


EVENT_CHOICES_LOGIN = 0
EVENT_CHOICES_LOGOUT = 1
EVENT_CHOICES_REGISTER = 2
EVENT_CHOICES_PAGE_VISIT = 3

EVENT_CHOICES = (
    (EVENT_CHOICES_LOGIN, _('Login')),
    (EVENT_CHOICES_LOGOUT, _('Logout')),
    (EVENT_CHOICES_REGISTER, _('Register')),
    # (3, _('Deposit')),
    # (4, _('Withdraw')),
    (EVENT_CHOICES_PAGE_VISIT, _('Page Visit')),
    # (6, _('bet'))
)



ASIAPAY_CMDTYPE = (
    ('01', '查询存款订单'),
    ('02', '查询提款订单'),
)
ASIAPAY_CASHOUTMETHOD_CHOICES = (
    ('CashSCBatch', '加密货币'),
    ('cashifacebatch', '代付'),
)

LOCALHOST = "http://localhost:3000"
DEV_URL = "https://ibet-web-dev.claymoreusa.net"

# LINEpay
LINE_PAYMENTS_SANDBOX_URL = "https://sandbox-api-pay.line.me/v2/payments/"
PRODUCT_IMG_URL = "https://pathtoproductimage.jpg"  # dummy image, will be replaced with actual company URL later

# qaicash-payment
QAICASH_URL = keys["QAICASH"]["URL"]
MERCHANTID = keys["QAICASH"]["MERCHANTID"]
MERCHANTAPIKEY = keys["QAICASH"]["MERCHANTAPIKEY"]
APIVERSION = keys["QAICASH"]["APIVERSION"]
DEPOSIT_URL = keys["QAICASH"]["DEPOSIT_URL"]
PAYOUT_URL = keys["QAICASH"]["PAYOUT_URL"]

# paypal-payment
PAYPAL_MODE = 'sandbox'   # sandbox or live
PAYPAL_CLIENT_ID = 'AXoM7FKTdT8rfh-SI66SlAWd_P85YSsNfTvm0zjB0-AhJhUhUHTuXi4L87DcgkxLSLPYKCMO5DVl2pDD'
PAYPAL_CLIENT_SECRET = 'ENKmcu7Sci-RHW2gHvzmeUbZvSaCuwRiEirKH0_TkYo4AZWbVnfevS-hxq6cS6sevLU5TB3SMfq85wSB'
PAYPAL_SANDBOX_URL = 'https://api.sandbox.paypal.com/'


if os.getenv("ENV") != "local":
    # fetch prod credentials from s3
    ASTROPAY_URL = "https://api.astropaycard.com"
    ASTROPAY_X_LOGIN = keys["ASTROPAY"]["X_LOGIN"]
    ASTROPAY_X_TRANS_KEY = keys["ASTROPAY"]["X_TRANS_KEY"]
    ASTROPAY_SECRET = keys["ASTROPAY"]["SECRET"]
    # print(ASTROPAY_X_LOGIN, ASTROPAY_X_TRANS_KEY, ASTROPAY_SECRET)
else:
    # astroPay sandbox keys:
    ASTROPAY_URL = 'https://sandbox-api.astropaycard.com'  # astroPay sandbox url
    ASTROPAY_X_LOGIN = '1PboDQ2FySeUK8YmaJTkfVlFzy0zTMvQ'
    ASTROPAY_X_TRANS_KEY = 'sQaDolJOA4cvlPoBwLXQjDAEnOO1XCjX'
    ASTROPAY_SECRET = "RJLuSCDcd6mj7SoinVzkH7g2ueJRlScH"


# fgo
FGATE_URL = keys["FGO"]["URL"]
FGATE_PARTNERID = keys["FGO"]["PARTNERID"]
FGATE_PARTNERKEY = keys["FGO"]["PARTNERKEY"]
FGATE_TYPE = keys["FGO"]["TYPE"]

# astroPay sandbod WEBPAYSTATUS:
ASTROPAY_WP_LOGIN = 'f1b1d639c5'
ASTROPAY_WP_TRANS_KEY = '738e34417a'

# circlepay
CIRCLEPAY_USERCODE = keys["CIRCLEPAY"]["USERCODE"]
CIRCLEPAY_API_KEY = keys["CIRCLEPAY"]["API_KEY"]
CIRCLEPAY_EMAIL = keys["CIRCLEPAY"]["EMAIL"]
CIRCLEPAY_DEPOSIT_URL = "https://gateway.circlepay.ph/payment/"
CIRCLEPAY_CHECK_STATUS_URL = "https://api.circlepay.ph/transaction/"

# scratch card API
SCRATCHCARD_URL = "https://api.thethanhtien.com/charge-card/"
SCRATCHCARD_PARTNER_ID = keys["SCRATCHCARD"]["PARTNER_ID"]
SCRATCHCARD_CODE = keys["SCRATCHCARD"]["CODE"]
SCRATCHCARD_EMAIL = keys["SCRATCHCARD"]["EMAIL"]

# asia-pay
ASIAPAY_API_URL = keys["ASIAPAY"]["API_URL"]
ASIAPAY_CID = keys["ASIAPAY"]["CID"]
ASIAPAY_DEPOSITKEY = keys["ASIAPAY"]["DEPOSITKEY"]
ASIAPAY_CASHKEY = keys["ASIAPAY"]["CASHKEY"]
ASIAPAY_CPASS = keys["ASIAPAY"]["CPASS"]
ASIAPAY_KEY1 = keys["ASIAPAY"]["KEY1"]
ASIAPAY_UNITEKEY = keys["ASIAPAY"]["UNITEKEY"]
ASIAPAY_R1 = keys["ASIAPAY"]["R1"]
ASIAPAY_R2 = keys["ASIAPAY"]["R2"]
ASIAPAY_QRPAYWAY = keys["ASIAPAY"]["QRPAYWAY"]
ASIAPAY_TRUSTUSER = keys["ASIAPAY"]["TRUSTUSER"]

# help2pay sandbox credentials & callback

HELP2PAY_MERCHANT_THB = "M0513"
HELP2PAY_MERCHANT_VND = "M0514"
HELP2PAY_CONFIRM_PATH = "accounting/api/help2pay/deposit_result"
HELP2PAY_SUCCESS_PATH = "accounting/api/help2pay/deposit_success"

if os.getenv("ENV") != "local":  # fetch prod credentials from s3
    API_DOMAIN = "https://payment-testing.claymoreeuro.com/"
    HELP2PAY_SECURITY_THB = keys["HELP2PAY"]["PRODUCTION"]["TH"]
    HELP2PAY_SECURITY_VND = keys["HELP2PAY"]["PRODUCTION"]["VN"]
    HELP2PAY_URL = "https://api.racethewind.net/MerchantTransfer"
else:
    API_DOMAIN = "https://754dc8ae.ngrok.io/"
    HELP2PAY_SECURITY_THB = keys["HELP2PAY"]["SANDBOX"]["TH"]
    HELP2PAY_SECURITY_VND = keys["HELP2PAY"]["SANDBOX"]["VN"]
    HELP2PAY_URL = "http://api.besthappylife.biz/MerchantTransfer"

BackURI = "http://128dbbc7.ngrok.io/accounting/api/help2pay/deposit_result"
REDIRECTURL = "http://128dbbc7.ngrok.io/accounting/api/help2pay/deposit_success"

# payzod production
# TODO: Will need to update Production credentials because these credentials are temporary
if os.getenv("ENV") != "local":  # fetch prod credentials from s3
    PAYZOD_API_URL = "https://www.payzod.com/api/qr/"
    PAYZOD_MERCHANT_ID = keys["PAYZOD"]["PRODUCTION"]["MERCHANT_ID"]
    PAYZOD_MERCHANT_NAME = keys["PAYZOD"]["PRODUCTION"]["MERCHANT_NAME"]
    PAYZOD_PASSKEY = keys["PAYZOD"]["PRODUCTION"]["PASSKEY"]
else:  # payzod sandbox
    PAYZOD_API_URL = "https://dev.payzod.com/api/qr/"
    PAYZOD_MERCHANT_ID = keys["PAYZOD"]["SANDBOX"]["MERCHANT_ID"]
    PAYZOD_MERCHANT_NAME = keys["PAYZOD"]["SANDBOX"]["MERCHANT_NAME"]
    PAYZOD_PASSKEY = keys["PAYZOD"]["SANDBOX"]["PASSKEY"]


GAME_FILTER_OPTION = [
    {
        'name': 'Games Category',
        'data': ['New', 'Popular', 'Table Games', 'Slots', 'All Games']
    },
    {
        'name': 'Jackpot',
        'data': ['Daily Jackpots', 'Fixed Jackpots', 'Progressive Jackpot', 'Multiple Jackpots']
    },
    {
        'name': 'Provider',
        'data': ['Netent', 'Play\'n Go', 'Big Time Gaming', 'Microgaming', 'Quickspin', 'Pragmatic Play', 'Blueprint', 'Novomatic', 'IGT', 'Elk Studios',
        'Genesis', 'High5', 'Iron Dog', 'Just For The Win', 'Kalamba', 'Leander', 'Lightning Box', 'Nextgen', 'Red7', 'Red Tiger Gaming', 'Scientific Games', 
        'Thunderkick', 'Yggdrasil', 'Other']
    },
    {
        'name': 'Feature',
        'data': ['Megaways', 'Pay Both Ways', 'Bonus Feature', 'Free Spins', 'Double Or Nothing Feature']
    },
    {
        'name': 'Theme',
        'data': ['Egypt', 'Oriental', 'Mythology', 'Animal', 'Adventure', 'Fruit', 'Western', 'Film / Tv', 'Music', 'Sports',
            'Space', 'Holidays', 'Dark/ Halloween', 'Vegas']
    },
    {
        'name': 'Sort by',
        'data': ['Name', 'Popularity', 'Jackpot Size Asc', 'Jackpot Size Desc']
    },
]

# Notification
MESSAGE_REJECTED = 0
MESSAGE_PENDING  = 1
MESSAGE_APPROVED = 2

NOTIFICATION_STATUS = (
    (MESSAGE_REJECTED, 'REJECTED'),
    (MESSAGE_PENDING, 'PENDING'),
    (MESSAGE_APPROVED, 'APPROVED')
)

SYSTEM_USER = 1

NOTIFICATION_CONSTRAINTS_QUANTITY = 1000

AWS_SMS_REGION = 'eu-west-1'
AWS_SQS_REGION = 'eu-west-2'

COUNTRY_CODE_CHINA = 'CNY'
COUNTRY_CODE_GERMANY = 'DE'
COUNTRY_CODE_FINAND = 'FI'
COUNTRY_CODE_NORWAY = 'NO'
COUNTRY_CODE_THAILAND = 'THB'
COUNTRY_CODE_VIETNAM = 'VN'
COUNTRY_CODE_NETHERLANDS = 'NL'
COUNTRY_CODE_UNITED_KINGDOM = 'UK'

MARKET_OPTIONS = {
    'ibetMarket_options': [
        COUNTRY_CODE_CHINA,
        COUNTRY_CODE_GERMANY,
        COUNTRY_CODE_FINAND,
        COUNTRY_CODE_NORWAY,
        COUNTRY_CODE_THAILAND,
        COUNTRY_CODE_VIETNAM,
        COUNTRY_CODE_NETHERLANDS,
        COUNTRY_CODE_UNITED_KINGDOM
    ],
    'letouMarket_options': [
        COUNTRY_CODE_CHINA,
        COUNTRY_CODE_THAILAND,
        COUNTRY_CODE_VIETNAM
    ]
}

COUNTRY_CODE_TO_IMG_PREFIX = {
    COUNTRY_CODE_CHINA: 'china',
    COUNTRY_CODE_GERMANY: 'germany',
    COUNTRY_CODE_FINAND: 'finland',
    COUNTRY_CODE_NORWAY: 'norway',
    COUNTRY_CODE_THAILAND: 'thailand',
    COUNTRY_CODE_VIETNAM: 'vietnam',
    COUNTRY_CODE_NETHERLANDS: 'netherlands',
    COUNTRY_CODE_UNITED_KINGDOM: 'united-kingdom'

}

DEPARTMENT_LIST = [
    {
        'code': '1',
        'name': 'Customer service'
    },
    {
        'code': '2',
        'name': 'Payments'
    },
    {
        'code': '3',
        'name': 'Risk'
    },
    {
        'code': '4',
        'name': 'Marketing'
    },
    {
        'code': '5',
        'name': 'IT Operations'
    },
    {
        'code': '6',
        'name': 'Finance'
    },
    {
        'code': '7',
        'name': 'HR'
    },
    {
        'code': '8',
        'name': 'Sportsbook'
    }
]


PERMISSION_CODE = [
    {   
        "name": "Members",
        "permission": [],
        "menu": [
            {
                "name": "Members list",
                "permission": [
                    {
                        "CODE": "1001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "1002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "1003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Member details",
                "permission": [
                    {
                        "CODE": "2001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "2002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "2003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    },
    {   
        "name": "Report",
        "permission": [
            {
                "CODE": "3001",
                "PERMISSION": "No access"

            },{
                "CODE": "3002",
                "PERMISSION": "READ"
            },
            {
                "CODE": "3003",
                "PERMISSION": "ALL"
            }
        ]
    },
    {   
        "name": "Bonuses",
        "permission": [
            {
                "CODE": "4001",
                "PERMISSION": "No access"
                
            },{
                "CODE": "4002",
                "PERMISSION": "READ"
            },
            {
                "CODE": "4003",
                "PERMISSION": "ALL"
            }
        ]
    },
    {   
        "name": "Risk control",
        "permission": [
            {
                "CODE": "5001",
                "PERMISSION": "No access"

            },{
                "CODE": "5002",
                "PERMISSION": "READ"
            },
            {
                "CODE": "5003",
                "PERMISSION": "ALL"
            }
        ]
    },
    {   
        "name": "Marketing",
        "permission": [],
        "menu": [
            {
                "name": "VIP",
                "permission": [
                    {
                        "CODE": "6001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "6002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "6003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Telesales",
                "permission": [
                    {
                        "CODE": "7001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "7002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "7003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Interal messaging",
                "permission": [
                    {
                        "CODE": "8001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "8002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "8003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    },
    {   
        "name": "Affiliates",
        "permission": [],
        "menu": [
            {
                "name": "Affiliates list",
                "permission": [
                    {
                        "CODE": "9001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "9002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "9003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Affiliate details",
                "permission": [
                    {
                        "CODE": "10001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "10002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "10003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    },
    {   
        "name": "Messaging",
        "permission": [],
        "menu": [
            {
                "name": "Messages",
                "permission": [
                    {
                        "CODE": "11001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "12002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "12003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Group",
                "permission": [
                    {
                        "CODE": "14001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "14002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "14003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Campaigns",
                "permission": [
                    {
                        "CODE": "15001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "15002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "15003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    },
    {   
        "name": "Finance",
        "permission": [],
        "menu": [
            {
                "name": "Deposits",
                "permission": [
                    {
                        "CODE": "16001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "16002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "16003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Withdrawals",
                "permission": [
                    {
                        "CODE": "17001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "17002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "17003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Settings",
                "permission": [
                    {
                        "CODE": "18001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "18002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "18003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    },
    {   
        "name": "Content management",
        "permission": [
            {
                "CODE": "19001",
                "PERMISSION": "No access"

            },
            {
                "CODE": "19002",
                "PERMISSION": "READ"
            },
            {
                "CODE": "19003",
                "PERMISSION": "ALL"
            }
        ]
    },
    {   
        "name": "System admin",
        "permission": [],
        "menu": [
            {
                "name": "Users",
                "permission": [
                    {
                        "CODE": "20001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "20002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "20003",
                        "PERMISSION": "ALL"
                    }
                ]
            },
            {
                "name": "Roles",
                "permission": [
                    {
                        "CODE": "21001",
                        "PERMISSION": "No access"
                    },
                    {
                        "CODE": "21002",
                        "PERMISSION": "READ"
                    },
                    {
                        "CODE": "21003",
                        "PERMISSION": "ALL"
                    }
                ]
            }
        ]
    }
]

# agent
COMMISSION_SET = (
    ('System', 'System'),
    ('Personal', 'Personal'),
)

AFFILIATE_LEVEL = (
    ('Normal', 'Normal'),
    ('VIP', 'VIP'),
)

LETOU_DOMAIN="https://www.letou.com/"   # for affiliate refer link

MONTHLY_COMMISSION_SETTLE_DATE = "05"


BONUS_QUEUE_NAME = "bonus_queue"
BONUS_QUEUE_CL_NAME = "bonus_queue_cl"

PUBLIC_S3_BUCKET = "https://ibet-web.s3-us-west-1.amazonaws.com/"

# Error code define
ERROR_CODE_SUCCESS = 1
ERROR_CODE_BLOCK = 100
ERROR_CODE_INVAILD_INFO = 101
ERROR_CODE_INACTIVE = 102
ERRPR_CODE_NOT_FOUND = 103



BONUS_TYPE_VERIFICATION = 0
BONUS_TYPE_DEPOSIT = 1
BONUS_TYPE_TURNOVER = 2
BONUS_TYPE_STANDARD = 3
BONUS_TYPE_FREESPINS = 4

BONUS_TYPE_CHOICES = (
    (BONUS_TYPE_VERIFICATION, 'VERIFICATION'),
    (BONUS_TYPE_DEPOSIT, 'DEPOSIT'),
    (BONUS_TYPE_TURNOVER, 'TURNOVER'),
    (BONUS_TYPE_STANDARD, 'STANDARD'),
    (BONUS_TYPE_FREESPINS, 'FREE SPINS'),
)

BONUS_STATUS_CHOICES = (
    (0, 'INACTIVE'),
    (1, 'ACTIVE'),
    (2, 'DISABLED'),
)


USER_BONUS_EVENT_TYPE_CHOICES = (
    (0, 'STARTED'),
    (1, 'ACTIVE'),
    (2, 'COMPLETED'),
    (3, 'EXPIRED'),
)

BONUS_RELEASE_TYPE_CHOICES = (
    (0, 'Pre-wager'),
    (1, 'Post-wager'),
)

BONUS_AGGREGATE_METHOD_CHOICES = (
    (0, 'SUM'),
    (1, 'COUNT'),
    (2, 'AVERAGE'),
    (3, 'MAX'),
    (4, 'LATEST'),
)

BRAND_OPTIONS = (
    ('letou', 'Letou'),
    ('ibet', 'iBet')
)
