from __future__ import annotations

import sqlite3
import threading


class ConnPool:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn_pool = {}
        self.clock = 0
        self.max_conn = 100

    def get_conn(self):
        thread_id = threading.get_ident()
        if thread_id not in self.conn_pool:
            self.conn_pool[thread_id] = (sqlite3.connect(self.db_path, check_same_thread=False), self.clock)
            self.clock += 1
        self.remove_oldest()
        return self.conn_pool[thread_id][0]

    def remove_oldest(self):
        if len(self.conn_pool) < self.max_conn:
            return
        # find the oldest connection
        time_added_list = []
        thread_id_list = []
        for conn_id, (conn, added_time) in self.conn_pool.items():
            time_added_list.append(added_time)
            thread_id_list.append(conn_id)
        # remove the 20% oldest connections
        n_to_remove = len(self.conn_pool) // 5
        argsort = sorted(range(len(time_added_list)), key=lambda x: time_added_list[x])
        for i in range(n_to_remove):
            thread_id = thread_id_list[argsort[i]]
            self.conn_pool[thread_id][0].close()
            del self.conn_pool[thread_id]


    def close_conn(self):
        thread_id = threading.get_ident()
        if thread_id in self.conn_pool:
            self.conn_pool[thread_id][0].close()
            del self.conn_pool[thread_id]

    def close_all(self):
        for (conn, added_time) in self.conn_pool.values():
            conn.close()
        self.conn_pool = {}
