import io
import zipfile
import uuid
import os

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.config import settings
from app.schemas.screenshot import ScreenshotTask
from db.core import get_db
from db.models.screenshot import Screenshot
from app.tasks.screenshot import take_screenshots_task

app = FastAPI()


@app.get("/isalive")
async def is_alive():
    return {"status": "alive"}


@app.post("/screenshots")
async def create_screenshot_task(task: ScreenshotTask):
    unique_id = str(uuid.uuid4())
    # Send the task to Dramatiq
    take_screenshots_task.send_with_options(
        args=(task.start_url, task.number_of_links_to_follow, unique_id)
    )
    return {"unique_id": unique_id}


@app.get("/screenshots/{unique_id}")
async def get_screenshots(unique_id: str, db: AsyncSession = Depends(get_db)):
    # Query the database for screenshots associated with the unique_id
    result = await db.execute(
        select(Screenshot).where(Screenshot.unique_id == unique_id)
    )
    screenshots = result.scalars().all()

    if not screenshots:
        raise HTTPException(
            status_code=404, detail="No screenshots found with given ID"
        )

    # TODO: Limit the number of screenshots returned or implement pagination
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for screenshot in screenshots:
            zip_file.write(
                screenshot.image_path, arcname=os.path.basename(screenshot.image_path)
            )

    zip_buffer.seek(0)

    response = StreamingResponse(zip_buffer, media_type="application/zip")
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename={unique_id}_screenshots.zip"

    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
