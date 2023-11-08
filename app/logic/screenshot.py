import hashlib
import logging
from playwright.sync_api import sync_playwright
from sqlalchemy.orm import Session

from app.config import settings
from app.logic.image import compress_image
from db.models.screenshot import Screenshot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_LINKS_TO_FOLLOW = settings.max_links_to_follow


def calculate_checksum(image_path):
    with open(image_path, "rb") as image_file:
        file_contents = image_file.read()
        return hashlib.sha256(file_contents).hexdigest()


def add_screenshot_to_db(unique_id, image_path, file_name, image_url: str, db):
    # Adjust the image_path to point to the compressed file
    compressed_image_path = image_path + ".jpg"

    checksum = calculate_checksum(compressed_image_path)
    new_screenshot = Screenshot(
        unique_id=unique_id,
        image_path=compressed_image_path,
        checksum=checksum,
        file_name=file_name + ".jpg",
        image_url=image_url,
    )
    db.add(new_screenshot)
    db.commit()
    return new_screenshot


def take_screenshot(browser, url, path):
    try:
        page = browser.new_page()
        page.goto(url)
        page.screenshot(path=path)
        page.close()

        # Compress the image after taking the screenshot
        compress_image(path)

        # Return the new path with the compressed file extension
        return path + ".jpg"
    except Exception as e:
        logger.error(f"Error taking screenshot of {url}: {e}")
        return None


def crawl_and_screenshot(start_url, number_of_links, unique_id, db: Session):
    number_of_links = min(number_of_links, MAX_LINKS_TO_FOLLOW)
    if number_of_links < 1:
        raise ValueError(
            f"Number of links to follow must be greater than 0, got {number_of_links}"
        )

    if number_of_links > MAX_LINKS_TO_FOLLOW:
        raise ValueError(
            f"Number of links to follow must be less than {MAX_LINKS_TO_FOLLOW}, got {number_of_links}"
        )

    if not start_url.startswith("http"):
        raise ValueError(f"Start URL must start with http, got {start_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        screenshots = []
        initial_path = take_screenshot(
            browser, start_url, f"screenshots/{unique_id}_0.png"
        )
        if initial_path:
            screenshots.append(
                add_screenshot_to_db(
                    unique_id, initial_path, f"{unique_id}_0.png", start_url, db
                )
            )

        page = browser.new_page()
        page.goto(start_url)
        links = page.evaluate(
            "() => Array.from(document.querySelectorAll('a')).map(a => a.href);"
        )
        page.close()
        valid_links = list(set(filter(lambda link: link.startswith("http"), links)))
        followed_links = valid_links[:number_of_links]

        for index, url in enumerate(followed_links, start=1):
            path = f"screenshots/{unique_id}_{index}.png"
            screenshot = take_screenshot(browser, url, path)
            if screenshot:
                screenshots.append(
                    add_screenshot_to_db(
                        unique_id, screenshot, f"{unique_id}_{index}.png", url, db
                    )
                )

        browser.close()
        return [s.image_path for s in screenshots if s is not None]
