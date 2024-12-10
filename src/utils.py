from datetime import datetime, timedelta

def get_default_period_end():
    today = datetime.today()
    if today.weekday() >= 5:  # If today is Saturday (5) or Sunday (6)
        offset = today.weekday() - 4  # Move back to Friday
        return today - timedelta(days=offset)
    return today

def get_default_period_init(period_end):
    return period_end - timedelta(days=365)

if __name__ == "__main__":
    print(get_default_period_end())
    print(get_default_period_init(get_default_period_end()))
