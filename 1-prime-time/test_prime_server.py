import prime_server
import pytest


@pytest.mark.parametrize(
    "test_input,expected_output",
    [
        (-10, False),
        (1, False),
        (2, True),
        (3, True),
        (4, False),
        (19, True),
        (21, False),
        (1001, False),
        (7919, True),
        (115248, False),
        (115249, True),
        (2.5, False),
        (7919.0, True),
    ],
)
def test_prime_check(test_input: int, expected_output: bool):
    assert prime_server.is_prime(test_input) == expected_output


@pytest.mark.parametrize(
    "test_input,expected_output",
    [
        ('{"method":"isPrime", "number": 2}\n', 2),
        ('{"method":"isPrime", "number": "two"}\n', None),
        ('{"method":"isPrime",', None),
        ('{"method":"is-it-prime?", "number": 2}\n', None),
        ('{"methodology":"isPrime", "number": 2}\n', None),
        ('{"method":"isPrime", "numero": 2}\n', None),
        ('{"method":"isPrime","number":true}\n', None),
        ('{"method":"isPrime","number": 15, "foo": "bar"}\n', 15),
    ],
)
def test_prime_request(test_input: str, expected_output: int | None):
    assert prime_server.parse_prime_request(test_input) == expected_output
