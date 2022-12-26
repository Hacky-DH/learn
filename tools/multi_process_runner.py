import collections
import faulthandler
import json
import logging
import multiprocessing as mp
import os
import queue
import signal
import sys
import threading
import time
import traceback

# _ProcessStatusInfo contains process status information. When is_successful
# attribute is True, the subprocess has ended successfully, or if False, the
# exception stack trace info is stored in exc_info to pass on to parent process
# to be re-raised.
_ProcessStatusInfo = collections.namedtuple(
    '_ProcessStatusInfo',
    ['task_type', 'task_id', 'is_successful', 'exc_info', 'return_value'])

# Information returned from a successful MultiProcessRunner run.
MultiProcessRunnerResult = collections.namedtuple('MultiProcessRunnerResult',
                                                  ['return_value', 'stdout'])

# CUDA_VISIBLE_DEVICES is set to -1
ProcessEnvironment = collections.namedtuple(
    'ProcessEnvironment',
    ['task_type', 'task_id', 'cluster_spec', 'rpc_layer', 'grpc_fail_fast'])

# Resources for communication between worker processes and the main process.
#
# `process_status_queue` is used by `multi_process_runner` internally for
#   communication from subprocesses to the parent process for whether it's been
#   successful, and if not what the error stack trace is.
# `parent_to_sub_queue` is used for communications from parent to subprocess.
#   Currently this is only used to terminate subprocesses.
# `streaming_pipe_w` is to stream stdout and stderr from subprocesses to parent
#   process.
# `barrier` is a barrier for the party of all subprocesses.
Resources = collections.namedtuple('Resources', [
    'process_status_queue', 'parent_to_sub_queue', 'streaming_pipe_w',
    'barrier'
])

# Default time out sec is selected so that it's handled before the default
# "medium" timeout of the test runs.
_DEFAULT_TIMEOUT_SEC = 200

# The timeout in seconds to wait to force kill a child process. When a child
# process times out we first try to SIGTERM it so that it has a chance to dump
# stacktraces. However dumping stacktrace can take a long time.
_FORCE_KILL_WAIT_SEC = 30


class MultiProcessRunner(object):
    '''
    A utility class to start multiple processes to simulate a cluster

    simple version from tensorflow/python/distribute/multi_process_runner.py
    tf version 2.6.0
    it can be used in pytest

    This class is not thread-safe.
    '''

    def __init__(self,
                 fn,
                 cluster_spec,
                 rpc_layer=None,
                 max_run_time=None,
                 grpc_fail_fast=None,
                 stream_output=True,
                 return_output=False,
                 daemon=False,
                 dependence_on_chief=True,
                 auto_restart=False,
                 args=None,
                 kwargs=None):
        """Instantiation of a `MultiProcessRunner`.

    Args:
      fn: Function to be run on child processes. This will be run on processes
        for all task types.
      cluster_spec: Dict for cluster spec. The following is an
        example of cluster with three workers and two ps's.
        {"worker": ["worker0.example.com:2222",
                    "worker1.example.com:2222",
                    "worker2.example.com:2222"],
         "ps": ["ps0.example.com:2222",
                "ps1.example.com:2222"]}
      rpc_layer: RPC layer to use. Default value is 'grpc'.
      max_run_time: `None` or integer. If not `None`, child processes are forced
        to exit at approximately this many seconds after this utility is called.
        We achieve this through `signal.alarm()` api. Note that this is best
        effort at Python level since Python signal handler does not get executed
        when it runs lower level C/C++ code. So it can be delayed for
        arbitrarily long time. If any of the child process is still running when
        `max_run_time` is up, they will be force-terminated and an
        `UnexpectedSubprocessExitError` may be raised. If `None`, child
        processes are not forced to exit.
      grpc_fail_fast: Whether GRPC connection between processes should fail
        without retrying. Defaults to None, in which case the environment
        variable is not explicitly set.
      stream_output: True if the output/error from the subprocesses should be
        streamed to be printed in parent process' log. Defaults to True.
      return_output: If True, the output/error from the subprocesses should be
        collected to be attached to the resulting namedtuple returned from
        `join()`. The list of output can be retrieved via `stdout` attribute.
        Defaults to False.
      daemon: Whether to start processes as daemons.
      dependence_on_chief: Whether to terminates the cluster if the chief exits.
        If auto_restart is True, it only terminates the cluster if the chief
        exits with a zero exit code.
      auto_restart: Whether to automatically restart processes that exit with
        non-zero exit code.
      args: Positional arguments to be sent to `fn` run on subprocesses.
      kwargs: Keyword arguments to be sent to `fn` run on subprocesses.

    Raises:
      ValueError: if there are more than one chief in the `cluster_spec`.
    """

        assert cluster_spec is not None
        if 'chief' in cluster_spec and len(cluster_spec['chief']) > 1:
            raise ValueError(
                'If chief exists in the cluster, there must be at most '
                'one chief. Current `cluster_spec` has {} chiefs.'.format(
                    len(cluster_spec['chief'])))
        if not callable(fn):
            raise ValueError('fn is not a callable')

        self._fn = fn
        self._cluster_spec = cluster_spec
        self._rpc_layer = rpc_layer or 'grpc'
        self._max_run_time = max_run_time
        self._grpc_fail_fast = grpc_fail_fast
        self._stream_output = stream_output
        self._return_output = return_output
        self._dependence_on_chief = dependence_on_chief
        self._daemon = daemon
        self._auto_restart = auto_restart
        self._args = args or ()
        self._kwargs = kwargs or {}

        self._joined = False
        self._process_lock = threading.Lock()
        # Guarded by self._process_lock.
        self._processes = {}
        # Record which processes are terminated. Due to a bug in Python<3.7,
        # terminated processes return 255 exit code, which should cause an exception
        # in join().
        # https://bugs.python.org/issue30589
        # Guarded by self._process_lock.
        self._terminated = set()
        self._reading_threads = []

        self._manager = manager()
        self._process_status_queue = self._manager.Queue()
        self._parent_to_sub_queue = self._manager.Queue()
        parties = sum(
            len(addresses) for addresses in self._cluster_spec.values())
        self._barrier = self._manager.Barrier(parties)

        # We use a queue to collect outputs from worker processes since it's thread
        # safe.
        self._streaming_queue = self._manager.Queue()

        self._watchdog_thread = None

    def set_args(self, args=None, kwargs=None):
        self._args = args or self._args
        self._kwargs = kwargs or self._kwargs

    def _continuously_readline_from_sub(self, pipe_r, task_type, task_id):
        """Function to continuously read lines from subprocesses."""
        with os.fdopen(pipe_r.fileno(), 'r', closefd=False) as reader:
            for line in reader:
                task_string = '[{}-{}]:'.format(task_type, task_id)
                formatted_line = '{} {}'.format(task_string.ljust(14), line)
                if self._stream_output:
                    print(formatted_line, end='', flush=True)
                if self._return_output:
                    self._streaming_queue.put(formatted_line)

    def _start_subprocess_and_reading_thread(self,
                                             task_type,
                                             task_id,
                                             cluster_spec=None,
                                             fn=None,
                                             args=None,
                                             kwargs=None):
        """Start a subprocess and a thread the reads lines from the subprocess."""
        cluster_spec = cluster_spec or self._cluster_spec

        process_env = ProcessEnvironment(task_type=task_type,
                                         task_id=task_id,
                                         cluster_spec=cluster_spec,
                                         rpc_layer=self._rpc_layer,
                                         grpc_fail_fast=self._grpc_fail_fast)
        pipe_r, pipe_w = mp.Pipe(duplex=False)
        resources = Resources(
            process_status_queue=self._process_status_queue,
            parent_to_sub_queue=self._parent_to_sub_queue,
            streaming_pipe_w=pipe_w,
            barrier=self._barrier,
        )
        if fn is None:
            fn, args, kwargs = self._fn, self._args, self._kwargs

        p = _Process(process_env=process_env,
                     target=_ProcFunc(),
                     args=(resources, process_env, fn, args, kwargs),
                     daemon=self._daemon)
        p.start()
        self._processes[(task_type, task_id)] = p
        self._terminated.discard((task_type, task_id))

        # For each subprocess, we dedicate a thread continuously reading lines
        # from them.
        thread = threading.Thread(target=self._continuously_readline_from_sub,
                                  args=(pipe_r, task_type, task_id))
        thread.start()
        self._reading_threads.append(thread)

        if self._watchdog_thread is None or not self._watchdog_thread.is_alive(
        ):
            self._watchdog_thread = threading.Thread(
                target=self._process_watchdog)
            self._watchdog_thread.start()

    def start(self):
        """Starts processes, one for each task in `cluster_spec`.

    Note that this is best effort by the applicable multiprocessing library,
    and it may take up to seconds for a subprocess to be successfully started.
    """
        with self._process_lock:
            if self._processes:
                raise ValueError('MultiProcessRunner already started.')
            if self._joined:
                raise ValueError('cannot start new processes after'
                                 'MultiProcessRunner.join() is called')

            for task_type, addresses in self._cluster_spec.items():
                for task_id, _ in enumerate(addresses):
                    self._start_subprocess_and_reading_thread(
                        task_type, task_id)

        if self._max_run_time is not None:

            def handler(signum, frame):
                del signum, frame
                self.terminate_all()

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(self._max_run_time)

    def start_in_process_as(self, as_task_type, as_task_id):
        """Start the processes, with the specified task run in main process.

    This is similar to `start()` except that the task with task_type
    `as_task_type` and task_id `as_task_id` is run in the main process.
    This method is particularly useful when debugging tool such as `pdb` is
    needed in some specific task. Note that since this method is blocking until
    that specific task exits, additional actions would need a thread to be
    called:

    ```python
    def fn():
      # user code to be run
      import pdb; pdb.set_trace()

    def follow_ups():
      time.sleep(5)
      mpr.start_single_process(
          task_type='evaluator',
          task_id=0)

    mpr = multi_process_runner.MultiProcessRunner(fn,cluster_spec)
    threading.Thread(target=follow_ups).start()
    mpr.start_in_process_as(as_task_type='chief', as_task_id=0)
    mpr.join()
    ```

    Note that if `return_output=True`, the logs/stdout by task
    run by the main process is not available in result.stdout.

    Args:
      as_task_type: The task type to be run in the main process.
      as_task_id: The task id to be run in the main process.
    """
        if self._processes:
            raise ValueError('MultiProcessRunner already started.')
        with self._process_lock:
            if self._joined:
                raise ValueError('cannot start new processes after'
                                 'MultiProcessRunner.join() is called')
            for task_type, addresses in self._cluster_spec.items():
                for task_id, _ in enumerate(addresses):
                    if not (task_type == as_task_type
                            and task_id == as_task_id):
                        self._start_subprocess_and_reading_thread(
                            task_type, task_id)

        _set_tf_config(as_task_type, as_task_id, self._cluster_spec,
                       self._rpc_layer)
        self._fn(*self._args, **self._kwargs)

    def start_single_process(self,
                             task_type,
                             task_id,
                             cluster_spec=None,
                             fn=None,
                             args=None,
                             kwargs=None):
        """Starts a single process.

    This starts a process in the cluster with the task type, task id, and the
    process function (`fn`). If process function is `None`, the function
    provided at `__init__` will be used. If `cluster_spec` is `None`, the
    cluster spec provided at `__init__` will be used.

    TODO(rchao): It is meant that all subprocesses will be updated with the new
    cluster spec, but this has yet to be implemented. At this time only the
    newly started subprocess picks up this updated cluster spec.

    Args:
      task_type: The task type.
      task_id: The task id.
      cluster_spec: The cluster spec to be used on the newly started
        process. If `None`, the cluster spec provided at `__init__` will be
        used.
      fn: The process function to be run on the newly started
        process. If specified, specify `args` and `kwargs` as well. If `None`,
        the function provided at `__init__` will be used.
      args: Optional positional arguments to be supplied in `fn`.
      kwargs: Optional keyword arguments to be supplied in `fn`.
    """
        with self._process_lock:
            if self._joined:
                raise ValueError('cannot start new processes after'
                                 'MultiProcessRunner.join() is called')
            self._start_subprocess_and_reading_thread(
                task_type,
                task_id,
                cluster_spec=cluster_spec,
                fn=fn,
                args=args or (),
                kwargs=kwargs or {})

    def _queue_to_list(self, queue_to_convert):
        """Convert `queue.Queue` to `list`."""
        list_to_return = []
        # Calling `queue.empty()` is not reliable.
        while True:
            try:
                list_to_return.append(queue_to_convert.get(block=False))
            except queue.Empty:
                break
        return list_to_return

    def _get_process_statuses(self):
        # One worker may have multiple statuses. We only keep the last one.
        statuses = {}
        for status in self._queue_to_list(self._process_status_queue):
            statuses[(status.task_type, status.task_id)] = status
        return statuses

    def get_process_id(self, task_type, task_id):
        """Returns the subprocess id given the task type and task id."""
        with self._process_lock:
            p = self._processes.get((task_type, task_id), None)
        return p.pid if p else None

    def get_process_exit_code(self, task_type, task_id):
        """Returns the subprocess exit code given the task type and task id.

    Args:
      task_type: The task type.
      task_id: The task id.

    Returns:
      The subprocess exit code; `None` if the subprocess has not exited yet.

    Raises:
      KeyError: If the corresponding subprocess is not found with `task_type`
        and `task_id`.
    """
        with self._process_lock:
            p = self._processes[(task_type, task_id)]
        return p.exitcode if p else None

    def process_exists(self, task_type, task_id):
        """Returns whether the subprocess still exists given the task type and id.

    Args:
      task_type: The task type.
      task_id: The task id.

    Returns:
      Boolean; whether the subprocess still exists. If the subprocess has
      exited, this returns False.
    """
        return self.get_process_exit_code(task_type, task_id) is None

    def _process_watchdog(self):
        """Simulates a cluster management system.

    - If auto_restart is True, it restarts processes that exit with a non-zero
      exit code. Note that when join() times out it overrides auto_restart to
      False.
    - If dependence_on_chief is True, it terminates all processes once the chief
      exits. If auto_restart is also True, it only terminates all processes if
      the chief exit with a zero exit code, otherwise it restarts the chief.

    This runs in self._watchdog_thread.
    """
        while True:
            time.sleep(1)
            with self._process_lock:
                chief = self._processes.get(('chief', 0), None)
                # Terminate the cluster when _dependence_on_chief is True if either:
                # - chief has exited with zero exit code.
                # - chief has exited with non-zero exit code and self._auto_restart is
                #   False.
                if chief and self._dependence_on_chief and chief.exitcode is not None:
                    if chief.exitcode == 0 or (not self._auto_restart):
                        for p in self._processes.values():
                            # Give other processes a chance to exit on their own.
                            p.join(timeout=3)
                        self._terminate_all()
                        for p in self._processes.values():
                            p.join()
                        return

                # Auto restart failed processes if self._auto_restart is True.
                if self._auto_restart:
                    has_failure = False
                    for (task_type, task_id), p in self._processes.items():
                        if p.exitcode is not None and p.exitcode != 0:
                            has_failure = True
                            logging.info('Restarting failed %s-%d', task_type,
                                         task_id)
                            self._start_subprocess_and_reading_thread(
                                task_type, task_id)
                    if has_failure:
                        continue

                # Exit the thread if all processes have exited at this point.
                if all(p.exitcode is not None
                       for p in self._processes.values()):
                    return

    def _reraise_if_subprocess_error(self, process_statuses):
        for process_status in process_statuses.values():
            assert isinstance(process_status, _ProcessStatusInfo)
            if not process_status.is_successful:
                raise RuntimeError(process_status.exc_info)

    def join(self, timeout=_DEFAULT_TIMEOUT_SEC):
        """Joins all the processes with timeout.

    If any of the subprocesses does not exit approximately after `timeout`
    seconds has passed after `join` call, this raises a
    `SubprocessTimeoutError`.

    Note: At timeout, it uses SIGTERM to terminate the subprocesses, in order to
    log the stack traces of the subprocesses when they exit. However, this
    results in timeout when the test runs with tsan (thread sanitizer); if tsan
    is being run on the test targets that rely on timeout to assert information,
    `MultiProcessRunner.terminate_all()` must be called after `join()`, before
    the test exits, so the subprocesses are terminated with SIGKILL, and data
    race is removed.

    Args:
      timeout: optional integer or `None`. If provided as an integer, and not
      all processes report status within roughly `timeout` seconds, a
      `SubprocessTimeoutError` exception will be raised. If `None`, `join` never
      times out.

    Returns:
      A `MultiProcessRunnerResult` object, which has two attributes,
      `return_value` and `stdout`. `return_value` always contains a list of
      return values from the subprocesses, although the order is not meaningful.
      If `return_output` argument is True at `__init__`, `stdout` is available
      that contains a list of all messages from subprocesses' stdout and stderr.

    Raises:
      SubprocessTimeoutError: if not all processes report status approximately
        within `timeout` seconds. When this is raised, a
        `MultiProcessRunnerResult` object can be retrieved by
        `SubprocessTimeoutError`'s mpr_result attribute, which has the same
        structure as above 'Returns' section describes.
      UnexpectedSubprocessExitError: If any of the subprocesses did not exit
        properly (for example, they exit on SIGTERM or SIGKILL signal). When
        this is raised, a `MultiProcessRunnerResult` object can be retrieved by
        `UnexpectedSubprocessExitError`'s mpr_result attribute, which has the
        same structure as above 'Returns' section describes. If `max_run_time`
        is not `None`, it is expected that some subprocesses may be
        force-killed when `max_run_time` is up, and this is raised in those
        cases.
      Exception: if there is an Exception propagated from any subprocess. When
        this is raised, a `MultiProcessRunnerResult` object can be retrieved by
        `UnexpectedSubprocessExitError`'s mpr_result attribute, which has the
        same structure as above 'Returns' section describes.
    """
        if timeout and not isinstance(timeout, int):
            raise ValueError('`timeout` must be an integer or `None`.')
        with self._process_lock:
            if self._joined:
                raise ValueError("MultiProcessRunner can't be joined twice.")
            self._joined = True

        self._watchdog_thread.join(timeout)
        if self._watchdog_thread.is_alive():
            # Timeout. Force termination to dump worker processes stack trace.
            with self._process_lock:
                self._auto_restart = False
            logging.error(
                'Timeout when joining for child processes. Terminating...')
            self.terminate_all(sig=signal.SIGTERM)
            # Wait for the processes to terminate by themselves first, so they have a
            # chance to dump stacktraces. After _FORCE_KILL_WAIT_SEC, we SIGKILL them.
            self._watchdog_thread.join(_FORCE_KILL_WAIT_SEC)
            if self._watchdog_thread.is_alive():
                logging.error('Timeout when waiting for child processes to '
                              'print stacktrace. Sending SIGKILL...')
                self.terminate_all()
                self._watchdog_thread.join()
            process_statuses = self._get_process_statuses()
            self._reraise_if_subprocess_error(process_statuses)
            raise SubprocessTimeoutError(
                'One or more subprocesses timed out, where timeout was set to {}s. '
                'Please change the `timeout` argument for '
                '`MultiProcessRunner.join()` or `multi_process_runner.run()` '
                'if it should be adjusted.'.format(timeout),
                self._get_mpr_result(process_statuses))

        for (task_type, task_id), p in self._processes.items():
            logging.info('%s-%d exit code: %s', task_type, task_id, p.exitcode)

        process_statuses = self._get_process_statuses()
        self._reraise_if_subprocess_error(process_statuses)

        # Checking all the processes that are expected to exit properly.
        for (task_type, task_id), p in self._processes.items():
            # Successfully exiting process has exit code 0. We ignore processes that
            # are terminated.
            assert p.exitcode is not None
            if (p.exitcode > 0
                    and (task_type, task_id) not in self._terminated):
                raise UnexpectedSubprocessExitError(
                    'Subprocess %s-%d exited with exit code %s. See logs for details.'
                    % (task_type, task_id, p.exitcode),
                    self._get_mpr_result(process_statuses))

        logging.info('Joining log reading threads.')
        for thread in self._reading_threads:
            thread.join()
        logging.info('Joined log reading threads.')

        # Clear the alarm.
        signal.alarm(0)

        return self._get_mpr_result(process_statuses)

    def _get_mpr_result(self, process_statuses):
        stdout = self._queue_to_list(self._streaming_queue)
        return_values = []
        for process_status in process_statuses.values():
            if process_status.return_value is not None:
                return_values.append(process_status.return_value)
        return MultiProcessRunnerResult(stdout=stdout,
                                        return_value=return_values)

    def terminate(self, task_type, task_id):
        """Terminates the process with `task_type` and `task_id`.

    If auto_retart=True, the terminated task will be restarted unless the chief
    has already exited with zero exit code.

    Args:
      task_type: the task type.
      task_id: the task id.

    """
        with self._process_lock:
            p = self._processes.get((task_type, task_id), None)
            if p is None:
                raise ValueError('{}-{} does not exist'.format(
                    task_type, task_id))
            self._terminated.add((task_type, task_id))
            self._parent_to_sub_queue.put('terminate {} {}'.format(
                task_type, task_id))
            p.join()

    def _terminate_all(self, sig=None):
        """Terminates all subprocesses.

    The caller is required to hold self._process_lock.

    Args:
      sig: the signal used to terminate the process. The default is SIGKILL.
    """

        # Use SIGKILL as default. In systems where that's unavailable such as
        # windows, use SIGTERM.
        sig = sig or getattr(signal, 'SIGKILL', signal.SIGTERM)
        for (task_type, task_id), p in self._processes.items():
            if p.exitcode is not None:
                logging.info('%s-%d has already exited. Not terminating.',
                             task_type, task_id)
                continue
            try:
                os.kill(p.pid, sig)
                self._terminated.add((task_type, task_id))
                logging.info('%s-%d terminated with signal %r.', task_type,
                             task_id, sig)
            except ProcessLookupError:
                logging.info('Attempting to kill %s-%d but it does not exist.',
                             task_type, task_id)

    def terminate_all(self, sig=None):
        """Terminates all subprocesses."""
        with self._process_lock:
            self._terminate_all(sig)


class _Process(mp.Process):
    """A modified `multiprocessing.Process` that can set up environment variables."""

    # TODO(crccw): consider moving other logics in _ProcFunc to _Process.

    def __init__(self, process_env, **kwargs):
        super(_Process, self).__init__(**kwargs)
        self._process_env = process_env
        self._actual_run = getattr(self, 'run')
        self.run = self._run_with_setenv

    def _run_with_setenv(self):
        # We need to set environment variables before doing anything because
        # setenv() is not thread-safe.
        process_env = self._process_env
        if process_env.grpc_fail_fast is not None:
            os.environ['GRPC_FAIL_FAST'] = str(process_env.grpc_fail_fast)
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        _set_tf_config(process_env.task_type, process_env.task_id,
                       process_env.cluster_spec, process_env.rpc_layer)
        return self._actual_run()


class _ProcFunc(object):
    """Represents a callable to run in a subprocess."""

    def _message_checking_func(self, task_type, task_id):
        """A function that regularly checks messages from parent process."""
        while True:
            try:
                message = self._resources.parent_to_sub_queue.get(block=False)

                # Currently the only possible message is termination.
                if not message.startswith('terminate'):
                    raise ValueError(
                        'Unrecognized message: {}'.format(message))

                if message == 'terminate {} {}'.format(task_type, task_id):
                    break
                else:
                    # If the message is not targeting this process, put it back to the
                    # queue.
                    self._resources.parent_to_sub_queue.put(message)
                    time.sleep(1)
            except queue.Empty:
                time.sleep(0.1)
        self._resources.process_status_queue.put(
            _ProcessStatusInfo(task_type=task_type,
                               task_id=task_id,
                               is_successful=True,
                               exc_info=None,
                               return_value=None))
        # `os._exit(1)` is used to more reliably terminate a subprocess.
        os._exit(1)

    def _close_streaming(self):
        """Close stdout, stderr and streaming pipe.

    We need to explicitly close them since Tensorflow may take a while to exit,
    so that the reading threads in the main process can exit more quickly.
    """
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout.close()
        sys.stderr.close()
        self._resources.streaming_pipe_w.close()

    def __call__(self, resources, process_env, fn, args, kwargs):
        """The wrapper function that actually gets run in child process(es)."""

        global _barrier

        self._resources = resources
        _barrier = self._resources.barrier

        faulthandler.enable()
        faulthandler.register(signal.SIGTERM, chain=True)

        # Assign sys.stdout and sys.stderr as duplicates of `streaming_pipe_w` so
        # print() and logging.*() write directly to `streaming_pipe_w`.
        # Unfortunately since we cannot prepend task_type and task_id information to
        # the streamed logs we will need a thread per subprocess to distinguish
        # where the piece of message is from.
        os.dup2(resources.streaming_pipe_w.fileno(), sys.stdout.fileno())
        os.dup2(resources.streaming_pipe_w.fileno(), sys.stderr.fileno())

        pid = os.getpid()
        logging.info('Subprocess with PID %d (%s, %d) is now being started.',
                     pid, process_env.task_type, process_env.task_id)
        logging.info('TF_CONFIG: %r', os.environ['TF_CONFIG'])

        # The thread will be dedicated to checking messages from the parent process.
        threading.Thread(  # pylint: disable=unexpected-keyword-arg
            target=self._message_checking_func,
            args=(process_env.task_type, process_env.task_id),
            daemon=True).start()

        info = _run_contained(process_env.task_type, process_env.task_id, fn,
                              args, kwargs)
        self._resources.process_status_queue.put(info)

        # Re-raise the exception in addition to reporting it to the parent
        # process, so that even if `--test_timeout` flag is set and the
        # error doesn't make it to be shown in parent process before bazel's
        # timeout, the log would still show what happens in this subprocess,
        # instead of silently suppressing the error due to early bazel
        # timeout. Raising an error in the subprocess produces stack trace in
        # the log, but the program continues running.
        if not info.is_successful:
            raise RuntimeError(info.exc_info)

        self._close_streaming()

        # Exit with code 0 as it's considered successful exit at this point.
        sys.exit(0)


def _run_contained(task_type, task_id, fn, args, kwargs):
    """Runs `fn` with `args` and `kwargs`.

  The function returns _ProcessStatusInfo which captures the return value and
  the exception.

  Args:
    task_type: the task type.
    task_id: the task index.
    fn: the function to be run.
    args: optional positional arguments to be supplied in `fn`.
    kwargs: optional keyword arguments to be supplied in `fn`.

  Returns:
    a _ProcessStatusInfo.

  """
    is_successful = False
    return_value = None
    exc_info = None
    try:
        return_value = fn(*args, **kwargs)
        is_successful = True
        return _ProcessStatusInfo(task_type=task_type,
                                  task_id=task_id,
                                  is_successful=is_successful,
                                  exc_info=exc_info,
                                  return_value=return_value)

    # If `fn` ends up exiting with `sys.exit()`, the `SystemExit` is not
    # handled here.
    except Exception as e:  # pylint: disable=broad-except
        traceback.print_exc()
        return _ProcessStatusInfo(task_type=task_type,
                                  task_id=task_id,
                                  is_successful=is_successful,
                                  exc_info=str(e),
                                  return_value=return_value)


class SubprocessTimeoutError(RuntimeError):
    """An error that indicates there is at least one subprocess timing out.

  When this is raised, a namedtuple object representing the multi-process run
  result can be retrieved by
  `multi_process_runner.SubprocessTimeoutError`'s
  `mpr_result` attribute. See
  `multi_process_runner.run` for more information.
  """

    def __init__(self, msg, mpr_result):
        super(SubprocessTimeoutError, self).__init__(msg)
        self.mpr_result = mpr_result


class UnexpectedSubprocessExitError(RuntimeError):
    """An error indicating there is at least one subprocess with unexpected exit.

  When this is raised, a namedtuple object representing the multi-process run
  result can be retrieved by
  `multi_process_runner.UnexpectedSubprocessExitError`'s
  `mpr_result` attribute. See
  `multi_process_runner.run` for more information.
  """

    def __init__(self, msg, mpr_result):
        super(UnexpectedSubprocessExitError, self).__init__(msg)
        self.mpr_result = mpr_result


def _set_tf_config(task_type, task_id, cluster_spec, rpc_layer=None):
    """Set TF_CONFIG environment variable."""
    tf_config_dict = {
        'cluster': cluster_spec,
        'task': {
            'type': task_type,
            'index': task_id,
        },
    }
    if rpc_layer is not None:
        tf_config_dict['rpc_layer'] = rpc_layer
    os.environ['TF_CONFIG'] = json.dumps(tf_config_dict)


def run(fn,
        cluster_spec,
        rpc_layer=None,
        max_run_time=None,
        return_output=False,
        timeout=_DEFAULT_TIMEOUT_SEC,
        args=None,
        kwargs=None):
    """Run `fn` in multiple processes according to `cluster_spec`.

  Given a callable `fn`, `multi_process_runner.run`
  launches multiple processes, each of which runs `fn`. These processes are
  referred to as "subprocesses" or "child processes". Each of those subprocesses
  will have their `TF_CONFIG` environment variable set, according to
  `cluster_spec` and their task types. The stdout of the subprocesses are
  streamed to the main process' and thus available in logs (if `stream_output`
  is True), with [type-id] prefix.

  `multi_process_runner.run` will block until all
  subprocesses have successfully exited, and return a namedtuple object that
  represents the run result. This object has a `return_value` attribute, which
  is a list that contains subprocesses `fn`'s return values, for those
  subprocesses that successfully returned from `fn`. The order of `return_value`
  list is not meaningful. If an optional arg `return_output` (default to False)
  is set to True, the namedtuple object will have an additional attribute
  `stdout`, which is a list containing the stdout of the subprocesses. If any
  subprocess' `fn` ends up raising an error, that error will be reraised from
  `multi_process_runner.run`, and the aforementioned
  namedtuple object will be available through the exception's
  `mpr_result` attribute.

  This utility is used for simulating running TensorFlow programs across
  multiple task types, and each of the task type may contain more than one task
  (except for "chief" where more than one task is prohibited). Test coverage of
  multi-worker training is the main application of this utility, where code
  written for multi-worker training can be realistically covered in unit tests.

  Args:
    fn: Function to be run on child processes. This will be run on processes for
      all task types.
    cluster_spec: Dict for cluster spec. The following is an example of
      cluster with three workers and two ps's.
      {"worker": ["worker0.example.com:2222",
                  "worker1.example.com:2222",
                  "worker2.example.com:2222"],
       "ps": ["ps0.example.com:2222",
              "ps1.example.com:2222"]}
    rpc_layer: RPC layer to use. Default value is 'grpc'.
    max_run_time: `None` or integer. If not `None`, child processes are forced
      to exit at approximately this many seconds after this utility is called.
      We achieve this through `signal.alarm()` api. Note that this is best
      effort at Python level since Python signal handler does not get executed
      when it runs lower level C/C++ code. So it can be delayed for arbitrarily
      long time. If any of the child process is still running when
      `max_run_time` is up, they will be force-terminated and an
      `multi_process_runner
      .UnexpectedSubprocessExitError`
      may be raised. If `None`, child processes are not forced to exit.
    return_output: If True, the output/error from the subprocesses should be
      collected to be attached to the resulting namedtuple returned from this
      utility. The list of output can be retrieved via `stdout` attribute.
      Defaults to False.
    timeout: optional integer or `None`. If provided as an integer, and not all
      processes report status within roughly `timeout` seconds, a
      `multi_process_runner.SubprocessTimeoutError`
      exception will be raised. If `None`,
      `multi_process_runner.run` never times out.
      Defaults to the constant `_DEFAULT_TIMEOUT_SEC` defined in
      `multi_process_runner` module.
    args: Positional arguments to be sent to `fn` run on subprocesses.
    kwargs: Keyword arguments to be sent to `fn` run on subprocesses.

  Returns:
      A namedtuple object, which has two attributes,
      `return_value` and `stdout`. `return_value` always contains a list of
      returnvalues from the subprocesses, although the order is not meaningful.
      If `return_output` argument is True, `stdout` is available that contains a
      list of all messages from subprocesses' stdout and stderr, and the order
      is mostly chronological.

  Raises:
    ValueError: if there are more than one chief in the `cluster_spec`.
    multi_process_runner.SubprocessTimeoutError: if
      not all processes report status approximately
      within `timeout` seconds. When this is raised, a
      namedtuple object can be retrieved by
      `multi_process_runner.SubprocessTimeoutError`'s
      `mpr_result` attribute, which has the same
      structure as above 'Returns' section describes.
    multi_process_runner.UnexpectedSubprocessExitError:
      If any of the subprocesses did not exit
      properly (for example, they exit on SIGTERM or SIGKILL signal). When
      this is raised, a namedtuple object can be retrieved by
      `multi_process_runner.UnexpectedSubprocessExitError`'s
      `mpr_result` attribute, which has the
      same structure as above 'Returns' section describes. If `max_run_time`
      is not `None`, it is expected that some subprocesses may be
      force-killed when `max_run_time` is up, and this is raised in those
      cases.
    Exception: if there is an Exception propagated from any subprocess. When
      this is raised, a namedtuple object can be retrieved by
      `multi_process_runner
      .UnexpectedSubprocessExitError`
      `mpr_result` attribute, which has the
      same structure as above 'Returns' section describes.
  ```
  """
    runner = MultiProcessRunner(fn,
                                cluster_spec,
                                rpc_layer,
                                max_run_time=max_run_time,
                                return_output=return_output,
                                args=args,
                                kwargs=kwargs)
    runner.start()
    return runner.join(timeout)


# This is set by MultiProcessRunner in worker processes.
_barrier = None


def get_barrier():
    """Returns a `multiprocessing.Barrier` for `multi_process_runner.run`.

  `get_barrier()` returns
  a `multiprocessing.Barrier` object which can be used within `fn` of
  `multi_process_runner` to wait with
  `barrier.wait()` call until all other tasks have also reached the
  `barrier.wait()` call, before they can proceed individually.

  Note that all tasks (subprocesses) have to reach `barrier.wait()` call to
  proceed. Currently it is not supported to block on only a subset of tasks
  in the cluster.

  Example:
  ```python

  def fn():
    some_work_to_be_done_by_all_tasks()

    multi_process_runner.get_barrier().wait()

    # The barrier guarantees that at this point, all tasks have finished
    # `some_work_to_be_done_by_all_tasks()`
    some_other_work_to_be_done_by_all_tasks()

  result = multi_process_runner.run(
      fn=fn,
      cluster_spec=()
  ```


  Returns:
    A `multiprocessing.Barrier` for `multi_process_runner.run`.
  """
    if _barrier is None:
        raise ValueError(
            'barrier is not defined. It is likely because you are calling '
            'get_barrier() in the main process. get_barrier() can only be called '
            'in the subprocesses.')
    return _barrier


_manager = None
_manager_lock = threading.Lock()


def manager():
    """Returns the multiprocessing manager object for concurrency tools.

  The manager object is useful as it controls a server process that holds
  the python objects that can be shared across processes. This can be used
  for parent-subprocess communication:

  ```python
  manager = multi_process_runner.manager()
  some_event_happening_in_subprocess = manager.Event()
  mpr = multi_process_runner.MultiProcessRunner(fn, cluster_spec,
      args=(some_event_happening_in_subprocess,))
  mpr.start()
  some_event_happening_in_subprocess.wait()
  # Do something that only should after some event happens in subprocess.
  ```

  Note that the user of multi_process_runner should not create additional
  `multiprocessing.Manager()` objects; doing so can result in segfault in
  some cases.

  This method should only be called after multi_process_runner.test_main() is
  called.
  """
    global _manager
    with _manager_lock:
        if _manager is None:
            _manager = mp.Manager()
        return _manager
