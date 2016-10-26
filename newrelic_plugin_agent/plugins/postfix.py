"""
Postfix

"""
from newrelic_plugin_agent.plugins import base
import subprocess
import logging

LOGGER = logging.getLogger(__name__)

class ShellCommandFailed(Exception):
    """ Raised when a shell command fails """

class Postfix(base.Plugin):

    GUID = 'com.supportbee.newrelic_postfix_agent'

    def poll(self):
        try:
            self.add_gauge_value("Postfix/DeferredQueueSize", "messages", self.queue_size("deferred")) 
            self.add_gauge_value("Postfix/BounceQueueSize", "messages", self.queue_size("bounce")) 
            self.add_gauge_value("Postfix/HoldQueueSize", "messages", self.queue_size("hold"))
            self.add_gauge_value("Postfix/CorruptQueueSize", "messages", self.queue_size("corrupt"))
            self.add_gauge_value("Postfix/IncomingQueueSize", "messages", self.queue_size("incoming"))
            self.add_gauge_value("Postfix/ActiveQueueSize", "messages", self.queue_size("active")) 

            self.finish()
        except ShellCommandFailed as e:
            LOGGER.error(str(e))

    def queue_size(self, queue):
        command = "find " + self.postfix_queue_directory() + "/" + queue + " -type f | wc -l"
        queue_size = int(self.run_shell_command(command))
        return queue_size

    def postfix_queue_directory(self):
        if not getattr(self, '_postfix_queue_directory', None):
            self._postfix_queue_directory = self.run_shell_command("postconf -h queue_directory")
        return self._postfix_queue_directory

    def run_shell_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        stdout_data, stderr_data = process.communicate()
        if stderr_data:
            error_message = "Running shell command `{0}` failed with error: `{1}`".format(command, stderr_data.rstrip())
            raise ShellCommandFailed(error_message)

        return stdout_data.rstrip()
