# Typical Linux configuration
PYBOT_CMD = "/usr/local/bin/pybot"
REBOT_CMD = "/usr/local/bin/rebot"

# Typical Windows configuration
# PYBOT_CMD = "c:\\Python27\\Scripts\\pybot.bat"
# REBOT_CMD = "c:\\Python27\\Scripts\\rebot.bat"

# Typical Mac configuration
# PYBOT_CMD = "/Library/Frameworks/Python.framework/Versions/2.7/bin/pybot"
# REBOT_CMD = "/Library/Frameworks/Python.framework/Versions/2.7/bin/rebot"


# Other cross platform configuration items
TEST_REGEXP = '.*\.(txt|robot)'
MAX_PARALLEL_TESTS = 5
MAX_EXECUTION_TIME = 6000
FAILED_RERUNS = 2
ADVERTISE_TIME = 10
REPORT_NAME = "Regression"
REPORT_FILENAME = "output.xml"
BEFORE_RUN = ''
AFTER_RUN = ''


