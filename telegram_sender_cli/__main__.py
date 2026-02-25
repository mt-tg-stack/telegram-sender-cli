import asyncio
import sys

from telegram_sender_cli.app import main

try:
    asyncio.run(main())
except KeyboardInterrupt:
    sys.exit()
