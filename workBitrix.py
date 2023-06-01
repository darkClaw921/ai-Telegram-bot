from fast_bitrix24  import Bitrix
from dotenv import load_dotenv
import os
load_dotenv()
bit = Bitrix(os.environ.get('WEB_HOOK'))

def create_deal(items:dict):
    dealID = bit.call('crm.deal.add', items=items)
    return dealID

def create_contact():
    pass

