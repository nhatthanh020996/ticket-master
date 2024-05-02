from datetime import datetime
import pytz


def gen_local_datetime():
    return datetime.now(tz=pytz.timezone('Asia/Ho_Chi_Minh'))