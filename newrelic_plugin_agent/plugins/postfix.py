"""
Postfix

"""
from newrelic_plugin_agent.plugins import base
import subprocess


class Postfix(base.Plugin):

    GUID = 'com.supportbee.newrelic_postfix_agent'

    def poll(self):
        self.add_gauge_value("Postfix/DeferredQueueSize", None, self.queue_size("deferred")) 
        self.add_gauge_value("Postfix/BounceQueueSize", None, self.queue_size("bounce")) 
        self.add_gauge_value("Postfix/HoldQueueSize", None, self.queue_size("hold"))
        self.add_gauge_value("Postfix/CorruptQueueSize", None, self.queue_size("corrupt"))
        self.add_gauge_value("Postfix/IncomingQueueSize", None, self.queue_size("incoming"))
        self.add_gauge_value("Postfix/ActiveQueueSize", None, self.queue_size("active")) 

        self.finish()

    def queue_size(self, queue):
        command = "find " + self.postfix_queue_directory() + "/" + queue + " type -f | wc -l"
        queue_size = int(self.run_shell_command(command))
        return queue_size

    def postfix_queue_directory(self):
        if not getattr(self, '_postfix_queue_directory', None):
            self._postfix_queue_directory = self.run_shell_command("postconf -h queue_directory")
        return self._postfix_queue_directory

    def run_shell_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        stdout_data, stderr_data = process.communicate()
        return stdout_data.rstrip()
