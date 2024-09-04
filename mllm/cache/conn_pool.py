from __future__ import annotations

import sqlite3
import threading


class ConnPool:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn_pool = {}
        self.threads = {}
        self.max_conn = 50
        self.lock_for_closing = threading.Lock()

    def get_conn(self):
        current_thread = threading.current_thread()
        thread_id = current_thread.ident
        conn = self.conn_pool.get(thread_id)
        if conn is not None:
            return conn
        # wait for the lock
        with self.lock_for_closing:
            # Add a new connection if the thread does not have one
            if thread_id not in self.conn_pool:
                self.conn_pool[thread_id] = sqlite3.connect(self.db_path, check_same_thread=False)
                self.threads[thread_id] = current_thread
            if len(self.conn_pool) >= self.max_conn:
                # remove the connections that is not running
                for tid in list(self.threads.keys()):
                    if not self.threads[tid].is_alive():
                        del self.conn_pool[tid]
                        del self.threads[tid]
            return self.conn_pool[thread_id]

    def close_conn(self):
        with self.lock_for_closing:
            thread_id = threading.get_ident()
            if thread_id in self.conn_pool:
                self.conn_pool[thread_id].close()
                del self.conn_pool[thread_id]
                del self.threads[thread_id]

    def close_all(self):
        with self.lock_for_closing:
            for conn in self.conn_pool.values():
                conn.close()
            self.conn_pool = {}
            self.threads = {}
