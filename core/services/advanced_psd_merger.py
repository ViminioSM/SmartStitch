import os
from typing import Callable

from PIL import Image as pil
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

from core.utils.constants import SUPPORTED_IMG_TYPES


ConsoleFunc = Callable[[str], None]


YieldFunc = Callable[[], None] | None


class AdvancedPsdMerger:
    """Merge pairs of images (normal + edited) into 2-layer PSD files."""

    def __init__(self, console_func: ConsoleFunc | None = None) -> None:
        self.console = console_func or print

    def _log(self, message: str) -> None:
        self.console(message + "\n")

    def merge_folders_to_psd(
        self,
        normal_dir: str,
        edited_dir: str,
        output_dir: str | None = None,
        yield_func: YieldFunc = None,
    ) -> int:
        """Create PSDs from images with the same filename in two folders.

        For each file name present in both folders, this loads the normal image
        as the base layer and the edited image as the top layer, then writes a
        2-layer PSD into the *edited* folder using the common file stem.
        """
        if not os.path.isdir(normal_dir) or not os.path.isdir(edited_dir):
            raise ValueError("Both normal and edited folders must exist.")

        # Build maps from filename stem (without extension) to full filename,
        # filtering only supported image types. This allows matching
        # `001.png` with `001.jpg`, for example.
        def build_stem_map(directory: str) -> dict[str, str]:
            stem_map: dict[str, str] = {}
            for name in os.listdir(directory):
                full_path = os.path.join(directory, name)
                if not os.path.isfile(full_path):
                    continue
                _stem, ext = os.path.splitext(name)
                if ext.lower() not in SUPPORTED_IMG_TYPES:
                    continue
                if _stem in stem_map:
                    # Ambiguous; skip duplicate stems.
                    self._log(
                        f"[Advanced] Duplicate stem '{_stem}' in '{directory}', skipping this entry."
                    )
                    continue
                stem_map[_stem] = name
            return stem_map

        normal_map = build_stem_map(normal_dir)
        edited_map = build_stem_map(edited_dir)

        common_stems = sorted(normal_map.keys() & edited_map.keys())
        if not common_stems:
            self._log("[Advanced] No matching files found between the two folders.")
            self._log(
                f"[Advanced] Normal stems: {sorted(normal_map.keys())}"
            )
            self._log(
                f"[Advanced] Edited stems: {sorted(edited_map.keys())}"
            )
            return 0

        self._log(f"[Advanced] Found {len(common_stems)} matching file(s) by stem.")

        # Determine target root for PSD output.
        target_root = output_dir if output_dir else edited_dir
        if not os.path.isdir(target_root):
            os.makedirs(target_root, exist_ok=True)

        created = 0
        for stem in common_stems:
            normal_name = normal_map[stem]
            edited_name = edited_map[stem]
            normal_path = os.path.join(normal_dir, normal_name)
            edited_path = os.path.join(edited_dir, edited_name)

            try:
                base_img = pil.open(normal_path).convert("RGBA")
                edited_img = pil.open(edited_path).convert("RGBA")
            except Exception as exc:  # Pillow/IO errors
                self._log(
                    f"[Advanced] Skipping stem '{stem}' ({normal_name} / {edited_name}): {exc!r}"
                )
                continue

            # Ensure both layers have the same size.
            if edited_img.size != base_img.size:
                edited_img = edited_img.resize(base_img.size, pil.LANCZOS)

            # Create an empty PSD document using the base image to define
            # canvas size, then add two explicit layers: Normal (RAW) and
            # Edited (RD).
            psd = PSDImage.frompil(base_img)

            # Ensure we always have two real layers in the final PSD.
            normal_layer = PixelLayer.frompil(
                base_img,
                psd,
                name="Normal",
            )
            edited_layer = PixelLayer.frompil(
                edited_img,
                psd,
                name="Edited",
            )

            # Order: Normal at the bottom, Edited on top.
            psd.append(normal_layer)
            psd.append(edited_layer)

            output_path = os.path.join(target_root, f"{stem}.psd")

            try:
                psd.save(output_path)
                created += 1
                self._log(f"[Advanced] Created PSD: {output_path}")
            except Exception as exc:  # PSD save errors
                self._log(
                    f"[Advanced] Failed to save PSD for stem '{stem}' ({normal_name} / {edited_name}): {exc!r}"
                )

            # Close images to free resources.
            base_img.close()
            edited_img.close()

            # Allow callers (such as the GUI) to process events between
            # PSD creations, preventing the window from appearing
            # unresponsive during long merges.
            if yield_func is not None:
                try:
                    yield_func()
                except Exception:
                    # Guard against unexpected errors in the callback so
                    # that the merge itself is not interrupted.
                    pass

        self._log(f"[Advanced] Finished. Created {created} PSD file(s).")
        return created
