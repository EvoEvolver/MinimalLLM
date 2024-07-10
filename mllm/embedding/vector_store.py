from __future__ import annotations

from typing import List, Callable

import numpy as np

from mllm.display.show_html import show_json_table
from mllm.embedding.get import get_embeddings
from mllm.utils.logger import Logger


class EmbedSearchLogger(Logger):
    active_loggers = []

    def display_log(self):
        contents = [log for log in self.log_list]
        filenames = [caller_name.split("/")[-1] for caller_name in self.caller_list]
        info_list = []
        for i in range(len(contents)):
            content = contents[i]
            info_list.append({
                "filename": filenames[i],
                "content": content
            })
        show_json_table(info_list)

class VectorStoreItem:
    def __init__(self, item):
        self.vectors = None
        self.srcs = []
        self.weights = []
        self.item = item

    def set_vectors(self, vector_list: List, start):
        self.vectors = np.array(vector_list[start:start + len(self.srcs)])
        return start + len(self.srcs)

    def set_single_vectors(self):
        self.vectors = np.array(get_embeddings(self.srcs))


class VectorStore:
    def __init__(self, score_function=None):
        self.stored_items = []
        self.item_to_index = {}
        if score_function is not None:
            self.score_function = score_function
        else:
            self.score_function = similarity_by_exp

    def add_item(self, item, srcs: List[str], weights: List=None):
        stored_item = VectorStoreItem(item)
        stored_item.srcs = srcs
        if weights is not None:
            stored_item.weights = weights
        else:
            stored_item.weights = np.ones(len(srcs))
        self.stored_items.append(stored_item)
        self.item_to_index[item] = len(self.stored_items) - 1

    def get_top_k_items(self, query: str | List[str], k: int = 10) -> List[str]:
        summed_similarities, items_to_search = self.get_similarities(query, log_stack=2)
        return items_to_search[:k]

    def get_similarities(self, query: str | List[str], items_to_search: List = None, log_stack=1) -> [np.ndarray, List]:
        if isinstance(query, str):
            query = [query]
        query_vecs = np.array(get_embeddings(query))


        if items_to_search is None:
            stored_items = self.stored_items
        else:
            stored_items = [self.stored_items[self.item_to_index[item]] for item in items_to_search]

        no_vector_items = [stored_item for stored_item in stored_items if stored_item.vectors is None]

        srcs = []
        for stored_item in no_vector_items:
            srcs.extend(stored_item.srcs)
        vectors = get_embeddings(srcs)
        start = 0
        for stored_item in no_vector_items:
            start = stored_item.set_vectors(vectors, start)

        inner_prod_list = []
        for stored_item in stored_items:
            inner_prod_list.append(stored_item.vectors.dot(query_vecs.T))

        scores = self.score_function(inner_prod_list)

        # Rank items
        item_rank = np.argsort(scores)[::-1]
        scores = scores[item_rank]
        stored_items = [stored_items[i] for i in item_rank]
        items = [stored_item.item for stored_item in stored_items]
        inner_prod_list = [inner_prod_list[i] for i in item_rank]

        EmbedSearchLogger.add_log_to_all(get_item_similarity_log(stored_items, inner_prod_list, query, top_k=10), stack_depth=log_stack)

        return scores, items

def get_item_similarity_log(stored_items: List[VectorStoreItem], inner_prod_list, query, top_k=10):
    contents = []
    for i, stored_item in enumerate(stored_items):
        inner_prod = inner_prod_list[i]
        max_inner_prod = np.max(inner_prod, 1)
        max_index = np.argmax(max_inner_prod)
        matched_src_inner_prod = inner_prod[max_index]
        matched_query = query[np.argmax(matched_src_inner_prod)]
        content = f"""
Item: {repr(stored_item.item)}
Max Inner Product: {max(matched_src_inner_prod)}
Matched Query: {matched_query}
Matched Src : {stored_item.srcs[max_index]}
"""
        contents.append(content)
    res = "\n".join(contents)
    return res.replace("\n", "<br/>")


def similarity_by_exp(inner_prod_list):
    a = 2.0
    b = 0.1
    # Batch normalization & Add bias
    avg_inner_prod_list = [np.average(inner_prod) for inner_prod in inner_prod_list]
    avg_inner_prod_list = np.array(avg_inner_prod_list)
    average_similarity = np.average(avg_inner_prod_list)
    # Add bias
    inner_prod_list = [inner_prod - average_similarity - b for i, inner_prod in enumerate(inner_prod_list)]
    # Add non-linearity
    inner_prod_list = [np.exp(inner_prod * a) for inner_prod in inner_prod_list]
    # get max inner product
    scores = [np.max(inner_prod) for inner_prod in inner_prod_list]
    return np.array(scores)



def get_vector_store(items: List, get_srcs: Callable[[str], List[str]]) -> VectorStore:
    vector_store = VectorStore()
    src_list = []
    item_list = []
    for i, item in enumerate(items):
        srcs = get_srcs(item)
        src_list.extend(srcs)
        item_list.extend([item] * len(srcs))
        vector_store.add_item(item, srcs)
    return vector_store


def get_vector_store_from_str(str_list: List[str]) -> VectorStore:
    return get_vector_store(str_list, lambda x: [x])