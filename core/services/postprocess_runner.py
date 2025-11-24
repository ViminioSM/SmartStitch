import os
import shlex
import subprocess

from core.models.work_directory import WorkDirectory
from core.services.global_logger import logFunc


class PostProcessRunner:
    def run(self, workdirectory: WorkDirectory, **kwargs: dict[str:any]):
        app_path = kwargs.get("postprocess_app", "")
        args_str = kwargs.get("postprocess_args", "")
        console_func = kwargs.get("console_func", print)

        if not app_path:
            console_func("No post process application configured. Skipping.\n")
            return

        # Build the argument list in a robust way
        try:
            # posix=False to respect Windows paths (backslashes)
            extra_args = shlex.split(args_str, posix=False)
        except ValueError:
            # If parsing fails, fall back to passing everything as a single argument
            extra_args = [args_str] if args_str else []

        # Replace special tokens with real paths at the argument level
        resolved_args: list[str] = []
        for token in extra_args:
            # Strip surrounding quotes, in case the user typed
            # something like "C:\\path\\with spaces" in the arguments field
            if len(token) >= 2 and token[0] == token[-1] == '"':
                token = token[1:-1]

            if token == '[stitched]':
                resolved_args.append(workdirectory.output_path)
            elif token == '[processed]':
                resolved_args.append(workdirectory.postprocess_path)
            else:
                resolved_args.append(token)

        command = [app_path] + resolved_args

        # Log the full command to the GUI console
        console_func(
            "Executing post process: " + " ".join(command) + "\n"
        )

        return self.call_external_func(
            workdirectory.postprocess_path, command, console_func
        )

    @logFunc(inclass=True)
    def call_external_func(self, processed_path, command, console_func):
        if not os.path.exists(processed_path):
            os.makedirs(processed_path)
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            errors='replace',
            universal_newlines=True,
            shell=False,
        )
        console_func("Post process started!\n")
        for line in proc.stdout:
            console_func(line)
        # for line in proc.stderr:
        #   print_func(line)
        console_func("\nPost process finished successfully!\n")
        proc.stdout.close()
        return_code = proc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, command)
