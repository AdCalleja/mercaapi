import asyncio
import os
import requests
import tempfile
from pathlib import Path

import click
from loguru import logger
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from app.database import get_engine
from app.parser import parse_mercadona
from app.models import Product, NutritionalInformation, is_food_category
from app.ai.ticket import AIInformationExtractor
# TODO: Implement or import the estimate_nutritional_info function
# from app.ai.nutrition_estimator import estimate_nutritional_info


@click.group()
def cli():
    pass


@cli.command()
@click.option("--max-requests", default=5, help="Maximum requests per minute")
@click.option("--update-existing", is_flag=True, help="Update existing products")
def parse(max_requests, update_existing=False):
    """Parse products from Mercadona API."""
    logger.info("Starting the Mercadona parser")
    engine = get_engine()
    asyncio.run(
        parse_mercadona(
            engine, max_requests, skip_existing_products=not update_existing
        )
    )
    logger.info("Parsing completed")


def clean_numeric(value):
    if isinstance(value, str):
        cleaned = "".join(char for char in value if char.isdigit() or char == ".")
        return float(cleaned) if cleaned else None
    return value



NUTRITION_PROMPT = """
    Extract all nutritional information from this image.    
    Provide the output as a JSON object with the following structure:
    {
        "calories": number,
        "total_fat": number,
        "saturated_fat": number,
        "polyunsaturated_fat": number,
        "monounsaturated_fat": number,
        "trans_fat": number,
        "total_carbohydrate": number,
        "dietary_fiber": number,
        "total_sugars": number,
        "protein": number,
        "salt": number
    }
    Use null for any values not present in the image.
    Ensure all numeric values are numbers, not strings.
    """

def download_image(image_url: str) -> str:
    """Download image from URL and save to temporary file, returning the file path"""
    logger.debug(f"Downloading image from {image_url}")
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(
            f"Failed to download image. Status code: {response.status_code}"
        )
    
    # Create a temporary file with the correct extension
    suffix = ".jpg"  # Default to jpg
    content_type = response.headers.get("Content-Type", "")
    if "png" in content_type.lower():
        suffix = ".png"
    
    # Save the image to a temporary file
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    try:
        with os.fdopen(fd, 'wb') as temp_file:
            temp_file.write(response.content)
        return temp_path
    except Exception as e:
        os.unlink(temp_path)  # Clean up on error
        raise e

@cli.command()
@click.option(
    "--reprocess-all",
    is_flag=True,
    help="Reprocess all products with missing or null calorie information",
)
def process_nutritional_information(reprocess_all):
    logger.info("Processing nutritional information for products")
    api_key = os.environ.get("GEMINI_API_KEY")
    assert api_key, "Please set the GEMINI_API_KEY environment variable"
    nutrition_extractor = AIInformationExtractor(groq_api_key=None, gemini_api_key=api_key, gemini_model="gemini-2.0-flash-lite")

    # Create an event loop for running async functions
    loop = asyncio.get_event_loop()

    engine = get_engine()
    with Session(engine) as session:
        query = select(Product).options(
            joinedload(Product.category), joinedload(Product.images)
        )
        if not reprocess_all:
            query = query.where(Product.nutritional_information == None)  # noqa: E711
        else:
            query = query.outerjoin(NutritionalInformation).where(
                (NutritionalInformation.id == None)  # noqa: E711
                | (NutritionalInformation.calories == None)  # noqa: E711
            )

        products = session.exec(query).unique()

        for product in products:
            if product.category and is_food_category(product.category):
                logger.info(f"Processing product '{product.name}' ({product.id})")
                nutritional_info = None

                if product.images:
                    for image in reversed(product.images):
                        try:
                            # Download image to temporary file
                            image_path = download_image(image.zoom_url)
                            # Use run_until_complete to properly await the async function
                            try:
                                nutritional_info = loop.run_until_complete(
                                    nutrition_extractor.process_file_nutrition(
                                        image_path, NUTRITION_PROMPT
                                    )
                                )
                                if (
                                    nutritional_info is not None
                                    and nutritional_info.calories is not None
                                ):
                                    break
                            finally:
                                # Clean up the temporary file
                                try:
                                    os.unlink(image_path)
                                except Exception as cleanup_error:
                                    logger.warning(f"Failed to clean up temporary file {image_path}: {cleanup_error}")
                        except Exception as e:
                            logger.error(
                                f"Error processing image for product {product.id}: {str(e)}"
                            )

                if (
                    nutritional_info is None
                    or nutritional_info.calories is None
                ):
                    logger.warning(
                        f"No nutritional information found in images for product {product.id}. Estimating using LLM."
                    )
                    # # Check if estimate_nutritional_info is imported or defined
                    # try:
                    #     nutritional_info = estimate_nutritional_info(product)
                    # except NameError:
                    #     logger.error(f"Function estimate_nutritional_info is not defined. Skipping estimation.")
                    #     nutritional_info = None

                if nutritional_info:
                    nutritional_info.calories = nutritional_info.calories
                    cleaned_info = {
                        key: clean_numeric(getattr(nutritional_info, key))
                        for key in nutritional_info.model_fields
                    }

                    existing_info = product.nutritional_information
                    if existing_info:
                        for key, value in cleaned_info.items():
                            setattr(existing_info, key, value)
                    else:
                        db_nutritional_info = NutritionalInformation(
                            product_id=product.id, **cleaned_info
                        )
                        session.add(db_nutritional_info)

                    session.commit()
                    logger.info(
                        f"Added/Updated nutritional information for product {product.id}"
                    )
            else:
                logger.warning(
                    f"Skipping product '{product.name}' ({product.id}), not a food product."
                )

    logger.info("Nutritional information processing completed")


if __name__ == "__main__":
    cli()
