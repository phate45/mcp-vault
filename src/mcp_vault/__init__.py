import asyncio

def main():
    """Main entry point for the package."""
    from . import server  # Lazy import - only when main() is called
    asyncio.run(server.main())

__all__ = ['main']

