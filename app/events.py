import os

from main import app
from db.core import engine


@app.on_event("startup")
async def startup_event():
    # Create local directories if they don't exist
    os.makedirs("screenshots", exist_ok=True)

    # If we have any other startup routines, we can place them here
    # For example, test a database connection
    async with engine.connect() as conn:
        await conn.run_sync(lambda x: None)  # This just ensures the connection works

    # If we are using a dependency that requires initialization, do it here
    # e.g., init_some_service()


@app.on_event("shutdown")
async def shutdown_event():
    # Close and dispose the engine on application shutdown
    await engine.dispose()
