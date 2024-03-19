from mllm import Chat, display_chats

if __name__ == '__main__':
    with display_chats():
        chat = Chat()
        chat += "Give me a random number from 1 to 10"
        res = chat.complete()
        print(res)

    # put something in the argument to disable the logger
    with display_chats(1):
        chat = Chat()
        chat += "Give me a random number from 1 to 10"
        res = chat.complete()
        print(res)
