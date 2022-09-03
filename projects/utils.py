from datetime import datetime

def get_html_date():
    today = datetime.today()
    return today.strftime('%Y-%m-%d')