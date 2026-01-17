import io
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count

from PIL import Image as pil

from ..utils.constants import WIDTH_ENFORCEMENT
from .global_logger import logFunc


# Module-level function for multiprocessing (must be picklable)
def _resize_image_worker(args: tuple) -> bytes:
    """Worker function to resize a single image and return as bytes."""
    img_bytes, new_img_width = args
    
    img = pil.open(io.BytesIO(img_bytes))
    
    if img.size[0] != new_img_width:
        img_ratio = float(img.size[1] / img.size[0])
        new_img_height = int(img_ratio * new_img_width)
        if new_img_height > 0:
            img = img.resize((new_img_width, new_img_height), pil.LANCZOS)
    
    # Serialize back to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img.close()
    return buffer.getvalue()


class ImageManipulator:
    def __init__(self, max_workers: int = None):
        """Initialize ImageManipulator with optional max_workers for multiprocessing.
        
        If max_workers is None, uses CPU count.
        """
        self.max_workers = max_workers or cpu_count()

    @logFunc(inclass=True)
    def resize(
        self,
        img_objs: list[pil.Image],
        enforce_setting: WIDTH_ENFORCEMENT,
        custom_width: int = 720,
    ) -> list[pil.Image]:
        """Resizes all given images according to the set enforcement setting.
        
        Uses multiprocessing for true parallel resizing across CPU cores.
        """
        if enforce_setting == WIDTH_ENFORCEMENT.NONE:
            return img_objs
        
        # Determine target width
        new_img_width = 0
        if enforce_setting == WIDTH_ENFORCEMENT.AUTOMATIC:
            widths, heights = zip(*(img.size for img in img_objs))
            new_img_width = min(widths)
        elif enforce_setting == WIDTH_ENFORCEMENT.MANUAL:
            new_img_width = custom_width
        
        # Serialize images to bytes for multiprocessing
        img_bytes_list = []
        for img in img_objs:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes_list.append(buffer.getvalue())
            img.close()
        
        # Prepare arguments for workers
        args_list = [(img_bytes, new_img_width) for img_bytes in img_bytes_list]
        
        # Use ProcessPoolExecutor for true parallelism
        resized_bytes = [None] * len(img_objs)
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(_resize_image_worker, args): idx
                for idx, args in enumerate(args_list)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                resized_bytes[idx] = future.result()
        
        # Convert bytes back to PIL Images
        resized_imgs = [
            pil.open(io.BytesIO(img_bytes)) for img_bytes in resized_bytes
        ]
        
        return resized_imgs

    @logFunc(inclass=True)
    def combine(self, img_objs: list[pil.Image]) -> pil.Image:
        """Combines given image objs to a single vertically stacked single image obj."""
        widths, heights = zip(*(img.size for img in img_objs))
        combined_img_width = max(widths)
        combined_img_height = sum(heights)
        combined_img = pil.new('RGB', (combined_img_width, combined_img_height))
        combine_offset = 0
        for img in img_objs:
            combined_img.paste(img, (0, combine_offset))
            combine_offset += img.size[1]
            img.close()
        return combined_img

    @logFunc(inclass=True)
    def slice(
        self, combined_img: pil.Image, slice_locations: list[int]
    ) -> list[pil.Image]:
        """Combines given combined img to into multiple img slices given the slice locations."""
        max_width = combined_img.size[0]
        img_objs = []
        for index in range(1, len(slice_locations)):
            upper_limit = slice_locations[index - 1]
            lower_limit = slice_locations[index]
            slice_boundaries = (0, upper_limit, max_width, lower_limit)
            img_slice = combined_img.crop(slice_boundaries)
            img_objs.append(img_slice)
        combined_img.close()
        return img_objs
