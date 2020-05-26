# python >= 3.6
import os
import sys
import faulthandler
import collections
import multiprocessing as mp
import threading
import signal
import time
import queue
import json
import traceback


# _ProcessStatusInfo contains process status information
_ProcessStatusInfo = collections.namedtuple('_ProcessStatusInfo',
        ['is_successful'])
_SubprocessInfo = collections.namedtuple('_SubprocessInfo', ['pid'])

_DEFAULT_TIMEOUT_SEC = 200


class MultiProcessRunner(object):
    '''
    A utility class to start multiple processes to simulate a cluster

    simple version from tensorflow/python/distribute/multi_process_runner.py
    It can run any where, but the tensorflow version only run in unittest.
    '''

    def __init__(self,
            proc_func,
            cluster_spec,
            max_run_time_sec=None,
            stream_stdout=True,
            list_stdout=False,
            gpu_devices=None,
            args=None,
            kwargs=None):
        '''
        Args:
            proc_func: Function to be run on child processes. This will be
                run on processes for all task types.
            cluster_spec: Dict for cluster spec.
            max_run_time_sec: If set, child processes is forced to exit at
                approximately this many seconds after `start` is called.
            stream_stdout: True if the output/error from the subprocesses
                should be streamed to be printed in parent process' log.
            list_stdout: if True, return the output/error as list
            gpu_devices: str, default None, use task id as gpu, e.g. '0,1'
        '''
        assert callable(proc_func)
        assert cluster_spec is not None and isinstance(cluster_spec, dict)
        self.proc_func = proc_func
        self.cluster_spec = cluster_spec
        self.max_run_time_sec = max_run_time_sec
        self.stream_stdout = stream_stdout
        self.list_stdout = list_stdout
        self.gpu_devices = gpu_devices
        self.args = args or ()
        self.kwargs = kwargs or {}

        self.outstanding_subprocess_count = 0
        self.all_forced_terminated = False
        self.terminate_thread_pipes = []

        self.ctx = mp.get_context('fork')
        self.process_status_queue = self.ctx.Queue()
        self.subprocess_info_queue = self.ctx.Queue()
        self.streaming_queue = self.ctx.Queue()

    def start(self):
        has_chief = 'chief' in self.cluster_spec
        for task_type, addresses in self.cluster_spec.items():
            for task_id, _ in enumerate(addresses):
                self._start_subprocess(task_type, task_id, has_chief)

        if self.max_run_time_sec is not None:
            def handler(signum, frame):
                del signum, frame
                self.terminate_all()

            signal.signal(signal.SIGALRM, handler)
            signal.alarm(self.max_run_time_sec)

    def join(self, timeout=_DEFAULT_TIMEOUT_SEC):
        if not timeout:
            timeout = float('inf')
        start_time = time.time()
        while self.outstanding_subprocess_count > 0:
            while True:
                try:
                    ps = self.process_status_queue.get(timeout=10)
                    break
                except queue.Empty:
                    if self.all_forced_terminated:
                        break
                    if time.time() - start_time > timeout:
                        self.terminate_all(signal.SIGTERM)
                        raise RuntimeError(
                                'One or more subprocesses timed out, '
                                f'{self.outstanding_subprocess_count}')
            if self.all_forced_terminated:
                break
            self.outstanding_subprocess_count -= 1
            assert isinstance(ps, _ProcessStatusInfo)
            if not ps.is_successful:
                # wait other subprocesses fail
                time.sleep(3)
                self.terminate_all(signal.SIGTERM)
                raise RuntimeError(f'{ps.task_type}-{ps.task_id} '
                        'raise an error')
        time.sleep(3)
        # read all the stream queue
        ret_list = []
        while True:
            try:
                ret_list.append(self.streaming_queue.get(False))
            except queue.Empty:
                break
        self.terminate_threads()
        return ret_list

    def terminate_threads(self):
        for pp in self.terminate_thread_pipes:
            try:
                writer = os.fdopen(pp.fileno(), 'w')
                writer.writelines(['EOF'])
                pp.close()
            except:
                pass

    def terminate_all(self, sig=None):
        sig = sig or getattr(signal, 'SIGKILL', signal.SIGTERM)
        subprocess_infos = []
        while True:
            try:
                si = self.subprocess_info_queue.get(False)
                subprocess_infos.append(si)
            except queue.Empty:
                break

        self.terminate_threads()
        for si in subprocess_infos:
            print(f'kill child process {si.pid}')
            os.kill(si.pid, sig)
        self.all_forced_terminated = True

    def _start_subprocess(self, task_type, task_id, has_chief):
        # use pipe to collect std stream
        pipe_r, pipe_w = self.ctx.Pipe(False) # unidirectional pipe
        self.terminate_thread_pipes.append(pipe_w)
        p = self.ctx.Process(target=self._process_target,
                args=(pipe_w, task_type, task_id, has_chief))
        p.start()
        self.outstanding_subprocess_count += 1

        # no task type and id in pipe
        t = threading.Thread(target=self._thread_target,
                args=(pipe_r, task_type, task_id))
        t.start()

    def _thread_target(self, pipe_r, task_type, task_id):
        task = f'[{task_type}-{task_id}]'.ljust(10)
        reader = os.fdopen(pipe_r.fileno(), 'r')
        while True:
            line = reader.readline()
            if not line or line == 'EOF':
                pipe_r.close()
                break
            formatted_line = f'{task} {line}'
            if self.stream_stdout:
                print(formatted_line, end='', flush=True)
            if self.list_stdout:
                self.streaming_queue.put(formatted_line)

    def _process_target(self, pipe_w, task_type, task_id, has_chief):
        faulthandler.enable()
        faulthandler.register(signal.SIGTERM, chain=True)
        pid = os.getpid()
        self.subprocess_info_queue.put(_SubprocessInfo(pid))
        # Assign sys.stdout and sys.stderr as duplicates of `pipe_w`
        # so print() and logging.*() write directly to `pipe_w`.
        os.dup2(pipe_w.fileno(), sys.stdout.fileno())
        os.dup2(pipe_w.fileno(), sys.stderr.fileno())
        tf_config = {'cluster': self.cluster_spec,
                'task': {'type': task_type, 'index': task_id}}
        os.environ['TF_CONFIG'] = json.dumps(tf_config)
        if 'ps' == task_type:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        else:
            tid = task_id + 1 if has_chief and task_type=='worker' else task_id
            gpus = self.gpu_devices or tid
            os.environ['CUDA_VISIBLE_DEVICES'] = str(gpus)
        try:
            self.proc_func(*self.args, **self.kwargs) # ignore return
            is_successful = True
        except:
            is_successful = False
        finally:
            signal.alarm(0)
            self.process_status_queue.put(_ProcessStatusInfo(
                is_successful=is_successful))

def run(proc_func,
        cluster_spec,
        max_run_time_sec=None,
        stream_stdout=True,
        list_stdout=False,
        gpu_devices=None,
        timeout=_DEFAULT_TIMEOUT_SEC,
        args=None,
        kwargs=None):
    runner = MultiProcessRunner(
            proc_func,
            cluster_spec,
            max_run_time_sec=max_run_time_sec,
            stream_stdout=stream_stdout,
            list_stdout=list_stdout,
            gpu_devices=gpu_devices,
            args=args,
            kwargs=kwargs)
    runner.start()
    return runner.join(timeout)
