from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception

standard_multi_attempts = retry(
    wait=wait_fixed(0.5),
    stop=(stop_after_attempt(3)),
    retry=retry_if_exception(lambda e: True),
    reraise=False,
)


def test_standard_multi_attempts():
    @standard_multi_attempts
    def a():
        print("a")
        raise ValueError("a")
    a()
