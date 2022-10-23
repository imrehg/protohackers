"""
Implementing Protohackers 0: Smoke Test

This is basically the implementation of of RFC 862
https://www.rfc-editor.org/rfc/rfc862.html
"""

import argparse
import asyncio
import json
import logging
import math
import re
from dataclasses import dataclass
from inspect import Attribute

logger = logging.getLogger("prime_server")


def is_prime(number: int | float) -> bool:
    """Checking a number whether they are prime."""
    # Change every float into integer types if possible
    if not isinstance(number, int) and number.is_integer():
        number = int(number)

    # Prime checking
    result = True
    if isinstance(number, int) and number >= 2:
        for i in range(2, math.floor(math.sqrt(number)) + 1):
            if number % i == 0:
                result = False
                break
    else:
        # Non-integers, 1, and negative numebers are all non-primes
        result = False
    return result


# Could do some of these better with pydantic.validate_arguments
# https://pydantic-docs.helpmanual.io/usage/validation_decorator/
def parse_prime_request(data: str) -> int | None:
    """Parse the prime request data"""
    try:
        request = json.loads(data)
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        return None

    if (
        "method" not in request
        or request["method"] != "isPrime"
        or "number" not in request
        or not isinstance(request["number"], int | float)
        or isinstance(
            request["number"], bool
        )  # booleans also evaluates as int so need special treatment
    ):
        return None

    return request["number"]


async def prime_service(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Do them echo for a given stream"""
    while True:
        # Read data all the way to EOF
        data = await reader.readline()

        # A but of logging
        addr = writer.get_extra_info("peername")
        client = f"{addr[0]}:{addr[1]}"
        logger.debug(
            f"Received message from {client} with length {len(data)}."
        )

        logger.debug(f"{client}: Request: {data}")
        number = parse_prime_request(data)
        malformed = number is None
        if not malformed:
            print(f">>>>> {data} -> {number}")
            result = {"method": "isPrime", "prime": is_prime(number)}
        else:
            result = {"method": "isPrimeQuestion", "prime": "who knows?"}
        logger.debug(f"{client}: Response: {result}")

        response = (json.dumps(result) + "\n").encode("ASCII")
        # Send the same data back
        writer.write(response)
        await writer.drain()

        if malformed:
            break

    writer.close()
    logger.debug(f"Closed connection to {client}.")


async def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Running the echo server."""
    logger.info(f"Starting prime server on {host}:{port}")
    server = await asyncio.start_server(prime_service, host, port)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prime Server; Protohackers 1.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host value of the server. To open to the world, set it to '0.0.0.0'",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to run the server on."
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Run with debug log level enabled.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    asyncio.run(main(args.host, args.port))
