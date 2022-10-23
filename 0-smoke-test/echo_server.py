"""
Implementing Protohackers 0: Smoke Test

This is basically the implementation of of RFC 862
https://www.rfc-editor.org/rfc/rfc862.html
"""

import argparse
import asyncio
import logging

logger = logging.getLogger("echo_server")


async def echo(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Do them echo for a given stream"""
    # Read data all the way to EOF
    data = await reader.read(n=-1)

    # A but of logging
    addr = writer.get_extra_info("peername")
    client = f"{addr[0]}:{addr[1]}"
    logger.debug(f"Received message from {client} with length {len(data)}.")

    # Send the same data back
    writer.write(data)
    await writer.drain()

    writer.close()
    logger.debug(f"Closed connection to {client}.")


async def main(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Running the echo server."""
    logger.info(f"Starting server on {host}:{port}")
    server = await asyncio.start_server(echo, host, port)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Echo Server as per RFC862; Protohackers 0.",
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
