import asyncio

import nest_asyncio
from IPython.terminal.embed import InteractiveShellEmbed
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from traitlets.config import Config

from apps.example.models import *
from apps.example.repositories.somemodel_repo import *
from apps.example.services.core_service import *

# App-specific imports (services, models, etc.)
from config.settings import get_settings

# ---------------------------
# Async setup
# ---------------------------

# Load app settings (e.g. DB URL, debug mode)
settings = get_settings()

# Create async engine for SQLModel
async_engine = create_async_engine(
    url=str(settings.ASYNC_SQLITE_URI),
    echo=settings.DEBUG,
    poolclass=NullPool,
)

# Async session factory (like Django’s connection/session)
async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Patch the event loop so we can re-enter it (IPython already has one running)
nest_asyncio.apply()

# ---------------------------
# IPython shell logic
# ---------------------------

# Shell banner message
banner = """
🚀 FastAPI Shell — SQLModel (async)
Available:
- session              : active AsyncSession
- async_session        : session factory (for manual `async with`)
- Imported all models/services from apps.example.*
"""


# Async entrypoint — ensures session context is active throughout shell
async def start_shell():
    async with async_session() as session:
        # Configure IPython shell with autoawait and asyncio loop
        config = Config()
        config.TerminalInteractiveShell.autoawait = True
        config.TerminalInteractiveShell.loop_runner = "asyncio"

        shell = InteractiveShellEmbed(config=config, banner1=banner)

        # Start IPython with a preloaded namespace
        shell(
            user_ns={
                "session": session,
                "async_session": async_session,
                # Add common service classes or helpers here if desired
            }
        )


# Synchronous entrypoint for poetry/CLI
def main():
    asyncio.run(start_shell())


# Run the shell
if __name__ == "__main__":
    main()
