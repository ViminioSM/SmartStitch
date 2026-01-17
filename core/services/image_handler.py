import io
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count

from PIL import Image as pil
from psd_tools import PSDImage

from ..models import WorkDirectory
from .global_logger import logFunc
from ..utils.constants import PHOTOSHOP_FILE_TYPES


# Module-level functions for multiprocessing (must be picklable)
def _load_image_worker(args: tuple) -> bytes:
    """Worker function to load a single image and return as bytes."""
    img_path, psd_first_layer_only = args
    ext = os.path.splitext(img_path)[1].lower()
    
    if ext not in PHOTOSHOP_FILE_TYPES:
        image = pil.open(img_path)
    else:
        psd = PSDImage.open(img_path)
        if psd_first_layer_only and len(psd) > 0:
            image = psd[0].topil()
        else:
            image = psd.topil()
    
    # Convert to RGB if necessary and serialize to bytes
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGB')
    
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


def _save_image_worker(args: tuple) -> str:
    """Worker function to save a single image from bytes."""
    img_bytes, full_path, img_format, quality = args
    
    image = pil.open(io.BytesIO(img_bytes))
    
    if img_format in PHOTOSHOP_FILE_TYPES:
        psd_obj = PSDImage.frompil(image)
        psd_obj.save(full_path)
    else:
        image.save(full_path, quality=quality)
    image.close()
    
    return os.path.basename(full_path)


class ImageHandler:
    def __init__(self, max_workers: int = None):
        """Initialize ImageHandler with optional max_workers for multiprocessing.
        
        If max_workers is None, uses CPU count.
        """
        self.max_workers = max_workers or cpu_count()

    @logFunc(inclass=True)
    def load(
        self,
        workdirectory: WorkDirectory,
        psd_first_layer_only: bool = False,
    ) -> list[pil.Image]:
        """Loads all image files in a given work into a list of PIL image objects.

        When *psd_first_layer_only* is True and the input file is a PSD/PSB,
        only the first layer (usually the background) is rendered instead of the
        full composited image.
        
        Uses multiprocessing for true parallel loading across CPU cores.
        """
        input_files = workdirectory.input_files
        img_paths = [
            os.path.join(workdirectory.input_path, imgFile)
            for imgFile in input_files
        ]
        
        # Prepare arguments for worker
        args_list = [(path, psd_first_layer_only) for path in img_paths]
        
        # Use ProcessPoolExecutor for true parallelism
        img_bytes_list = [None] * len(img_paths)
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(_load_image_worker, args): idx
                for idx, args in enumerate(args_list)
            }
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                img_bytes_list[idx] = future.result()
        
        # Convert bytes back to PIL Images in main process
        img_objs = [
            pil.open(io.BytesIO(img_bytes)) for img_bytes in img_bytes_list
        ]
        
        return img_objs

    @logFunc(inclass=True)
    def save(
        self,
        workdirectory: WorkDirectory,
        img_obj: pil.Image,
        img_iteration: 1,
        img_format: str = '.png',
        quality=100,
    ) -> str:
        if not os.path.exists(workdirectory.output_path):
            os.makedirs(workdirectory.output_path)
        img_file_name = str(f'{img_iteration:02}') + img_format
        full_path = os.path.join(workdirectory.output_path, img_file_name)
        
        if img_format in PHOTOSHOP_FILE_TYPES:
            psd_obj = PSDImage.frompil(img_obj)
            psd_obj.save(full_path)
        else:
            img_obj.save(full_path, quality=quality)
            img_obj.close()
        
        workdirectory.output_files.append(img_file_name)
        return img_file_name

    def save_all(
        self,
        workdirectory: WorkDirectory,
        img_objs: list[pil.Image],
        img_format: str = '.png',
        quality=100,
    ) -> WorkDirectory:
        """Save all images using multiprocessing for true parallel writes."""
        if not os.path.exists(workdirectory.output_path):
            os.makedirs(workdirectory.output_path)
        
        # Prepare file names and paths
        file_names = [
            str(f'{i+1:02}') + img_format for i in range(len(img_objs))
        ]
        full_paths = [
            os.path.join(workdirectory.output_path, fn) for fn in file_names
        ]
        
        # Serialize images to bytes for multiprocessing
        img_bytes_list = []
        for img in img_objs:
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes_list.append(buffer.getvalue())
            img.close()
        
        # Prepare arguments for workers
        args_list = [
            (img_bytes, full_path, img_format, quality)
            for img_bytes, full_path in zip(img_bytes_list, full_paths)
        ]
        
        # Use ProcessPoolExecutor for true parallelism
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(_save_image_worker, args) for args in args_list]
            for future in as_completed(futures):
                future.result()  # Raise any exceptions
        
        workdirectory.output_files.extend(file_names)
        return workdirectory
