parallel_pybot
==============

This is a parallel launcher for Pybot (see the [Robot Framework](https://github.com/robotframework/robotframework))  that basically allows you to launch several pybot instances at the same time, saving a lot of time on your CI system.

We at [Workshare](https://www.workshare.com) we use in our continuous integration system to parallelize the run of pybot tests so that they take less time to execute. Sweet!

It comes with a configuration file that allows you to fix the most common options and most of it is changeable trough the command line:
* "--timeout"  maximum time in seconds spent in executing one test before aborting 
* "--reruns",  maximum number of reruns executed on failed tests 
* "--parallels" maximum number of parallel test running at the same time
* "--logs"  folder where logs are generated, must exist!
* "--advertise"  the seconds to elapse before advertising the current status
* "--pybot" the command to execute to invoke pybot i.e. /usr/local/bin/pybot
* "--rebot" the command to execute to invoke pybot i.e. /usr/local/bin/rebot
* "--failed-only"  runs only the failed tests
* "--verbose"  verbose mode, more details about wassup
* "--no-fixtures"  no fixture code will be run before / after executions

The are few thing tough only configurable trough the configuration file:
- TEST_REGEXP  the regular expression used to identify tests in the folder, i.e. '.*\.txt' (all .txt files)
- BEFORE_RUN   a "fixture" test to be executed alone BEFORE the parallel tests starts (tipically used for environment setup)
- AFTER_RUN    a "fixture" test to be executed alone AFTER all the parallel tests finished (tipically used for cleanup)
- REPORT_NAME  the name of the rebot report
- REPORT_FILENAME  the filename of the rebot report

while othere can be specified as default in the configuration file:
* MAX_EXECUTION_TIME -> "--timeout"
* FAILED_RERUNS -> "--reruns"
* MAX_PARALLEL_TESTS -> "--parallels"
* ADVERTISE_TIME -> "--advertise"
* PYBOT_CMD -> "--pybot"
* REBOT_CMD -> "--rebot"
