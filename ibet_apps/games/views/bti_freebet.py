import requests
from utils.constants import *


###########################################################################################
# begin FREEBET API calls
###########################################################################################
def createChannel():
    header = {'RequestTarget': 'AJAXService'}
    payload = {
        "agentUserName": BTI_AGENT_USERNAME,
        "agentPassword": BTI_AGENT_PW
    }
    r = requests.post(BTI_FREEBET_URL + "/channelservice/createchannel", headers=header, json=payload)
    if r.status_code == 200:
        resp = r.json()
        session_id = resp[0]["Value"]["Value"]
        return session_id
    return None

def closeChannel(session_id):
    header = {'RequestTarget': 'AJAXService'}
    r = requests.post(BTI_FREEBET_URL + "/channelservice/closechannel/ch=" + session_id, headers=header)
    if r.status_code == 200:
        return True
    return False

# provider says this API is not working right now
def addSegment(session_id, segment_name):
    header = {'RequestTarget': 'AJAXService'}
    payload = {
        'sessionID': session_id,
        'SegmentName': segment_name
    }
    r = requests.post(BTI_FREEBET_URL + "/data/addsegment/ch=" + session_id, headers=header, json=payload)

    if r.status_code == 200 and r.json()[0]["Value"]["Value"].lower() == "ok":
        return True
    return False
# provider says this API is not working right now
def addCustomersToSegment(session_id, segment_name):
    header = {'RequestTarget': 'AJAXService'}
    payload = {
        'sessionID': session_id,
        'SegmentName': segment_name,

    }
    r = requests.post(BTI_FREEBET_URL + "/data/addsegment/ch=" + session_id, headers=header, json=payload)
    
    if r.status_code == 200 and r.json()[-1]["Value"]["Value"].lower() == "ok":
        return True
    return False

# give freeebet to user
def giveFreeBet(session_id, user_object, amount, coupon_code):
    path = f"/data/givefreebettocustomer/ch={session_id}"
    header = {'RequestTarget': 'AJAXService', 'content-type': 'application/json'}
    payload = '\"{\\"MerchantCode\\":\\"' + user_object.username + '\\",\\"Amount\\":' + str(amount) + ',\\"CouponCode\\":\\"' + coupon_code + '\\"}\"'

    r = requests.post(BTI_FREEBET_URL + path, headers=header, data=payload)

    if r.status_code == 200 and r.json()[0]["Value"]["Value"].lower() == "ok":
        return True
    return False

def getFreeBets(session_id, userid):
    path = f"/data/getfreebetsforcustomer/ch={session_id}"
    header = {'RequestTarget': 'AJAXService'}
    payload = {"MerchantCodes": userid}
    r = requests.post(BTI_FREEBET_URL + path, headers=header, json=payload)

    if r.status_code == 200 and r.json()[0]["Value"]["Value"].lower() == "ok":
        return True
    return False
