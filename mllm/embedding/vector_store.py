from typing import List, Callable

import numpy as np

from mllm.debug.show_table import show_json_table
from mllm.embedding.get import get_embeddings
from mllm.debug.logger import Logger


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


class VectorStore:
    def __init__(self, similarity_function=None):
        self.vectors = []
        self.srcs = []
        self.weights = []
        self.items_to_index = {}
        self._vectors = None
        self.removed_items = set()
        if similarity_function is not None:
            self.similarity_function = similarity_function
        else:
            self.similarity_function = similarity_by_exp

    def add_vecs(self, vecs: List, items: List, weights: List = None):
        assert len(vecs) == len(items)
        original_len = len(self.items_to_index)
        self.vectors.extend(vecs)
        if weights is None:
            weights = np.ones(len(vecs))
        self.weights.extend(weights)
        for item in items:
            assert item not in self.items_to_index
        for i, item in enumerate(items):
            index_start = i + original_len
            if item not in self.items_to_index:
                self.items_to_index[item] = [index_start, index_start + 1]
            else:
                self.items_to_index[item][1] = index_start + 1
        self._vectors = None

    def remove_items(self, items: List):
        self.removed_items.update(items)
        if len(items) > len(self.items_to_index) / 3:
            self.flush_removed_indices()

    def flush_removed_indices(self):
        removed_indices = []
        for item in self.removed_items:
            if item in self.items_to_index:
                removed_indices.extend(range(*self.items_to_index[item]))
                del self.items_to_index[item]
        new_vectors = []
        new_items_to_index = {}
        new_weights = []
        new_srcs = []
        for item in self.items_to_index.keys():
            indices_tuple = self.items_to_index[item]
            vectors_for_item = self.vectors[indices_tuple[0]:indices_tuple[1]]
            new_items_to_index[item] = [len(new_vectors),
                                        len(new_vectors) + len(vectors_for_item)]
            new_vectors.extend(vectors_for_item)
            new_weights.extend(self.weights[indices_tuple[0]:indices_tuple[1]])
        self.weights = new_weights
        self.vectors = new_vectors
        self.items_to_index = new_items_to_index
        self._vectors = None


    def get_top_k_items(self, query: str | List[str], k: int = 10) -> List[str]:
        summed_similarities, items_to_search = self.get_similarities(query)
        return items_to_search[:k]

    def get_similarities(self, query: str | List[str], items_to_search: List = None) -> [np.ndarray, List]:
        if isinstance(query, str):
            query = [query]
        vec = get_embeddings(query)
        vec = np.array(vec)

        if self._vectors is None:
            self._vectors = np.array(self.vectors)
        if items_to_search is None:
            items_to_search = list(self.items_to_index.keys())
        item_indices = []
        remaining_items = []
        for item in items_to_search:
            if item in self.removed_items:
                continue
            vec_index_tuple = self.items_to_index.get(item, None)
            if vec_index_tuple is None:
                continue
            item_indices.extend(range(*vec_index_tuple))
            remaining_items.append(item)

        items_to_search = remaining_items

        # Decide the order of filtering by the number of items
        if len(items_to_search) > len(self.items_to_index) / 2:
            flatten_inner_prod = (self._vectors.dot(vec.T))[item_indices]
        else:
            flatten_inner_prod = self._vectors[item_indices].dot(vec)

        summed_similarities = self.similarity_function(self, flatten_inner_prod, item_indices, items_to_search)

        # Rank items
        item_rank = np.argsort(summed_similarities)[::-1]
        summed_similarities = summed_similarities[item_rank]
        items_to_search = [items_to_search[i] for i in item_rank]

        top_k = 10
        EmbedSearchLogger.add_log_to_all(get_item_similarity_log(self, flatten_inner_prod, items_to_search[:top_k], query))

        return summed_similarities, items_to_search

def get_item_similarity_log(vector_store: VectorStore, flatten_inner_prod, items, query):
    contents = []
    for item in items:
        vec_index_tuple = vector_store.items_to_index[item]
        inner_prod_list = flatten_inner_prod[vec_index_tuple[0]:vec_index_tuple[1]]
        max_inner_prod_list = np.max(inner_prod_list, 1)
        max_index = np.argmax(max_inner_prod_list)
        matched_src_inner_prod = inner_prod_list[max_index]
        matched_query = query[np.argmax(matched_src_inner_prod)]
        content = f"""
Item: {repr(item)}
Max Inner Product: {max(matched_src_inner_prod)}
Matched Query: {matched_query}
"""
        contents.append(content)
    res = "\n".join(contents)
    return res.replace("\n", "<br/>")


def similarity_by_exp(vector_store, flatten_inner_prod, item_indices, items_to_search):
    a = 2.0
    b = 0.1
    # Batch normalization & Add bias
    average_similarity = np.average(flatten_inner_prod)
    flatten_inner_prod = flatten_inner_prod - average_similarity - b
    # Add non-linearity
    flatten_inner_prod = np.exp(flatten_inner_prod * a)
    # Apply weights
    flatten_inner_prod = flatten_inner_prod.T * np.array(vector_store.weights)[item_indices]
    flatten_inner_prod = np.sum(flatten_inner_prod, axis=0)
    # Sum by node
    summed_similarities = np.zeros(len(items_to_search))
    for i in range(len(items_to_search)):
        vec_index_tuple = vector_store.items_to_index[items_to_search[i]]
        n_vecs = vec_index_tuple[1] - vec_index_tuple[0]
        summed_similarities[i] = np.sum(
            flatten_inner_prod[vec_index_tuple[0]:vec_index_tuple[1]]) / (n_vecs ** 0.5)
    return summed_similarities



def get_vector_store(items: List, get_srcs: Callable[[str], List[str]]) -> VectorStore:
    vector_store = VectorStore()
    src_list = []
    item_list = []
    for i, item in enumerate(items):
        srcs = get_srcs(item)
        src_list.extend(srcs)
        item_list.extend([item] * len(srcs))
    embeddings = get_embeddings(src_list)
    vector_store.add_vecs(embeddings, item_list)
    return vector_store


def get_vector_store_from_str(str_list: List[str]) -> VectorStore:
    return get_vector_store(str_list, lambda x: [x])