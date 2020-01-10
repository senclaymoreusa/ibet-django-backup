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
PTKEY = b""
PTPEM = b""

print("env:" +os.getenv("ENV"))
print("datetime:" + str(datetime.datetime.now()))
print("[" + str(datetime.datetime.now()) + "] Using constants file for " + os.getenv("ENV") + " env.")

if os.getenv("ENV") != "local":
    AWS_S3_ADMIN_BUCKET = "ibet-admin-"+os.environ["ENV"]
    keys = utils.aws_helper.getThirdPartyKeys(AWS_S3_ADMIN_BUCKET, 'config/thirdPartyKeys.json')
    PTKEY= utils.aws_helper.getPTCertContent(AWS_S3_ADMIN_BUCKET, 'PT_CERT/CNY_UAT_FB88.key')
    PTPEM = utils.aws_helper.getPTCertContent(AWS_S3_ADMIN_BUCKET, 'PT_CERT/CNY_UAT_FB88.pem')
    
   
else:
    AWS_S3_ADMIN_BUCKET = "ibet-admin-dev"
    keys = utils.aws_helper.getThirdPartyKeys(AWS_S3_ADMIN_BUCKET, 'config/thirdPartyKeys.json')
    PTKEY = utils.aws_helper.getPTCertContent(AWS_S3_ADMIN_BUCKET, 'PT_CERT/CNY_UAT_FB88.key')
    PTPEM = utils.aws_helper.getPTCertContent(AWS_S3_ADMIN_BUCKET, 'PT_CERT/CNY_UAT_FB88.pem')
  
   
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

# CURRENCY_TYPES = (
#     ('USD', 'USD'),
#     ('EUR', 'EUR'),
#     ('JPY', 'JPY'),
#     ('CNY', 'CNY'),
#     ('HKD', 'HKD'),
#     ('AUD', 'AUD'),
#     ('THB', 'THB'),
#     ('MYR', 'MYR'),
#     ('VND', 'VND'),
#     ('MMK', 'MMK'),
#     ('XBT', 'XBT'),
#     ('TTC', 'TTC'),
# )

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
LBT         =   11

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
    (PAYMENTIQ, 'PaymentIQ'),
    (LBT, 'Local Bank Transfer')
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
CURRENCY_TEST = 20
CURRENCY_TTC = 13

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
    (CURRENCY_GBP, 'GBP'),
    (CURRENCY_TEST, 'UUD'),
    (CURRENCY_TTC, 'TTC')
)

TRAN_SUCCESS_TYPE = 0  # deposit / withdraw
TRAN_FAIL_TYPE = 1  # deposit / withdraw
TRAN_CREATE_TYPE = 2  # deposit / withdraw
TRAN_PENDING_TYPE = 3  # deposit / withdraw
TRAN_APPROVED_TYPE = 4  # not being used 
TRAN_CANCEL_TYPE = 5  # deposit / withdraw
TRAN_COMPLETED_TYPE = 6  
TRAN_RESEND_TYPE = 7    
TRAN_REJECTED_TYPE = 8  # withdraw
TRAN_RISK_REVIEW = 9  # withdraw

STATE_CHOICES = (
    (TRAN_SUCCESS_TYPE, 'Success'),
    (TRAN_FAIL_TYPE, 'Failed'),
    (TRAN_CREATE_TYPE, 'Created'),
    (TRAN_PENDING_TYPE, 'Pending'),
    (TRAN_APPROVED_TYPE, 'Approved'),    # not being used 
    (TRAN_CANCEL_TYPE, 'Canceled'),
    (TRAN_COMPLETED_TYPE, 'Completed'),
    (TRAN_RESEND_TYPE, 'Resent'),
    (TRAN_REJECTED_TYPE, 'Rejected'),
    (TRAN_RISK_REVIEW, 'Review'),
)

TRAN_STATUS_DICT = {
    'success': 0,
    'failed': 1,
    'created': 2,
    'pending': 3,
    'canceled': 5,
    'rejected': 8,
    'review': 9
}

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

TRANSACTION_DEPOSIT = 0
TRANSACTION_WITHDRAWAL = 1
TRANSACTION_BET_PLACED = 2
TRANSACTION_SETTLED = 3
TRANSACTION_TRANSFER = 4
TRANSACTION_BONUS = 5
TRANSACTION_ADJUSTMENT = 6
TRANSACTION_COMMISSION = 7

TRANSACTION_TYPE_CHOICES = (
    (TRANSACTION_DEPOSIT, 'Deposit'),
    (TRANSACTION_WITHDRAWAL, 'Withdrawal'),
    (TRANSACTION_BET_PLACED, 'Bet Placed'),
    (TRANSACTION_SETTLED, 'Bet Settled'),
    (TRANSACTION_TRANSFER, 'Transfer'),
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

GAME_TYPE_SPORTS = 0
GAME_TYPE_GAMES = 1
GAME_TYPE_LIVE_CASINO = 2
GAME_TYPE_TABLE_GAMES = 3
GAME_TYPE_GENERAL = 4

GAME_TYPE_CHOICES = (
    (GAME_TYPE_SPORTS, 'Sports'),
    (GAME_TYPE_GAMES, 'Games'),
    (GAME_TYPE_LIVE_CASINO, 'Live Casino'),
    (GAME_TYPE_TABLE_GAMES, 'Table Games'),
    (GAME_TYPE_GENERAL, 'General'),
)

SPREAD = 'SPREAD'
MONEYLINE = 'LINE'
TOTAL = 'OU'
TIP = 'TIP'
SINGLE = 'Single'
PARLAY = 'Parlay'
OTHER = 'Other'

BET_TYPES_CHOICES = [
    (SPREAD, 'Spread'),
    (MONEYLINE, 'Moneyline'),
    (TOTAL, 'Total O/U'),
    (TIP, 'Tip'),
    (SINGLE, 'Single'),
    (PARLAY,'Parlay'),
    (OTHER, 'Other'),

]
OUTCOME_CHOICES = [
    (0, 'Win'),
    (1, 'Lose'),
    (2, 'Tie/Push'),
    (3, 'Void'),
    (4, 'Running'),
    (5, 'Draw'),
    (6, 'Half lose'),
    (7, 'Rollback'),
    (8, 'Cancel'),
    (9, 'Cash'),
    (10, 'Half won'),
    (11, 'reject'),
    (12, 'waiting'),
    (13, 'waiting running'),
    (14, 'refund'),
]

ACTIVE_STATE = 0
DISABLED_STATE = 1

THIRDPARTY_STATUS_CHOICES = (
    (ACTIVE_STATE, "Active"), 
    (DISABLED_STATE, "Disabled")
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
ibetCN = 2
letouVN = 3
letouTH = 4
letouCN = 5

MARKET_CHOICES = (
    (ibetVN, "ibet-VN"),
    (ibetTH, "ibet-TH"),
    (ibetCN, "ibet-CN"),
    (letouVN, "letou-VN"),
    (letouTH, "letou-TH"),
    (letouCN, "letou-CN")
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


MEMBER_STATUS_NORMAL = 0
MEMBER_STATUS_SUSPICIOUS = 1
MEMBER_STATUS_RESTRICTED = 2
MEMBER_STATUS_CLOSED = 3
MEMBER_STATUS_BLACKLISTED = 4


MEMBER_STATUS = (
    (MEMBER_STATUS_NORMAL, _('Normal')),
    (MEMBER_STATUS_SUSPICIOUS, _('Suspicious')),
    (MEMBER_STATUS_RESTRICTED, _('Restricted')),
    (MEMBER_STATUS_CLOSED, _('Closed')),
    (MEMBER_STATUS_BLACKLISTED, _('Blacklisted'))
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
MESSAGE_DYNAMIC_GROUP = 3

GROUP_TYPE = (
    (PERMISSION_GROUP, 'Permission'),
    (MESSAGE_GROUP, 'Static'),
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
EVENT_CHOICES_SMS_CODE = 7

EVENT_CHOICES = (
    (EVENT_CHOICES_LOGIN, _('Login')),
    (EVENT_CHOICES_LOGOUT, _('Logout')),
    (EVENT_CHOICES_REGISTER, _('Register')),
    # (3, _('Deposit')),
    # (4, _('Withdraw')),
    (EVENT_CHOICES_PAGE_VISIT, _('Page Visit')),
    # (6, _('bet'))
    (EVENT_CHOICES_SMS_CODE, _('SMS CODE')),
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



if os.getenv("ENV") == "local" or "dev" in os.getenv("ENV"):
    # qaicash-payment staging
    QAICASH_URL = keys["QAICASH"]["STAGING"]["URL"]
    MERCHANTID = keys["QAICASH"]["STAGING"]["MERCHANTID"]
    MERCHANTAPIKEY = keys["QAICASH"]["STAGING"]["MERCHANTAPIKEY"]
    APIVERSION = keys["QAICASH"]["STAGING"]["APIVERSION"]
    DEPOSIT_URL = keys["QAICASH"]["STAGING"]["DEPOSIT_URL"]
    PAYOUT_URL = keys["QAICASH"]["STAGING"]["PAYOUT_URL"]
    CALLBACK_URL = keys["QAICASH"]["STAGING"]["CALLBACK_URL"]

elif "prod" in os.getenv("ENV"):
     # qaicash-payment production
    QAICASH_URL = keys["QAICASH"]["PRODUCTION"]["URL"]
    MERCHANTID = keys["QAICASH"]["PRODUCTION"]["MERCHANTID"]
    MERCHANTAPIKEY = keys["QAICASH"]["PRODUCTION"]["MERCHANTAPIKEY"]
    APIVERSION = keys["QAICASH"]["PRODUCTION"]["APIVERSION"]
    DEPOSIT_URL = keys["QAICASH"]["PRODUCTION"]["DEPOSIT_URL"]
    PAYOUT_URL = keys["QAICASH"]["PRODUCTION"]["PAYOUT_URL"]
    CALLBACK_URL = keys["QAICASH"]["PRODUCTION"]["CALLBACK_URL"]

# paypal-payment
PAYPAL_MODE = 'sandbox'   # sandbox or live
PAYPAL_CLIENT_ID = 'AXoM7FKTdT8rfh-SI66SlAWd_P85YSsNfTvm0zjB0-AhJhUhUHTuXi4L87DcgkxLSLPYKCMO5DVl2pDD'
PAYPAL_CLIENT_SECRET = 'ENKmcu7Sci-RHW2gHvzmeUbZvSaCuwRiEirKH0_TkYo4AZWbVnfevS-hxq6cS6sevLU5TB3SMfq85wSB'
PAYPAL_SANDBOX_URL = 'https://api.sandbox.paypal.com/'





# fgo
FGATE_URL = keys["FGO"]["URL"]
FGATE_PARTNERID = keys["FGO"]["PARTNERID"]
FGATE_PARTNERKEY = keys["FGO"]["PARTNERKEY"]
FGATE_TYPE = keys["FGO"]["TYPE"]

# astroPay sandbod WEBPAYSTATUS:
ASTROPAY_WP_LOGIN = 'f1b1d639c5'
ASTROPAY_WP_TRANS_KEY = '738e34417a'

# circlepay -- doesn't have a sandbox 
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

#iovation
IOVATION_SUBSCRIBERID = keys["IOVATION"]["SUBSCRIBERID"] 
IOVATION_ACCOUNT = keys["IOVATION"]["ACCOUNT"] 
IOVATION_PASSWORD = keys["IOVATION"]["PASSWORD"]
IOVATION_URL = keys["IOVATION"]["URL"]

#FGgame
BRANDID = keys["FG"]["BRANDID"]
BRAND_PASSWORD = keys["FG"]["BRAND_PASSWORD"]
PLATFORM = keys["FG"]["PLATFORM"],
FG_URL = keys["FG"]["FG_URL"]
FG_SESSION_CHECK = keys["FG"]["FG_SESSION_CHECK"]

#MGgame
USERNAME = keys["MG"]["USERNAME"]
PASSWORD = keys["MG"]['PASSWORD']

# LAUNCH_URL = 'https://lsl.omegasys.eu/ps/game/GameContainer.action'

#PTgame
PT_STATUS_SUCCESS = 0
PT_GENERAL_ERROR = 1
PT_BALANCE_ERROR = 2
PT_NEWPLAYER_ALERT = 3
PT_BASE_URL = keys["PT"]["PT_BASE_URL"]
ENTITY_KEY = keys["PT"]["ENTITY_KEY"]




if "prod" in os.getenv("ENV"):  # fetch prod credentials from s3
    API_DOMAIN = "https://payment-testing.claymoreeuro.com/"
    HELP2PAY_SECURITY_THB = keys["HELP2PAY"]["PRODUCTION"]["TH"]
    HELP2PAY_SECURITY_VND = keys["HELP2PAY"]["PRODUCTION"]["VN"]
    HELP2PAY_URL = "https://api.racethewind.net/MerchantTransfer"
    HELP2PAY_MERCHANT_THB = "M0513"
    HELP2PAY_MERCHANT_VND = "M0514"
    HELP2PAY_CONFIRM_PATH = "accounting/api/help2pay/deposit_result"
    HELP2PAY_SUCCESS_PATH = "accounting/api/help2pay/deposit_success"
    EA_KEY = keys["EAGAME"]["PRODUCTION"]["KEY"]
    EA_FTP_ADDR = keys["EAGAME"]["PRODUCTION"]["FTP_ADDR"]
    EA_FTP_USERNAME = keys["EAGAME"]["PRODUCTION"]["FTP_USERNAME"]
    EA_FTP_PASSWORD = keys["EAGAME"]["PRODUCTION"]["FTP_PASSWORD"]
    PAYZOD_API_URL = "https://www.payzod.com/api/qr/"
    PAYZOD_MERCHANT_ID = keys["PAYZOD"]["PRODUCTION"]["MERCHANT_ID"]
    PAYZOD_MERCHANT_NAME = keys["PAYZOD"]["PRODUCTION"]["MERCHANT_NAME"]
    PAYZOD_PASSKEY = keys["PAYZOD"]["PRODUCTION"]["PASSKEY"]
    QT_PASS_KEY = keys["QTGAMES"]["PRODUCTION"]["PASS_KEY"]
    qt = keys["QTGAMES"]["PRODUCTION"]
    H2P_PAYOUT_URL_THB = "https://app.racethewind.net/merchantpayout/M0513"
    H2P_PAYOUT_URL_VND = "https://app.racethewind.net/merchantpayout/M0514"
    ASTROPAY_URL = "https://api.astropaycard.com"
    ASTROPAY_X_LOGIN = keys["ASTROPAY"]["X_LOGIN"]
    ASTROPAY_X_TRANS_KEY = keys["ASTROPAY"]["X_TRANS_KEY"]
    ASTROPAY_SECRET = keys["ASTROPAY"]["SECRET"]
    ASTROPAY_CONFIRM_URL = API_DOMAIN + '/accounting/api/astropay/confirm'
    GDCASINO_MERCHANT_CODE = keys["GD_CASINO"]["PRODUCTION"]["MERCHANT_CODE"]
    GDCASINO_NAMESPACE = keys["GD_CASINO"]["PRODUCTION"]["NAMESPACE"]
elif "dev" in os.getenv("ENV"):
    API_DOMAIN = "https://ibet-django-apdev.claymoreasia.com/"
    HELP2PAY_SECURITY_THB = keys["HELP2PAY"]["SANDBOX"]["TH"]
    HELP2PAY_SECURITY_VND = keys["HELP2PAY"]["SANDBOX"]["VN"]
    HELP2PAY_URL = "http://api.besthappylife.biz/MerchantTransfer"
    HELP2PAY_MERCHANT_THB = "M0513"
    HELP2PAY_MERCHANT_VND = "M0514"
    HELP2PAY_CONFIRM_PATH = "accounting/api/help2pay/deposit_result"
    HELP2PAY_SUCCESS_PATH = "accounting/api/help2pay/deposit_success"
    EA_KEY = keys["EAGAME"]["SANDBOX"]["KEY"]
    EA_FTP_ADDR = keys["EAGAME"]["SANDBOX"]["FTP_ADDR"]
    EA_FTP_USERNAME = keys["EAGAME"]["SANDBOX"]["FTP_USERNAME"]
    EA_FTP_PASSWORD = keys["EAGAME"]["SANDBOX"]["FTP_PASSWORD"]
    PAYZOD_API_URL = "https://dev.payzod.com/api/qr/"
    PAYZOD_MERCHANT_ID = keys["PAYZOD"]["SANDBOX"]["MERCHANT_ID"]
    PAYZOD_MERCHANT_NAME = keys["PAYZOD"]["SANDBOX"]["MERCHANT_NAME"]
    PAYZOD_PASSKEY = keys["PAYZOD"]["SANDBOX"]["PASSKEY"]
    QT_PASS_KEY = keys["QTGAMES"]["SANDBOX"]["PASS_KEY"]
    qt = keys["QTGAMES"]["SANDBOX"]
    H2P_PAYOUT_URL_THB = "http://app.besthappylife.biz/MerchantPayout/M0513"
    H2P_PAYOUT_URL_VND = "http://app.besthappylife.biz/MerchantPayout/M0514"
    ASTROPAY_URL = "https://api.astropaycard.com"
    ASTROPAY_X_LOGIN = keys["ASTROPAY"]["X_LOGIN"]
    ASTROPAY_X_TRANS_KEY = keys["ASTROPAY"]["X_TRANS_KEY"]
    ASTROPAY_SECRET = keys["ASTROPAY"]["SECRET"]
    ASTROPAY_CONFIRM_URL = API_DOMAIN + '/accounting/api/astropay/confirm'
    GDCASINO_MERCHANT_CODE = keys["GD_CASINO"]["STAGING"]["MERCHANT_CODE"]
    GDCASINO_NAMESPACE = keys["GD_CASINO"]["STAGING"]["NAMESPACE"]
else:
    API_DOMAIN = "http://3fb2738f.ngrok.io/"
    HELP2PAY_SECURITY_THB = keys["HELP2PAY"]["SANDBOX"]["TH"]
    HELP2PAY_SECURITY_VND = keys["HELP2PAY"]["SANDBOX"]["VN"]
    HELP2PAY_URL = "http://api.besthappylife.biz/MerchantTransfer"
    HELP2PAY_MERCHANT_THB = "M0513"
    HELP2PAY_MERCHANT_VND = "M0514"
    HELP2PAY_CONFIRM_PATH = "accounting/api/help2pay/deposit_result"
    HELP2PAY_SUCCESS_PATH = "accounting/api/help2pay/deposit_success"
    EA_KEY = keys["EAGAME"]["SANDBOX"]["KEY"]
    EA_FTP_ADDR = keys["EAGAME"]["SANDBOX"]["FTP_ADDR"]
    EA_FTP_USERNAME = keys["EAGAME"]["SANDBOX"]["FTP_USERNAME"]
    EA_FTP_PASSWORD = keys["EAGAME"]["SANDBOX"]["FTP_PASSWORD"]
    PAYZOD_API_URL = "https://dev.payzod.com/api/qr/"
    PAYZOD_MERCHANT_ID = keys["PAYZOD"]["SANDBOX"]["MERCHANT_ID"]
    PAYZOD_MERCHANT_NAME = keys["PAYZOD"]["SANDBOX"]["MERCHANT_NAME"]
    PAYZOD_PASSKEY = keys["PAYZOD"]["SANDBOX"]["PASSKEY"]
    QT_PASS_KEY = keys["QTGAMES"]["SANDBOX"]["PASS_KEY"]
    qt = keys["QTGAMES"]["SANDBOX"]
    H2P_PAYOUT_URL_THB = "http://app.besthappylife.biz/MerchantPayout/M0513"
    H2P_PAYOUT_URL_VND = "http://app.besthappylife.biz/MerchantPayout/M0514"
    ASTROPAY_URL = 'https://sandbox-api.astropaycard.com'  # astroPay sandbox url
    ASTROPAY_X_LOGIN = '1PboDQ2FySeUK8YmaJTkfVlFzy0zTMvQ'
    ASTROPAY_X_TRANS_KEY = 'sQaDolJOA4cvlPoBwLXQjDAEnOO1XCjX'
    ASTROPAY_SECRET = "RJLuSCDcd6mj7SoinVzkH7g2ueJRlScH"
    ASTROPAY_CONFIRM_URL = 'http://3fb2738f.ngrok.io/accounting/api/astropay/confirm'
    GDCASINO_MERCHANT_CODE = keys["GD_CASINO"]["STAGING"]["MERCHANT_CODE"]
    GDCASINO_NAMESPACE = keys["GD_CASINO"]["STAGING"]["NAMESPACE"]

BackURI = "http://3fb2738f.ngrok.io/accounting/api/help2pay/deposit_result"
REDIRECTURL = "http://3fb2738f.ngrok.io/accounting/api/help2pay/deposit_success"

HELP2PAY_RETURN_URL = "http://ibet-django-apdev.claymoreasia.com/accounting/api/help2pay/withdraw_result"

GAME_FILTER_OPTION = [
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


GAME_FILTER_OPTIONS = {
    'Providers': [],
    'Features': ['Megaways', 'Pay Both Ways', 'Bonus Feature', 'Free Spins', 'Double Or Nothing Feature'],
    'Theme': ['Egypt', 'Oriental', 'Mythology', 'Animal', 'Adventure', 'Fruit', 'Western', 'Film/Tv', 'Music', 'Sports',
            'Space', 'Holidays', 'Dark/ Halloween', 'Vegas'],
    'Jackpot': ['Daily Jackpots', 'Fixed Jackpots', 'Progressive Jackpot', 'Multiple Jackpots'],
    'Sort': ['Name', 'Popularity', 'Jackpot Size Asc', 'Jackpot Size Desc']
}

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

AWS_SES_REGION = 'us-west-2'
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

LETOU_DOMAIN = "https://www.letou.com/cn/a/"   # for affiliate refer link

MONTHLY_COMMISSION_SETTLE_DATE = "05"


BONUS_QUEUE_NAME = "bonus_queue"
BONUS_QUEUE_CL_NAME = "bonus_queue_cl"

PUBLIC_S3_BUCKET = "https://ibet-web.s3-us-west-1.amazonaws.com/"

# Error code define
CODE_SUCCESS = 1
ERROR_CODE_BLOCK = 100
ERROR_CODE_INVALID_INFO = 101
ERROR_CODE_INACTIVE = 102
ERROR_CODE_NOT_FOUND = 103
ERROR_CODE_MAX_EXCEED = 104
ERROR_CODE_EMPTY_RESULT = 105
ERROR_CODE_TIME_EXCEED = 106

ERROR_CODE_DATABASE = 106
ERROR_CODE_FAIL = 107
ERROR_CODE_DUPE = 108

BONUS_TYPE_VERIFICATION = 0
BONUS_TYPE_DEPOSIT = 1
BONUS_TYPE_TURNOVER = 2
BONUS_TYPE_STANDARD = 3
BONUS_TYPE_FREESPINS = 4
BONUS_TYPE_MANUAL = 5

BONUS_TYPE_CHOICES = (
    (BONUS_TYPE_VERIFICATION, 'VERIFICATION'),
    (BONUS_TYPE_DEPOSIT, 'DEPOSIT'),
    (BONUS_TYPE_TURNOVER, 'TURNOVER'),
    (BONUS_TYPE_STANDARD, 'STANDARD'),
    (BONUS_TYPE_FREESPINS, 'FREE SPINS'),
    (BONUS_TYPE_MANUAL, 'MANUAL')
)

BONUS_STATUS_CHOICES = (
    (0, 'INACTIVE'),
    (1, 'ACTIVE'),
    (2, 'DISABLED'),
)


BONUS_START = 0
BONUS_ACTIVE = 1
BONUS_COMPLETED = 2
BONUS_EXPIRED = 3
BONUS_ISSUED = 4
BONUS_REDEEMED = 5

USER_BONUS_EVENT_TYPE_CHOICES = (
    (0, 'STARTED'),
    (1, 'ACTIVE'),
    (2, 'COMPLETED'),
    (3, 'EXPIRED'),
    (4, 'ISSUED'),
    (5, 'REDEEMED'),
)

BONUS_RELEASE_TYPE_CHOICES = (
    (0, 'Pre-wager'),
    (1, 'Post-wager'),
)

BONUS_AGGREGATE_SUM = 0
BONUS_AGGREGATE_COUNT = 1
BONUS_AGGREGATE_AVERAGE = 2
BONUS_AGGREGATE_MAX = 3
BONUS_AGGREGATE_LATEST = 4

BONUS_AGGREGATE_METHOD_CHOICES = (
    (0, 'SUM'),
    (1, 'COUNT'),
    (2, 'AVERAGE'),
    (3, 'MAX'),
    (4, 'LATEST'),
)

#GD CASINO

GDCASINO_URL = keys["GD_CASINO"]["URL"]
GDCASINO_API_URL = keys["GD_CASINO"]["API_URL"]
GDCASINO_MERCHANT_ACCESS_KEY = keys["GD_CASINO"]["MERCHANT_ACCESS_KEY"]
GDCASINO_FISHING_GAMEID = keys["GD_CASINO"]["FISHING_GAMEID"]

GDCASINO_STATUS_CODE =(
    (-1, 'UNKNOWN_ERROR'),
    (0, 'OK'),
    (1,'INVAILD_PARAMETER'),
    (2, 'INVAILD_TOKEN_ID'),
    (3, 'BET_ALREDY_SETTLED'),
    (4, 'BET_DOES_NOT_EXIST'),
    (5, 'BET_ALREADY_EXIST'),
    (6, 'ACCOUNT_LOCKED'),
    (7, 'INSUFFUCIENT_FUNDS'),
    (8, 'RETRY_TRANSACTION'),
    (201, 'INSUFFUCIENT_FUNDS_1(for maxbet)'),
    (202, 'ACCOUNT_LOCKED_1(for maxbet)'),
    (206, 'ABOVE_PLAYER_LIMIT_1(for maxbet)')
)

GDCASINO_STATUS = (
    (0, 'PENDING'),
    (1, 'DEBIT'),
    (2, 'CREDIT'), 
    (3, 'TIP'),
    (4, 'CANCEL'),
)
GDCASINO_GAME_TYPE = (
    (0, 'None'),
    (6, 'Baccarat'),
    (28, 'Roulette'),
    (29, 'Sic bo'),
    (100, 'Slot game'),
)


GDCASINO_CANCEL_REASON = (
    ('NONE', 'None'),
    ('CANCELLED_ROUND', 'Game round is cancelled.'),
    ('DEBIT_TIME_OUT', 'Debit response timeout.'),
    ('VOIDED_BET', 'Abnormal bet is voided.'),
    ('BETTING_TIME_FINISHED', 'Betting time is ended'),
    ('INVALID_DEBIT_REPLY', 'Debit reply is in wrong format.'),
)


BRAND_OPTIONS = (
    ('letou', 'Letou'),
    ('ibet', 'iBet')
)


SECURITY_QUESTION = (
    (0, _('What is your’s father birthday?')),
    (1, _('What is your’s mother birthday?')),
    (2, _('What is your’s spouse birthday?')),
    (3, _('What is your first company’s employee ID?')),
    (4, _('What is your primary school class teacher’s name?')),
    (5, _('What is your best childhood friend’s name?')),
    (6, _('What is the name of the person that influenced you the most?'))
    
)

# Bonus
BONUS_MANUAL = 0
BONUS_TRIGGERED = 1
BONUS_CATEGORY = (
    (0, 'Manual'),
    (1, 'Triggered'),
)

BONUS_MUST_HAVE = (
    (0, 'ID verified'),
    (1, 'Phone verified'),
    (2, 'Email verified'),
    (3, 'A successful deposit'),
    (4, 'A successful withdrawal'),
    (5, 'Manual audit for first withdrawal'),
)

BONUS_DELIVERY_PUSH = 0
BONUS_DELIVERY_SITE = 1
DELIVERY_CHOICES = (
    (0, 'Push'),
    (1, 'Site activation'),
)

BONUS_PAYOUT_INSTANT = 0
BONUS_PAYOUT_WEEKLY = 1
BONUS_PAYOUT_MANUAL = 2
BONUS_PAYOUT_NONE = 3

BONUS_PAYOUT_CHOICES = (
    (BONUS_PAYOUT_INSTANT, 'Instant'),
    (BONUS_PAYOUT_WEEKLY, 'Weekly'),
    (BONUS_PAYOUT_MANUAL, 'Manual'),
    (BONUS_PAYOUT_NONE, 'None')
)

# Games
# All provider
KY_PROVIDER = "KY"
BETSOFT_PROVIDER = "Betsoft"
EA_PROVIDER = "EA"
AG_PROVIDER = "AG"
FG_PROVIDER = "FG"
MG_PROVIDER = "MG"
ONEBOOK_PROVIDER = "Onebook"
GB_PROVIDER = "GB"
GD_PROVIDER = "GD"
N2_PROVIDER = "N2"
BTI_PROVIDER = "BTi"
PLAYNGO_PROVIDER = "PLAYNGO"
IMES_PROVIDER = "IMES"
QTECH_PROVIDER = "QTech"
ALLBET_PROVIDER = "ALLBET"

# Taiwan team
GPT_PROVIDER = "GPT"
OPUS_PROVIDER = "OPUS"
BBIN_PROVIDER = "BBIN"
PT_PROVIDER = "PT"



# Playngo
PNG_STATUS_OK = 0
PNG_STATUS_NOUSER = 1
PNG_STATUS_INTERNAL = 2
PNG_STATUS_INVALIDCURRENCY = 3
PNG_STATUS_WRONGUSERNAMEPASSWORD = 4
PNG_STATUS_ACCOUNTLOCKED = 5
PNG_STATUS_ACCOUNTDISABLED = 6
PNG_STATUS_NOTENOUGHMONEY = 7
PNG_STATUS_MAXCONCURRENTCALLS = 8
PNG_STATUS_SPENDINGBUDGETEXCEEDED = 9
PNG_STATUS_SESSIONEXPIRED = 10
PNG_STATUS_TIMEBUDGETEXCEEDED = 11
PNG_STATUS_SERVICEUNAVAILABLE = 12

PNG_ACCESS_TOKEN = keys["PLAYNGO"]["ACCESSTOKEN"]

# Inplay Matrix
IMES_URL = keys["IMES"]["URL"]
IMES_KEY = keys["IMES"]["DESKEY"]

# Kaiyuan Gaming
KY_AGENT = "71452"
KY_LINE_CODE_1 = "iBet01"
KY_API_URL = "https://kyapi.ky206.com:189/channelHandle"
KY_RECORD_URL = "https://kyapi.ky206.com:190/getRecordHandle"

# AllBet
ALLBET_PROP_ID = keys["ALLBET"]["PROPERTYID"]
ALLBET_SHA1_KEY = keys["ALLBET"]["SHA1KEY"]

#onebook
# ONEBOOK_PROVIDER = keys["ONEBOOK"]["PROVIDER"]
ONEBOOK_VENDORID = keys["ONEBOOK"]["VENDORID"]
ONEBOOK_OPERATORID = keys["ONEBOOK"]["OPERATORID"]
ONEBOOK_MAXTRANSFER = keys["ONEBOOK"]["MAXTRANSFER"]
ONEBOOK_MINTRANSFER = keys["ONEBOOK"]["MINTRANSFER"]
ONEBOOK_API_URL = keys["ONEBOOK"]["API_URL"]
ONEBOOK_DIRECTION_withdraw = keys["ONEBOOK"]["DIRECTION_withdraw"]
ONEBOOK_DIRECTION_deposit = keys["ONEBOOK"]["DIRECTION_deposit"]
ONEBOOK_IFRAME_URL = keys["ONEBOOK"]["IFRAME_URL"]
# AllBet
AB_URL = "https://platform-api.apidemo.net:8443/"

# SA
SA_SECRET_KEY = 'F0E5C6E337F84A13960D57B06C4E361F'
SA_ENCRYPT_KEY = 'g9G16nTs'
SA_MD5KEY = 'GgaIMaiNNtg'
SA_API_URL = 'http://sai-api.sa-apisvr.com/api/api.aspx'

#GB
# GB_PROVIDER = keys["GB"]["PROVIDER"]
GB_URL = keys["GB"]["URL"]
GB_API_URL = keys["GB"]["API_URL"]
GB_SPORT_URL = keys["GB"]["SPORT_URL"]
GB_OTHER_URL = keys["GB"]["OTHER_URL"]

# QT
QT_STATUS_SUCCESS = 0
QT_STATUS_UNKNOWN_ERROR = 1
QT_STATUS_INVALID_TOKEN = 2
QT_STATUS_LOGIN_FAILED = 3
QT_STATUS_ACCOUNT_BLOCKED = 4
QT_STATUS_REQUEST_DECLINED = 5

QT_STATUS_CODE = (
    (0, "SUCCESS"),
    (1, "UNKNOWN_ERROR"),
    (2, "INVALID_TOKEN"),
    (3, "LOGIN_FAILED"),
    (4, "ACCOUNT_BLOCKED"),
    (5, "REQUEST_DECLINED"),
)

# Betsoft
BETSOFT_KEY = keys["BETSOFT"]["KEY"]

#AG
AG_URL = "https://gi.claymoreasia.com/doBusiness.do"
AG_FORWARD_URL = "https://gci.claymoreasia.com/forwardGame.do"
AG_CAGENT = "EV3_AGIN"
AG_MD5 = "2YgQUaUZfDDt"
AG_DES = "MJp7ScbZ"
AG_DM = "http://ibet.com"
#IMES
IMES_PROVIDER = "IMES"
