from datetime import datetime

def get_html_date():
    today = datetime.today()
    return today.strftime('%Y-%m-%d')

def build_field_error(field:str, message:str):
    object = {}
    object[field] = [message]
    return object