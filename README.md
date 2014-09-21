Introduction
============

This is a parallel launcher for [Pybot](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#different-entry-points)
(see the [Robot Framework](https://github.com/robotframework/robotframework))  that basically allows you to launch several pybot instances at the same time, saving a lot of time on your CI system.

We at [Workshare](https://www.workshare.com) we use in our continuous integration system to parallelize the run of pybot tests so that they take less time to execute. Currently our 1k+ integration test sweet for [Workshare Connect](http://www.workshare.com/products/connect) runs in a couple of hours on our windows machine (of course on Linux it take less then half but hey, we have to validate our stuff with Windows and IE9). Sweet!

The way it works it's really simple: having you installed successfully the [Robot Framework](https://github.com/robotframework/robotframework)) then if you run [ppybot.py ](https://github.com/workshare/parallel_pybot/blob/master/ppybot.py) against any folder containing tests, it will execute such tests in parallel with [Pybot](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#different-entry-points) using the requested configuration (command line or file), aggregating then the results at the end with [Rebot](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#different-entry-points). You can specify the number of retries, the number of parallel bots you want, the timeout for each test... all should work pretty much as you expect it. You can also specify a test that runs before and after the whole parallel running, for global setup and cleanup operation.

When running it also generates [xunit compatible](http://reflex.gforge.inria.fr/xunit.html#xunitReport) output files (named _testname_.xunit.xml) that can be digested easily from your CI (in our case we use the standard [Jenkins](http://jenkins-ci.org/) reporting mechanism).


Example
=======
When you checkout the project you will also get my super naive example that basically does nothing :) To run it just execute the command:
```
python ppybot.py . 
```
Two tests will be run in parallel... wowee! Now you can basically try it against any folder containing tests you have, and see the magic happens!


Configuration
=============

It comes with a configuration file that allows you to fix the most common options and most of it is changeable trough the command line:
* "--timeout"  maximum time in seconds spent in executing one test before aborting 
* "--reruns",  maximum number of reruns executed on failed tests 
* "--parallels" maximum number of parallel test running at the same time
* "--logs"  folder where logs are generated, must exist!
* "--advertise"  the seconds to elapse before advertising the current status
* "--pybot" the command to execute to invoke [Pybot](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#different-entry-points) i.e. /usr/local/bin/pybot
* "--rebot" the command to execute to invoke [Rebot](http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#different-entry-points) i.e. /usr/local/bin/rebot
* "--failed-only"  runs only the failed tests
* "--verbose"  verbose mode, more details about wassup
* "--no-fixtures"  no fixture code will be run before / after executions

The are few thing tough only configurable trough the [configuration file](https://github.com/workshare/parallel_pybot/blob/master/ppybot_config.py):
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


Dependencies
============
The tool requires the [xunitparser library](https://pypi.python.org/pypi/xunitparser), you can install it via pip
```
sudo pip install xunitparser 
```
Or follow the instructions at the link :)


What else?
==========
Any question please open an issue, we will be happy to answer you! Any change feel free to go for a pull request, and you can of course clone the project but we will appreciate your contributions back :) 

__Disclaimer__: please note that I am _not_ a Python developer, so if the code looks naive it's just because I am not procifient enough. Python is actually a beautiful language, but I do not have time to study it properly at the moment, so I did the best that I could in the (very short) time I had.
