import sys
import os
import time
import subprocess
import ppybot_config as config

from os import listdir
from os.path import isfile, join

#
# Generic support functions
#

def isWindows():
    return sys.platform.startswith("win")
        

#
# Generic support classes
#



# encapsulate a running pybot process
class Pybot():

    process = None
    started = False
    
    def __init__(self, folder, filename, args):
        self.folder = folder
        self.name = filename[0:len(filename)-len(".txt")]
        self.args = args
    
    def __del__(self):
        self._close_log()
        
    def __str__(self):
        return "pybot %s (pid: %d)" % (self.name, self.pid)

    def start(self):

        commands = []
        commands.append(config.PYBOT_CMD)
        for arg in self.args:
            commands.append(arg)
            
        commands.append("-o")
        commands.append("%s.xml" % self.name)
        commands.append("-l")
        commands.append("NONE")
        commands.append("-r")
        commands.append("NONE")
        commands.append(self.name + ".txt")

        self.log = open(os.path.join(folder, ("%s.log" % self.name)), "w")
        self.process = subprocess.Popen(commands, cwd=folder, stdout=self.log, stderr=self.log)
#         self.process = subprocess.Popen(commands, cwd=folder)
        self.pid = self.process.pid
        print str(self)+" started!"
        self.started = True
        self.start_time = time.time()
    
    def elapsed(self):
        return time.time() - self.start_time;
        
    def wait(self, timeout):
        self.process.wait()
        self._close_log();

    def isRunning(self):
        running = self.process != None and self.process.poll() == None
        if not running:
            print str(self)+" finished!"
            self._close_log();
        return running
    
    def isDone(self):
        return self.started == True and (not self.isRunning())
    
    def kill(self):
        if self.isRunning():
            self.process.kill()
            self.process.terminate()
            self.process.wait()
            self.process = None

        self._close_log()
        print "%s was killed after %d elapsed seconds" % (str(self), self.elapsed())

    def _close_log(self):
        if hasattr(self, 'log') and self.log != None:
            self.log.close()
            self.log=None


    

            
#         if isWindows():
#             os.system("taskkill /T /F /PID %s" % self.process.pid)
#         else:
#             os.system("kill -9 %s" % self.process.pid)



#
# Main execution script
#

if len(sys.argv) <= 1:
    print 'please specify a folder!'
    exit

max_parallel = config.MAX_PARALLEL_TESTS
if len(sys.argv) > 2:
    max_parallel = int(sys.argv[2])

max_runtime = config.MAX_EXECUTION_TIME
if len(sys.argv) > 3:
    max_runtime = int(sys.argv[3])

folder = sys.argv[1]
tests = [ f for f in listdir(folder) if isfile(join(folder,f)) and f.endswith(".txt")]
allBots = []
print "Tests found:"
for test in tests:
    allBots.append(Pybot(folder, test, []))
    print "- "+test;
    
print "\nStarting bots! (max parallel %d, max time allowed %d seconds) " % (max_parallel, max_runtime)

runningBots = []
while len(allBots) > 0 or len(runningBots) > 0:
    
    time.sleep(1)
    
    for bot in runningBots:
        if bot.isDone():
            runningBots.remove(bot)
        if bot.elapsed() > max_runtime:
            runningBots.remove(bot)
            bot.kill();

    if len(runningBots) == 5:
        continue
     
    if len(allBots) > 0:
        bot = allBots[0];
        allBots.remove(bot)
        runningBots.append(bot)
        bot.start()

print "\nAll finished!"
