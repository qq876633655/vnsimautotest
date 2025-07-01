import os
import shutil
import datetime
date_now = datetime.datetime.now()
date_year = date_now.year
date_month = date_now.month
date_day = date_now.day
date_hour = date_now.hour
date_minute = date_now.minute
date_second = date_now.second
error_log_time = f"{str(date_year)}_{str(date_month)}_{str(date_day)}_{str(date_hour)}_{str(date_minute)}_{str(date_second)}"


log_for_old = "/home/visionnav/log/3DSLAM"
log_for_new = f"/home/visionnav/log/自动化异常日志/{error_log_time}/3DSLAM"
log_for_old_general = "/home/visionnav/log/general"
log_for_new_general = f"/home/visionnav/log/自动化异常日志/{error_log_time}/general"
shutil.copytree(log_for_old,log_for_new)
shutil.copytree(log_for_old_general,log_for_new_general)

