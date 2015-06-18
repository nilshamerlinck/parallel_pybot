import sys
import os
import time
import subprocess
import ppybot_config as config
import re
import xunitparser


from os import listdir
from os.path import isfile, join

from optparse import OptionParser




# encapsulate a running pybot process
class Pybot():

    pid = None
    process = None
    started = False
    
    ini_time = None
    end_time = None
    
    outFile = None
    logFile = None
    xunitFile = None
    
    test_result = None
    test_suite = None
    
    attempt = 0
    
    def __init__(self, folder, filename, options):
        self.folder = folder
        self.name = filename[0:len(filename)-len(".txt")]
        self.options = options

        self.outFile = "%s.out.xml" % os.path.join(options.logs_folder, self.name)
        self.logFile = "%s.log" % os.path.join(options.logs_folder, self.name)                               
        self.xunitFile = "%s.xunit.xml" % os.path.join(options.logs_folder, self.name)                               
                                       
    def __del__(self):
        self._on_finish()
            
    def __str__(self):
        if self.pid == None:
            return "pybot %s" % (self.name)
        else:
            return "pybot %s (pid: %d)" % (self.name, self.pid)

    def _init(self):
        self.end_time = None
        self.test_result = None
        self.test_suite = None

        
    def start(self, runfailed=False):

        self._init()

        commands = []
        commands.append(self.options.pybot_cmd)
        commands.append("-x")
        commands.append(self.xunitFile)
        commands.append("-l")
        commands.append("NONE")
        commands.append("-r")
        commands.append("NONE")
        if runfailed == True:
            commands.append("--runfailed")
            commands.append(self.outFile)
            self.outFileRunfailed  = "%s.rerun.%d.xml" % (os.path.join(self.options.logs_folder, self.name), self.attempt)
            commands.append("-o")
            commands.append(self.outFileRunfailed)
        else:
            commands.append("-o")
            commands.append(self.outFile)
            
        update_options(commands, self.options.pybot_opts)
        commands.append(self.name + ".txt")

        self.log = open(self.logFile, "w")
        self.process = subprocess.Popen(commands, cwd=self.folder, stdout=self.log, stderr=self.log)
        self.pid = self.process.pid
        if self.options.verbose: print str(self)+" started!"
        self.started = True
        self.ini_time = time.time()
        
    def elapsed(self):
        if self.end_time == None:
            if self.ini_time == None:
                return 0
            else:
                return time.time() - self.ini_time
        else:
            return self.end_time - self.ini_time
        
    def wait(self, timeout):
        self.process.wait()
        self._on_finish();

    def isRunning(self):
        running = self.process != None and self.process.poll() == None
        if not running:
            if self.options.verbose: print str(self)+" finished!"
            self._on_finish();
        return running
    
    def isDone(self):
        return self.started == True and (not self.isRunning())
    
    def kill(self):
        if self.isRunning():
            self.process.kill()
            self.process.terminate()
            self.process.wait()
            self.process = None

        self._on_finish()
        print "%s was killed after %d elapsed seconds" % (str(self), self.elapsed())

    def _on_finish(self):
        try: 
            self._on_finish_unsafe()
        except:
            None

    def _on_finish_unsafe(self):
        if hasattr(self, 'log') and self.log != None:
            self.log.close()
            self.log=None

        if self.end_time == None:
            self.end_time = time.time()

        self.pid = None
        self.attempt = self.attempt + 1

        self.load_xunit_results()

    def load_xunit_results(self):
        if self.xunitFile != None and os.path.isfile(self.xunitFile):
            if xunitparser != None:
                with open(self.xunitFile, 'r') as xunit:
                    self.test_suite, self.test_result = xunitparser.parse(xunit)
                    
    def was_successful(self):
        if self.test_result == None:
            return False
        else:
            return len(self.test_result.errors) == 0 and len(self.test_result.failures) == 0

    def output_file(self):
        return self.outFile

    def attempts(self):
        return self.attempt
 
   
#
# support functions
#

def update_options(commands, optstring):
  if optstring != None:
    opts = optstring.split()
    for opt in opts:
      commands.append(opt)


def isWindows():
    return sys.platform.startswith("win")
        
def run_bots(title, options, folder, bot_before, bot_after, bots, run_failed=False):
    
    torun_bots = remove_successful_bots(bots)
    if len(torun_bots) == 0:
        return
            
    print "\n\n================================================================================="
    print "Starting bots! Session: "+title
    print 
    print "- source folder: "+folder
    print "- results folder: "+options.logs_folder
    print "- max parallel pybots (processes): "+str(options.max_parallel_tests)
    print "- max time allowed (seconds): "+str(options.max_execution_time)
    print "\n=================================================================================\n"
    
    if (bot_before != None):
        print "Running BEFORE fixture..."
        bot_before.start()
        bot_before.wait(60)
        print "Done!\n"
    
    last_dump=time.time()
    done_bots = []
    all_bots = torun_bots[:]
    running_bots = []
    while len(all_bots) > 0 or len(running_bots) > 0:
        
        time.sleep(1)
        
        for bot in running_bots:
            if bot.isDone():
                running_bots.remove(bot)
                done_bots.append(bot)
            if bot.elapsed() > options.max_execution_time:
                running_bots.remove(bot)
                bot.kill();
    
        if len(running_bots) == options.max_parallel_tests:
            continue
         
        if len(all_bots) > 0:
            bot = all_bots[0];
            all_bots.remove(bot)
            running_bots.append(bot)
            bot.start(run_failed)
    
        if time.time() > last_dump + options.advertise_time:
            last_dump = time.time()
            dump_bots(running_bots, all_bots, done_bots)
    
    dump_bots(running_bots, all_bots, done_bots)

    if (bot_after != None):
        print "Running AFTER fixture..."
        bot_after.start()
        bot_after.wait(60)
        print "Done!\n"
    
    return done_bots

def remove_successful_bots(bots):
    torun_bots = []
    for bot in bots:
        if not bot.was_successful():
            torun_bots.append(bot)
            
    return torun_bots

def get_bot_results(bot):
    tc = bot.test_result
    if tc ==  None:
        return "not executed"
    else:
        return "%2.2d/%2.2d" % (tc.testsRun-len(tc.errors)-len(tc.failures), tc.testsRun)
    
def dump_bots(running_bots, queued_bots, done_bots):
    print "\n-------------------------------------------------"
    
    if len(running_bots) > 0:
        print "Running tests:"
        for bot in running_bots:
            print "- %s since %d seconds ago" % (str(bot), bot.elapsed())

    if len(queued_bots) > 0:
        print "Queued tests:"
        for bot in queued_bots:
            print "- %s " % (str(bot))

    if len(done_bots) > 0:
        print "Done tests: (success/total)"
        for bot in done_bots:
            result = "" if bot.was_successful() else "FAILED"
            print "- %s %s (elapsed: %d seconds) %s" % (get_bot_results(bot), str(bot), bot.elapsed(), result)

    print "-------------------------------------------------\n"

def parse_args():

    usage = "usage: %prog [options] folder_with_tests"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--timeout", dest="max_execution_time", type="int", default=config.MAX_EXECUTION_TIME,
                      help="maximum time in seconds spent in executing one test before aborting", metavar="SECONDS")
    parser.add_option("-r", "--reruns", dest="max_attempts", type="int", default=config.FAILED_RERUNS,
                      help="maximum number of reruns executed on failed tests", metavar="NUM")
    parser.add_option("-p", "--parallels", dest="max_parallel_tests", type="int", default=config.MAX_PARALLEL_TESTS,
                      help="maximum number of parallel test running at the same time", metavar="NUM")
    parser.add_option("-l", "--logs", dest="logs_folder", default=".",
                      help="folder where logs are generated, must exist", metavar="FOLDER")
    parser.add_option("-a", "--advertise", dest="advertise_time", default=config.ADVERTISE_TIME, type="int",
                      help="the seconds to elapse before advertising the current status", metavar="SECONDS")
    parser.add_option("--pybot", dest="pybot_cmd", default=config.PYBOT_CMD,
                      help="the command to execute to invoke pybot i.e. /usr/local/bin/pybot", metavar="PATH")
    parser.add_option("--rebot", dest="rebot_cmd", default=config.REBOT_CMD,
                      help="the command to execute to invoke pybot i.e. /usr/local/bin/rebot", metavar="PATH")
    parser.add_option("-f", "--failed-only", action="store_true", dest="failed_only", default=False, help="runs only the failed tests")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="verbose mode, more details about wassup")
    parser.add_option("-x", "--no-fixtures", action="store_true", dest="no_fixtures", default=False, help="no fixture code will be run before / after executions")
    parser.add_option("-s", "--select-from", dest="tests_file", type="string", help="select the files that will be run from a file")
    parser.add_option("--pybot-opts", dest="pybot_opts", default=None, help="additional commands to send to pybot")
    parser.add_option("--rebot-opts", dest="rebot_opts", default=None, help="additional commands to send to rebot")

    return parser.parse_args()
  
  
def makeFixtureBot(folder, filename, options):
    if isfile(join(folder,filename)):
        return Pybot(folder, filename, options)
    else:
        return None

def runtime_okay(options):
    return is_executable(options.pybot_cmd) and is_executable(options.rebot_cmd)

def is_executable(runtime):
    try:
        commands = []
        commands.append(runtime)
        commands.append("--version")
        process = subprocess.Popen(commands)
        process.wait()
        return True
    except:
        print "Cannot execute "+runtime+" - please check your configuration / parameters"
        return False


def get_test_files(folder, options):
    if options.tests_file != None:
        tests = [line.rstrip('\n') for line in open(options.tests_file)]
    elif config.TEST_REGEXP != None:
        tests = [f for f in listdir(folder) if isfile(join(folder, f)) and re.match(config.TEST_REGEXP, f)]
    else:
        tests = []
        
    return tests

#
# Main execution script
#

def main():

    (options, args) =  parse_args()
    
    if len(args) == 0:
        print "A destination folder must be specified!"
        os.abort()
        
    if runtime_okay(options) == False:
        print "The runtime is not correctly configured - I cannot run :("
        os.abort()
    else:
        if options.verbose: print "Runtime succesfully verified \n"

        
    folder = args[0]
    if options.logs_folder == ".":
        options.logs_folder = folder
        
    tests = get_test_files(folder, options)
    if len(tests) == 0:
        print "No tests found or selected"
        os.abort()
    
    all_bots = []
    if options.verbose: print "Tests found:"
    for test in tests:
        all_bots.append(Pybot(folder, test, options))
        if options.verbose: print "- "+test;
    
    if options.no_fixtures == False:
        bot_before = makeFixtureBot(folder,config.BEFORE_RUN, options)
        bot_after  = makeFixtureBot(folder,config.AFTER_RUN, options)
    else:
        bot_before = None
        bot_after  = None
        
    start_time = time.time()
    if options.failed_only == False:
        run_bots("main", options, folder, bot_before, bot_after, all_bots, False)
    else:
        for bot in all_bots:
            bot.load_xunit_results()
        all_bots = remove_successful_bots(all_bots)
    
    for i in range (1, 1+options.max_attempts):
        run_bots("failed #"+str(i), options, folder, bot_before, bot_after, all_bots, True)
    
    print "\n\n================================================================================="
    print "TEST FINISHED (elapsed: %d seconds)"  % (time.time() - start_time)
    print 
    for bot in all_bots:
        result = " ok " if bot.was_successful() else "FAIL"
        print "- %s %s %s (attempts %d, elapsed %d seconds)" % (result, get_bot_results(bot), str(bot), bot.attempts(), bot.elapsed())
    print "\n=================================================================================\n"
    
    if options.failed_only == False:
        print "\nNow running rebot..."
        commands = []
        commands.append(options.rebot_cmd)
        commands.append("--name")
        commands.append(config.REPORT_NAME)
        commands.append("--output")
        commands.append(config.REPORT_FILENAME)
        commands.append("*.out.xml")
        update_options(commands, options.rebot_opts)

        cli = ""
        for cmd in commands:
            cli = cli + cmd + " "
        print cli
        print
        
        subprocess.call(commands, cwd=options.logs_folder)
    
    print "\nDone!"


#
# script launch support
#

if __name__ == "__main__":
    main()

