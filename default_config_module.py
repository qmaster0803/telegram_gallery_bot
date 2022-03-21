bot_token      = "<-- FILL -->"
main_db_path   = "Library/bot_database.db"
library_path   = "Library/"
downloads_path = "tmp/"
server_url     = "http://localhost:4200/bot{0}/{1}"

#interval from <start_time> to <end_time> is hours in 24-hour format
#if you want to enable processing in all-day mode, set rotation_check_allday=1
#interval for checking photos rotation
rotation_check_allday = 1
rotation_check_start  = 2
rotation_check_stop   = 6