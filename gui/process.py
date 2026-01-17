import gc
import os
from time import time

from core.detectors import select_detector
from core.services import (
    DirectoryExplorer,
    ImageHandler,
    ImageManipulator,
    PostProcessRunner,
    SettingsHandler,
    logFunc,
)


class GuiStitchProcess:
    @logFunc(inclass=True)
    def run_with_error_msgs(self, **kwargs: dict[str:any]):
        status_func = kwargs.get("status_func", print)
        try:
            return self.run(**kwargs)
        except Exception as error:
            status_func(0, "Idle - {0}".format(str(error)))
            raise error

    def run(self, **kwargs: dict[str:any]):
        # Initialize Services
        settings = SettingsHandler()
        explorer = DirectoryExplorer()
        img_handler = ImageHandler()
        img_manipulator = ImageManipulator()
        postprocess_runner = PostProcessRunner()
        detector = select_detector(detection_type=settings.load("detector_type"))
        project_root = os.path.dirname(os.path.dirname(__file__))
        comiczip_script = os.path.join(project_root, "scripts", "comiczip.py")
        input_path = kwargs.get("input_path", "")
        output_path = kwargs.get("output_path", "")
        postprocess_path = kwargs.get("postprocess_path", "")
        psd_first_layer_only = kwargs.get("psd_first_layer_only", False)
        disable_postprocess = kwargs.get("disable_postprocess", False)
        disable_comiczip = kwargs.get("disable_comiczip", False)
        status_func = kwargs.get("status_func", print)
        console_func = kwargs.get("console_func", print)
        step_percentages = {
            "explore": 5.0,
            "load": 15.0,
            "combine": 5.0,
            "detect": 15.0,
            "slice": 10.0,
            "save": 30.0,
            "postprocess": 20.0,
        }
        has_postprocess = settings.load("run_postprocess") and not disable_postprocess
        run_comiczip = settings.load("run_comiczip") and not disable_comiczip
        if not has_postprocess:
            step_percentages["save"] = 50.0

        # Starting Stitch Process
        start_time = time()
        percentage = 0.0
        status_func(percentage, 'Exploring input directory for working directories')

        # Respect a custom output_path when provided; otherwise fall back
        # to the default behavior in DirectoryExplorer (input + suffix).
        explorer_kwargs: dict[str, str] = {}
        if output_path:
            explorer_kwargs["output"] = output_path
        if postprocess_path:
            explorer_kwargs["postprocess"] = postprocess_path

        input_dirs = explorer.run(input=input_path, **explorer_kwargs)
        input_dirs_count = len(input_dirs)
        status_func(
            percentage,
            'Working - [{count}] Working directories were found'.format(
                count=input_dirs_count
            ),
        )
        percentage += step_percentages.get("explore")
        dir_iteration = 1
        for dir in input_dirs:
            status_func(
                percentage,
                'Working - [{iteration}/{count}] Preparing & loading images Into memory'.format(
                    iteration=dir_iteration, count=input_dirs_count
                ),
            )
            imgs = img_handler.load(dir, psd_first_layer_only=psd_first_layer_only)
            imgs = img_manipulator.resize(
                imgs, settings.load("enforce_type"), settings.load("enforce_width")
            )
            percentage += step_percentages.get("load") / float(input_dirs_count)
            status_func(
                percentage,
                'Working - [{iteration}/{count}] Combining images into a single combined image'.format(
                    iteration=dir_iteration, count=input_dirs_count
                ),
            )
            combined_img = img_manipulator.combine(imgs)
            percentage += step_percentages.get("combine") / float(input_dirs_count)
            status_func(
                percentage,
                'Working - [{iteration}/{count}] Detecting & selecting valid slicing points'.format(
                    iteration=dir_iteration, count=input_dirs_count
                ),
            )
            slice_points = detector.run(
                combined_img,
                settings.load("split_height"),
                sensitivity=settings.load("senstivity"),
                ignorable_pixels=settings.load("ignorable_pixels"),
                scan_step=settings.load("scan_step"),
            )
            percentage += step_percentages.get("detect") / float(input_dirs_count)
            status_func(
                percentage,
                'Working - [{iteration}/{count}] Generating sliced output images in memory'.format(
                    iteration=dir_iteration, count=input_dirs_count
                ),
            )
            imgs = img_manipulator.slice(combined_img, slice_points)
            percentage += step_percentages.get("slice") / float(input_dirs_count)
            status_func(
                percentage,
                'Working - [{iteration}/{count}] Saving output images to storage (parallel)'.format(
                    iteration=dir_iteration, count=input_dirs_count
                ),
            )
            img_count = len(imgs)
            # Use parallel save_all for better performance
            img_handler.save_all(
                dir,
                imgs,
                img_format=settings.load("output_type"),
                quality=settings.load("lossy_quality"),
            )
            percentage += step_percentages.get("save") / float(input_dirs_count)
            status_func(
                percentage,
                'Working - [{iteration}/{count}] {count_imgs} images saved successfully'.format(
                    iteration=dir_iteration,
                    count=input_dirs_count,
                    count_imgs=img_count,
                ),
            )
            gc.collect()
            if has_postprocess:
                status_func(
                    percentage,
                    'Working - [{iteration}/{count}] Running post process on output files'.format(
                        iteration=dir_iteration,
                        count=input_dirs_count,
                    ),
                )
                postprocess_runner.run(
                    workdirectory=dir,
                    postprocess_app=settings.load("postprocess_app"),
                    postprocess_args=settings.load("postprocess_args"),
                    console_func=console_func,
                )
                percentage += step_percentages.get("postprocess") / float(input_dirs_count)
            if run_comiczip:
                status_func(
                    percentage,
                    'Working - [{iteration}/{count}] Running ComicZip on output files'.format(
                        iteration=dir_iteration,
                        count=input_dirs_count,
                    ),
                )
                postprocess_runner.run(
                    workdirectory=dir,
                    postprocess_app="python",
                    postprocess_args=f"{comiczip_script} -i [stitched] -o [processed]",
                    console_func=console_func,
                )
            dir_iteration += 1
        end_time = time()
        percentage = 100
        status_func(
            percentage,
            'Idle - Process completed in {time:.3f} seconds'.format(
                time=end_time - start_time
            ),
        )
