# (c) Copyright [2017] Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Loads experiment data and plots raw/smoothed batch times.

Usage:

>>> python time_analysis.py [PARAMETERS]

Parameters:

* ``--log-dir`` Scan this folder for *.log files. Scan recursively if ``--recursive`` is set.
* ``--log-file`` Get batch statistics from this experiment.
* ``--recursive`` Scan ``--log-dir`` folder recursively for log files.
"""
from __future__ import print_function
import argparse
from dlbs.logparser import LogParser
from dlbs.utils import IOUtils
import matplotlib.pyplot as plt
import numpy as np

def simple_moving_average(times, window_size):
    """Smoothes time series with simple moving average

    :param np.array time: Raw time series of batch times (milliseconds).
    :param int window_size: Size of a moving window.
    :return: Tuple of x and y values (x, y). Length of these lists is `len(times) - window_size`.
    """
    xs = range(window_size, len(times))
    ys = [0] * len(xs)
    # Compute first  value
    ys[0] = np.mean(times[0:window_size])
    for i in xrange(1, len(ys)):
        ys[i] = ys[i-1] + (times[window_size + i - 1] - times[i-1])/window_size
    return (xs,ys)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-dir', type=str, required=False, default=None,
                        help="Scan this folder for *.log files. "\
                             "Scan recursively if --recursive is set.")
    parser.add_argument('--log-file', type=str, required=False, default=None,
                        help="Get batch statistics from this experiment.")
    parser.add_argument('--recursive', required=False, default=False, action='store_true',
                        help='Scan --log-dir folder recursively for log files.')
    args = parser.parse_args()

    if args.log_dir is not None:
        files = IOUtils.find_files(args.log_dir, "*.log", args.recursive)
    else:
        files = []
    if args.log_file is not None:
        files.append(args.log_file)

    exps = LogParser.parse_log_files(files)
    for exp in exps:
        key = 'results.%s_times' % (exp['exp.phase'])
        if key not in exp:
            continue
        times = exp[key]
        xs = range(len(times))
        # Plot moving averages for different windows
        if exp['exp.device'] == 'gpu':
            title="%s / %s / GPU batch %s / GPUs count %s" % (exp['exp.framework_title'], exp['exp.model_title'], exp['exp.device_batch'], exp['exp.num_gpus'])
        else:
            title="%s / %s / CPU batch %d" % (exp['exp.framework_title'], exp['exp.model_title'], exp['exp.effective_batch'])
        plt.title(title)
        plt.xlabel('#iteration')
        plt.ylabel('batch time')
        plt.plot(xs, times)
        labels = ['Original']
        for window_size in [10, 30, 50, 70, 100]:
            xs,ys = simple_moving_average(times, window_size)
            line, = plt.plot(xs, ys)
            labels.append('Window=%d' % (window_size))
        legend = plt.legend(labels)
        plt.show()
        plt.clf()