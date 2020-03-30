import argparse
import psutil
import time
import numpy as np

"""
This is the command line parser that configures the thresholds for the available resources within this script.
The resources available to be configured for a threshold are: CPU, Memory and Storage
Example: python monitory.py --cpu 10.1
"""
parser = argparse.ArgumentParser(description='Resource monitoring. This script will alert you when CPU, Memory and or Storage space'
                                             'exceeds a certain threshold.')

parser.add_argument('--cpu',
                    dest='cpu_threshold_percent',
                    help='CPU utilization percentage threshold.')

parser.add_argument('--memory',
                    dest='memory_threshold_percent',
                    help='Memory/RAM utilization percentage threshold.')

args = parser.parse_args()

# Interval in seconds
THRESHOLD_CHECK_INTERVAL = 1
THRESHOLD_TIME_LAPSE = 20


def _append_fixed_length(value_list: [], v: int, max_size: int):
    """
    Keep a list of the last n values defined by max_size, when a new value is added the oldest value is discarded when the list exceeds max_size
    :param value_list: list of values
    :param v: the value to append to the list
    :param max_size: the maximum number of values the list should retain.
    :return:
    """
    if len(value_list) >= max_size:
        value_list.pop(0)

    value_list.append(v)


class CPUResource:
    def __init__(self, threshold_time, threshold_average: float):
        """
        Check the overall cpu utilization within the user space this script is running in.
        :param threshold_time: The reported time of the threshold check
        :param threshold_average: The max threshold to be compared against the threshold check
        """
        self.resource_name = "CPU"
        self.time_threshold_minutes = threshold_time
        self.threshold = threshold_average
        self.last_time_checked = time.time()
        self.list_of_values = []
        self.last_value = 0
        pass

    def is_beyond_threshold(self):
        """
            Tripping the CPU threshold asserts that the average load over the THRESHOLD_TIME_LAPSE
            averages above the threshold value. This ensures that spikes that occur once in a while
            are not reported if they are only a minor interference.
        """
        self.last_time_checked = time.time()
        _append_fixed_length(self.list_of_values, psutil.cpu_percent(), THRESHOLD_TIME_LAPSE)
        self.last_value = np.average(self.list_of_values)

        if self.last_value >= self.threshold and len(self.list_of_values) >= THRESHOLD_TIME_LAPSE:
            self.list_of_values.clear()
            return True

        return False


class MemoryResource:
    def __init__(self, threshold_time, threshold_average: float):
        """
        Check the overall memory utilization within the user space this script is running in.
        :param threshold_time: The reported time of the threshold check
        :param threshold_average: The max threshold to be compared against the threshold check
        """
        self.resource_name = "Memory"
        self.time_threshold_minutes = threshold_time
        self.threshold = threshold_average
        self.last_time_checked = time.time()
        self.list_of_values = []
        self.last_value = 0

    def is_beyond_threshold(self):
        """
            Tripping the Memory threshold asserts that the average load over the THRESHOLD_TIME_LAPSE
            averages above the threshold value. This ensures that spikes that occur once in a while
            are not reported if they are only a minor interference.

            It is most likely that once the memory  threshold is tripped, it will continue to be this way until someone manually
            dis-engages a running application or increases available memory.
        """
        self.last_time_checked = time.time()
        _append_fixed_length(self.list_of_values, psutil.virtual_memory()[2], THRESHOLD_TIME_LAPSE)
        self.last_value = np.average(self.list_of_values)

        if self.last_value >= self.threshold and len(self.list_of_values) >= THRESHOLD_TIME_LAPSE:
            self.list_of_values.clear()
            return True

        return False


class StorageResource:
    def __init__(self, threshold: float):
        self.resource_name = "Available Storage"
        pass

    def is_beyond_threshold(self):
        pass


def warn_threshold_breach(name, breach):
    """
    Send a warning that a threshold has been breached for a particular resource.
    :param name: Name of the resource
    :param breach: The value that breached the configured threshold for the resource name.
    :return: ...
    """
    print("Warning: Threshold breach for: " + name + ", value is: " + str(breach))


"""
From the argument parser, we add the requested resources to be scanned into the resource_to_check[] list.
Every THRESHOLD_CHECK_INTERVAL time lapse, each resource within the list has the configured threshold checked.,
"""
resources_to_check = []

if 'cpu_threshold_percent' in args:
    r = CPUResource(THRESHOLD_TIME_LAPSE, args.cpu_threshold_percent)
    resources_to_check.append(r)

if 'memory_threshold_percent' in args:
    r = MemoryResource(THRESHOLD_TIME_LAPSE, args.memory_threshold_percent)
    resources_to_check.append(r)

monitor_loop = True
while monitor_loop:
    time.sleep(THRESHOLD_CHECK_INTERVAL)
    print("Checking...")

    for r in resources_to_check:
        if r.is_beyond_threshold():
            warn_threshold_breach(r.resource_name, r.last_value)
            pass

    pass

