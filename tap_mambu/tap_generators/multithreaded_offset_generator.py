import json
import time
from copy import deepcopy
from threading import Thread

import backoff
from singer import get_logger

from .generator import TapGenerator
from ..helpers import transform_json, transform_datetime
from ..helpers.multithreaded_requests import MultithreadedRequestsPool
from ..helpers.perf_metrics import PerformanceMetrics

LOGGER = get_logger()


class MultithreadedOffsetGenerator(TapGenerator):
    def _init_params(self):
        self.time_extracted = None
        self.static_params = dict(self.endpoint_params)
        self.offset = 0
        self.overlap_window = 20
        self.artificial_limit = self.client.page_size
        self.limit = self.client.page_size + self.overlap_window
        self.batch_limit = 10000
        self.params = self.static_params

    def _init_config(self):
        super(MultithreadedOffsetGenerator, self)._init_config()
        self.end_of_file = False
        self.fetch_batch_thread = None
        self.last_batch_set = set()

    def error_check_and_fix(self, a, b):
        reunion = a | b
        if len(reunion) == len(a) + len(b):
            raise RuntimeError("Failed to error correct, aborting job.")
        if len(a) + self.artificial_limit < len(reunion) < len(a) + len(b):
            LOGGER.warning("Error checking returned errors, but they will be corrected!")
        return reunion

    @staticmethod
    def stop_all_request_threads(futures):
        for future in futures:
            future.cancel()

        for future in futures:
            while not future.done():  # Both finished and cancelled futures return 'done'
                time.sleep(0.1)

    def fetch_batch_continuously(self):
        while not self.end_of_file:
            if not self._all_fetch_batch_steps():
                self.end_of_file = True
            time.sleep(0.1)

    @backoff.on_exception(backoff.expo, RuntimeError, max_tries=5)
    def _all_fetch_batch_steps(self):
        # prepare batches (with self.limit for each of them until we reach batch_limit)
        futures = list()
        while len(self.buffer) + len(futures) * self.limit <= self.batch_limit:
            self.prepare_batch()
            # send batches to multithreaded_requests_pool
            futures.append(MultithreadedRequestsPool.queue_request(self.client, self.stream_name,
                                                                   self.endpoint_path, self.endpoint_api_method,
                                                                   self.endpoint_api_version,
                                                                   self.endpoint_api_key_type,
                                                                   deepcopy(self.endpoint_body),
                                                                   deepcopy(self.params)))
            self.offset += self.artificial_limit
        # wait for responses, and check them for errors
        last_batch = set()
        final_buffer = self.last_batch_set
        stop_iteration = False
        for future in futures:
            while not future.done():
                time.sleep(0.1)

            result = future.result()

            transformed_batch = self.transform_batch(transform_json(result, self.stream_name))
            temp_buffer = set([json.dumps(record, ensure_ascii=False).encode("utf8") for record in transformed_batch])

            if not temp_buffer:  # We finished the data to extract, time to stop
                self.stop_all_request_threads(futures)
                stop_iteration = True
                break

            last_batch = temp_buffer

            if not final_buffer:
                final_buffer = final_buffer | temp_buffer
                continue

            try:
                final_buffer = self.error_check_and_fix(final_buffer, temp_buffer)
            except RuntimeError:  # if errors are found
                LOGGER.exception("Discrepancies found in extracted data, and errors couldn't be corrected."
                                 "Cleaning up...")

                # wait all threads to finish/cancel all threads
                self.stop_all_request_threads(futures)
                LOGGER.info("Cleanup complete! Retrying extraction from last bookmark...")
                # retry the whole process (using backoff decorator, so we need to propagate the exception)
                # effectively rerunning this function with the same parameters
                raise

            if stop_iteration:
                break
        
        final_buffer -= self.last_batch_set
        self.last_batch_set = last_batch
        # if no errors found:
        # dump data into buffer
        for raw_record in final_buffer:
            record = json.loads(raw_record.decode("utf8"))
            self.buffer.append(record)

        self.last_batch_size = len(self.last_batch_set)
        if not final_buffer or stop_iteration:
            return False
        return True

    def __iter__(self):
        if self.fetch_batch_thread is None:
            self.fetch_batch_thread = Thread(target=self.fetch_batch_continuously, name="FetchContinuouslyThread")
            self.fetch_batch_thread.start()
        return self

    def next(self):
        if not self.buffer and not self.end_of_file:
            with PerformanceMetrics(metric_name="processor_wait"):
                while not self.buffer and not self.end_of_file:
                    time.sleep(0.01)
        if not self.buffer and self.end_of_file:
            raise StopIteration()
        return self.buffer.pop(0)

    def fetch_batch(self):
        raise DeprecationWarning("Function is being deprecated, and not implemented in this subclass!")