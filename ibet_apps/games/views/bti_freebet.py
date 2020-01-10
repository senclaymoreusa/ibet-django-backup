import requests
from utils.constants import *


###########################################################################################
# begin FREEBET API calls
###########################################################################################
def CreateChannel():
    BTI_FREEBET_URL = "https://bonus-api.bti360.io/"
    BTI_AGENT_USERNAME = "WKIBPH"
    BTI_AGENT_PW = "Tr6saneyu"
    username = BTI_AGENT_USERNAME
    password = BTI_AGENT_PW
    header = {'RequestTarget': 'AJAXService'}
    payload = {
        "agentUserName": username,
        "agentPassword": password
    }
    r = requests.post(BTI_FREEBET_URL + "/channelservice/createchannel", headers=header, json=payload)
    if r.status_code == 200:
        resp = r.json()
        session_id = resp[0]["Value"]["Value"]
        return session_id
    return None

def CloseChannel(session_id):
    header = {'RequestTarget': 'AJAXService'}
    r = requests.post(BTI_FREEBET_URL + "/channelservice/closechannel/ch=" + session_id, headers=header)
    if r.status_code == 200:
        return True
    return False

# provider says this API is not working right now
def AddSegment(session_id, segment_name):
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
def AddCustomersToSegment(session_id, segment_name):
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
def GiveFreeBet(session_id, user_object, amount):
    BTI_FREEBET_URL = "https://bonus-api.bti360.io/"
    path = f"/data/givefreebettocustomer/ch={session_id}"
    header = {'RequestTarget': 'AJAXService', 'content-type': 'application/json'}
    payload = '\"{\\"MerchantCode\\":\\"btiTest123\\",\\"Amount\\":' + str(amount) + ',\\"CouponCode\\":\\"WKxCqA\\"}\"'
    print(payload)
    # payload = '{"MerchantCode": "' + user_object.username + '","Amount": ' + amount + ',"CouponCode": "Sg6z2o" }'
    r = requests.post(BTI_FREEBET_URL + path, headers=header, data=payload)
    print(r.json())
    if r.status_code == 200 and r.json()[0]["Value"]["Value"].lower() == "ok":
        return True
    return False

def GetFreeBets(session_id, userid):
    path = f"/data/getfreebetsforcustomer/ch={session_id}"
    header = {'RequestTarget': 'AJAXService'}
    payload = {"MerchantCodes": userid}
    r = requests.post(BTI_FREEBET_URL + path, headers=header, json=payload)

    if r.status_code == 200 and r.json()[0]["Value"]["Value"].lower() == "ok":
        return True
    return False
