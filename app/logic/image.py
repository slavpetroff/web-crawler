import io

from PIL import Image


def compress_image(image_path, quality=85):
    """
    Compresses the image to save disk space.
    JPEG is used here for the compression.
    """
    # Open the original image
    with Image.open(image_path) as img:
        # Define the output IO stream
        with io.BytesIO() as output:
            # Save the image as JPEG with the defined quality
            img.save(output, format="JPEG", quality=quality)
            output.seek(0)
            # Write the compressed image to disk
            with open(image_path + ".jpg", "wb") as f:
                f.write(output.read())


def decompress_image(compressed_image_path):
    """
    Decompresses the image when retrieved.
    For JPEG, decompression is simply opening the file.
    """
    with Image.open(compressed_image_path) as img:
        # Here, we simply return the image object
        # which can be used to display or convert to other formats as needed.
        return img
