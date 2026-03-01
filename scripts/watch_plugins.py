#!/usr/bin/env python3
"""
Continuous Synchronization Tool for OpenWebUI Plugins.
Monitors a local directory for changes to .py files and actively synchronizes
them to the OpenWebUI server via the `upsert_function_from_file` and `upsert_tool_from_file` methods.

Usage:
    python scripts/watch_plugins.py --dir path/to/plugins --type [functions|tools]

Dependencies:
    pip install watchdog
"""

import argparse
import asyncio
import logging
import os
import sys
import time
from typing import Optional

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    print("Error: The 'watchdog' library is required for this tool.")
    print("Please install it using: pip install watchdog")
    sys.exit(1)

from openwebui_chat_client import AsyncOpenWebUIClient, setup_logging

logger = logging.getLogger("plugin_watcher")


class PluginSyncHandler(FileSystemEventHandler):
    """Handles file system events and syncs configured plugins."""

    def __init__(self, plugin_type: str, client_config: dict):
        self.plugin_type = plugin_type
        self.client_config = client_config
        self.loop = asyncio.get_event_loop()
        self._last_sync_time = {}

    def _should_sync(self, filepath: str) -> bool:
        if not filepath.endswith(".py"):
            return False

        # Debounce rapid save events (common in IDEs)
        current_time = time.time()
        if filepath in self._last_sync_time:
            if current_time - self._last_sync_time[filepath] < 2.0:
                return False

        self._last_sync_time[filepath] = current_time
        return True

    async def _sync_file(self, event_type: str, filepath: str):
        filename = os.path.basename(filepath)
        logger.info(f"Detected {event_type} on {filename}. Syncing to server...")

        try:
            async with AsyncOpenWebUIClient(**self.client_config) as client:
                if self.plugin_type == "functions":
                    result = await client.upsert_function_from_file(filepath)
                else:
                    result = await client.upsert_tool_from_file(filepath)

                if result:
                    logger.info(
                        f"✅ Successfully synced {self.plugin_type[:-1]}: {result.get('id', 'Unknown')}"
                    )
                else:
                    logger.error(
                        f"❌ Failed to sync {self.plugin_type[:-1]}: {filename}"
                    )
        except Exception as e:
            logger.error(f"Error during synchronization of {filename}: {e}")

    def on_modified(self, event):
        if not event.is_directory and self._should_sync(event.src_path):
            asyncio.run_coroutine_threadsafe(
                self._sync_file("modification", event.src_path), self.loop
            )

    def on_created(self, event):
        if not event.is_directory and self._should_sync(event.src_path):
            asyncio.run_coroutine_threadsafe(
                self._sync_file("creation", event.src_path), self.loop
            )


async def main():
    parser = argparse.ArgumentParser(
        description="Watch and sync OpenWebUI plugins continuously."
    )
    parser.add_argument(
        "--dir", type=str, required=True, help="Directory to watch for .py files"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["functions", "tools"],
        default="functions",
        help="Type of plugins to sync",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=os.getenv("OPENWEBUI_BASE_URL", "http://localhost:8080"),
        help="OpenWebUI Base URL",
    )
    parser.add_argument(
        "--token", type=str, default=os.getenv("OPENWEBUI_TOKEN"), help="API Token"
    )

    args = parser.parse_args()

    if not args.token:
        logger.error(
            "API Token must be provided via --token or OPENWEBUI_TOKEN environment variable."
        )
        sys.exit(1)

    watch_dir = os.path.abspath(args.dir)
    if not os.path.exists(watch_dir):
        logger.error(f"Watch directory does not exist: {watch_dir}")
        sys.exit(1)

    setup_logging(level=logging.INFO)
    logger.info(f"Starting plugin watcher in: {watch_dir}")
    logger.info(f"Plugin Type: {args.type}")
    logger.info(f"Server URL: {args.url}")

    # Prepare client kwargs for the handler
    client_config = {
        "base_url": args.url,
        "token": args.token,
    }

    event_handler = PluginSyncHandler(args.type, client_config)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()

    try:
        # Keep the async loop running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
