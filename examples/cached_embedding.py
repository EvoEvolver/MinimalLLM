from mllm import get_embeddings, caching

if __name__ == '__main__':
    inputs = ["1", "2", "3"]
    embeddings = get_embeddings(inputs)
    print(embeddings)
    caching.save()