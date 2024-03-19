from mllm import Chat

if __name__ == '__main__':
    chat = Chat()
    chat += "Give a json dict with keys 'a' and 'b' and values 1 and 2"
    res = chat.complete(parse="dict")
    print(res)