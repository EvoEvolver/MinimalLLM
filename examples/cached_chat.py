from mllm import Chat, caching

def get_random_number():
    chat = Chat()
    chat += "Give me a random number from 1 to 10"
    res = chat.complete()
    return res

if __name__ == '__main__':
    with caching.refresh_cache():
        num_1 = get_random_number()
    print(num_1)
    with caching.refresh_cache(on=False):
        num_1 = get_random_number()
    print(num_1)
    num_1 = get_random_number()
    print(num_1)
    caching.save()