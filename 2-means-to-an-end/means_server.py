"""
Implementing Protohackers 0: Smoke Test

This is basically the implementation of of RFC 862
https://www.rfc-editor.org/rfc/rfc862.html
"""

import argparse
import asyncio
import bisect
import json
import logging
import math
import re
from dataclasses import dataclass, field

logger = logging.getLogger("prime_server")

# Just some config that could be hard-coded but we won't
# The number of bytes in the message for the number formats
BYTES = 4
# The highest/lowest value for two's complement for the given number of bytes
MAXVAL = ((2**8) ** BYTES) // 2 - 1
MINVAL = -((2**8) ** BYTES) // 2


async def means_service(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Calculate them means"""
    addr = writer.get_extra_info("peername")
    client = f"{addr[0]}:{addr[1]}"
    logger.info(f"Connection from {client}")

    dataset = []
    while True:
        # Protocol uses exactly 1 type + 2x BYTES number of bytes to sed
        try:
            data = await reader.readexactly(1 + BYTES + BYTES)
        except asyncio.exceptions.IncompleteReadError:
            break

        message_type = chr(data[0])
        field1 = int.from_bytes(
            data[1 : 1 + BYTES], byteorder="big", signed=True
        )
        field2 = int.from_bytes(
            data[1 + BYTES : (1 + BYTES) + BYTES], byteorder="big", signed=True
        )

        if message_type == "I":
            bisect.insort_left(dataset, (field1, field2))
            logger.debug(f"Insert message; new dataset size: {len(dataset)}")

        if message_type == "Q":
            logger.debug(f"Query message; dataset size: {len(dataset)}")
            left_index = bisect.bisect_left(dataset, (field1, MINVAL))
            right_index = bisect.bisect_right(dataset, (field2, MAXVAL))
            running_sum = 0
            if left_index < right_index:
                entry_count = right_index - left_index
                for index in range(left_index, right_index):
                    running_sum += dataset[index][1]
                mean = int(running_sum / entry_count).to_bytes(
                    BYTES, byteorder="big", signed=True
                )
            else:
                mean = (0).to_bytes(BYTES, byteorder="big", signed=True)
            writer.write(mean)
            await writer.drain()

    writer.close()
    logger.info(f"Closed connection to {client}.")


async def main(host: str = "127.0.0.1", port: int = 9999) -> None:
    """Running the echo server."""
    logger.info(f"Starting prime server on {host}:{port}")
    server = await asyncio.start_server(means_service, host, port)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Means Server; Protohackers 2.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host value of the server. To open to the world, set it to '0.0.0.0'",
    )
    parser.add_argument(
        "--port", type=int, default=9999, help="Port to run the server on."
    )
    parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        action=argparse.BooleanOptionalAction,
        help="Run with debug log level enabled.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    asyncio.run(main(args.host, args.port))
