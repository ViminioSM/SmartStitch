<div align="center">
  <a href="https://github.com/MechTechnology/SmartStitch">
    <img alt="SmartStitch.Logo" width="200" height="200" src="https://github.com/MechTechnology/SmartStitch/raw/dev/assets/SmartStitchLogo.png">
  </a>
  <h1>SmartStitch</h1>
  <p>
    A small yet powerful program for stitching and cutting webtoons/manhwa/manhua raws.
  </p>
  <p>
    GUI Version supports most versions of Windows, Console Version should work on any platform with Python Installed on it.
  </p>
  <a href="https://github.com/MechTechnology/SmartStitch/releases/latest">
    <img src="https://img.shields.io/github/v/release/MechTechnology/SmartStitch">
  </a>
  <a href="https://github.com/MechTechnology/SmartStitch/releases/latest">
    <img src="https://img.shields.io/github/release-date/MechTechnology/SmartStitch">
  </a>
  <a href="https://github.com/MechTechnology/SmartStitch/releases/">
    <img src="https://img.shields.io/github/downloads/MechTechnology/SmartStitch/total">
  </a>
  <a href="https://github.com/MechTechnology/SmartStitch/tree/dev">
    <img src="https://img.shields.io/github/last-commit/MechTechnology/SmartStitch">
  </a>
  <a href="https://github.com/MechTechnology/SmartStitch/blob/dev/LICENSE">
    <img src="https://img.shields.io/github/license/MechTechnology/SmartStitch">
  </a>
  <p><strong>It's free, but any donation is appreciated</strong></p>
  <a href='https://ko-fi.com/mechtechnology' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
</div>

## What is SmartStitch?
SmartStitch is a small yet powerful tool for **stitching long webtoon / manhwa / manhua pages** and then **cutting them into panels** suitable for readers and editors.

The "smart" part comes from a pixel-based detector that tries to avoid cutting through text, SFX or important artwork. It makes life much easier for the team working on those raws – both CLRD and TS will thank you.

*It's not fancy, and does not use AI, but it's fast, robust, simple and – more importantly – it works. (So I decided to share it!)*

## Key Features (GUI)

- **Smart panel detection**
  - Combines multiple input images vertically and uses pixel comparison to choose safe cut positions.
  - Optional direct slicing mode for fixed-height panels.

- **Multi-tab GUI workflow**
  - **Basic**: input/output, file format, rough panel height.
  - **Advanced**: PSD-oriented workflows (two folders, PSD source).
  - **Detector**: tuning for detection sensitivity, scan step, margins.
  - **Profile**: save and switch between configuration profiles.
  - **Post Process**: run an external tool (e.g. waifu2x) and optionally ComicZip.

- **Advanced PSD Merge (GUI Only)**
  - **Two folders (Normal + Edited)**: merge RAW + edited pages into 2‑layer PSDs.
  - **PSD source (folder of PSDs)**: full pipeline based on PSD/PSB input, generating Edited, Original and final Merged PSD folders.

- **External post-process integration**
  - Runs any command-line tool after stitching (e.g. waifu2x, imagemagick).
  - Supports placeholders like `[stitched]` and `[processed]` in arguments.

- **ComicZip integration**
  - Optional ComicZip run to zip stitched / processed output.
  - In the Advanced PSD source workflow, ComicZip runs **only on the final [Merged] folder**.

- **Quality & format options**
  - PNG/JPG/WebP/BMP/PSD/TIFF/TGA output.
  - Lossy quality slider for JPG/WebP.
  - Width enforcement modes (none, automatic, custom).

- **Convenience features**
  - Drag‑and‑drop of folders into all input/output directory fields.
  - Multiple **profiles** for different projects / resolutions.
  - Robust logging system for easier bug reports.

The console version exposes the same core stitching/detection logic via command‑line flags, for batch or headless workflows.


## Screenshots
<div align="center">
<img alt="screenshot01" src="https://i.imgur.com/5vVFz0z.png">
<img alt="screenshot02" src="https://i.imgur.com/13ivTqN.png">
<img alt="screenshot03" src="https://i.imgur.com/PuEX3zf.png">
</div>

## Basic Quick Get Started (GUI)
1. Launch **SmartStitchGUI**.
2. In the **Basic** tab:
   - Set **Input Path** to your chapter folder.
   - The **Output Path** will auto‑fill as `Input [stitched]` (you can change it).
   - Choose **Output File Type** (png/jpg/webp/bmp/psd/tiff/tga).
   - Set **Rough Output Height** for the target panel height.
3. (Optional) In **Detector**, tune detection sensitivity / scan step / margins.
4. (Optional) In **Post Process**, configure an external tool and/or ComicZip.
5. Click **Start Process**.

- Input files are processed in the same order as your file explorer (sort by name).
- When you are comfortable with the basics, explore the **Advanced** and **Profile** tabs.

### How to launch the GUI Version (For Windows Users):
1. Put the raws you wish to stitch in a folder
2. Download the program zip file of the latest release (Found in the releases section in this github)
3. Unzip the file to a suitable place on your device.
4. Now the application will launch, and you can proceed with the Quick get started steps.

### How to launch the GUI Version (For Mac & Linux Users):
1. Download the source code zip file of the latest release (Found in the releases section in this github)
2. Unzip the file to a suitable place on your device.
3. Install python edition suitable for your machine. (Python 3.10+ is required)
4. Run the ```setup.py``` either by double clicking it or using the terminal ```python setup.py```
5. Run the ```SmartStitchGUI.py``` either by double clicking it or using the terminal: ```python SmartStitchGUI.py```
6. Now the application will launch, and you can proceed with the Quick get started steps.

Keep in mind that this setup is only needed once, after running the setup.py, you can just launch ```SmartStitchGUI.py``` directly every time

## Reporting Bugs [New to 3.0+]:
A very robust logging system has been implemented in the GUI version of SmartStitch for almost every interaction with the program, when an error occur the application will inform you about it, and leaves the details in a file called in the ```__logs__``` folder, There will be a file created for every day of usage. you can open an issue ticket here and attach the file, so it can be easily debugged and fixed.

And since it's just one person maintaining this application, only accepted tickets will be for version 3.0 and above. Please don't open tickets for lower versions, since your problem could have been already solved.

Please keep in mind that, if the issue is critical enough, it may require a copy of the raws files you used as input, but that will be for debugging special case issue, and will be requested if required.

You can also contact me at Discord if you don't want to use the GitHub Issue System. (MechTechnology#5466)

## Documentation
Here is the complete documentation for the application, it is broken down into 4 sections, basic settings, advanced settings, how to build your own version, how to run the console version.

## GUI Tabs Overview (Quick Reference)
- **Basic**
  - Input/Output folders, output file type, rough output height, width enforcement.
  - This is where most users will spend their time.

- **Advanced**
  - Advanced PSD Merge workflows:
    - **Two folders (Normal + Edited)** → merge RAW + edited images into 2‑layer PSDs.
    - **PSD source (folder of PSDs)** → run Edited / Original / Merged pipeline starting from PSD/PSB.

- **Detector**
  - Configure detection type (Smart Pixel Comparison vs Direct Slicing).
  - Sensitivity, scan line step, ignorable margins.

- **Profile**
  - Create and manage multiple named profiles.
  - Switching profile updates all GUI settings instantly.

- **Post Process**
  - Configure an external app (e.g. waifu2x) and its arguments.
  - Enable optional ComicZip run after post‑process.

## Basic Settings
These are the required settings that all users should be mindful of.

### Input Folder Path
Here you have to set the path for the Input Folder which contains the raws that will be processed by the program. If batch mode is enabled, it will search for subfolder within the given input path. So make sure your folder and files are in order.

*Console Parameter Name: --input_folder, -i*

### Output type
The default output type is png since it is lossless, however you can always change to other types, such as jpg, the program does save jpg at 100 quality, so there should be not noticeable loss in quality but it is up to the user what format they want. (You can also now use PSD files for convenience if you are a Photoshop user, however output files will not contain the layers of the original input psd file)

*Default: .png* --- *Supported Types: png, jpg, webp, bmp, psd, tiff, tga* --- *Console Parameter Name: -t*

### Rough Output Height
Here you set the size that you want most output panels to roughly be, the program will uses it as a guide to see where to slice/cut the images, however it IS ROUGH, meaning if the program finds bubbles/sfx/whatever at that specific pixel length, it will try to find the next closest position where it can cut the image. Thus the output size of each image will vary because of that, but they all will be roughly around this size.

*Default: 5000* --- *Console Parameter Name: -sh*

### Width Enforcement Mode and Custom Width
So essentially it's very straightforward. It adds a setting to select one of three modes to enforce change on the image width.
0 => No Enforcement, where you load the files as is, and work on them, if they vary in size, you will get some black lines in the side (Highest quality as there is no changes to the pixel values)
1 => Automatic uniform width, where you force all files to have the same width as the smallest file in the input folder.
2 => User Customized width, where the user specifies the width they want, that is the Custom Width parameter.
(Please just use waifu2x for upscaling raws, do not use this mode for it.)

*Default: 0* --- *Value Range: 0-2*
*Default: 720* --- *Console Parameter Name: -cw*

Console only support custom width or no enforcement

### Automaticed Batch Mode [New to 3.0+]
You can have multiple chapter folders in the input folder. The program will automatically search the nested tree, and treat every folder within the input folder as its own chapter and will work on them. It will skip folders with no images.

## Advanced Settings
These are settings for more tech savvy people, or people that find themselves in a special case that need some fine tuning of the settings.

### Detector Type
Detector type is a very simple setting, currently there is a smart pixel comparison detector which is the default way of edge detection in this program, and there is Direct Slicing, which cuts all panels to the exact size that the user inputs in the rough panel height field.

*Default: Smart Pixel Comparison, *Console Parameter Name: -dt*

### Object Detection Senstivity (Percentage)
Before slicing at a specific height, the program checks the row of pixels it will slice at if there is bubbles/sfx/whatever, it compares neighbouring pixels for any drastic jump in value, (the allowed tolarence for jumps in pixel is the Object Detection Senstivity)

if there is too big of a jump in value between the pixels, that means there is something that shouldn't be cut, so it move up a pixel row and repeat. For 100 Senstivity will mean if entire pixel row does not have the same exact pixel value/color, it will not slice at it. For 0 Senstivity being it does not care about the pixel values and will cut there, essentially turning the program into a normal Dumb Image Slicer.

*Default: 90* --- *Value Range: 0-100* --- *Console Parameter Name: -s*

### Scan Line Step
This is the step at which the program moves if it find the line it's on to be unsuitable to be sliced, meaning when it move on to the next line, it moves up/down X number of pixels to a new line, then it begins its scan algorithm once again. This X number of pixels is the scan line step. Smaller steps should give better results but larger ones do save computational power.

*Default: 5* --- *Value Range: 1-100* --- *Console Parameter Name: -sl*

### Ignorable Horizental Margins Pixels
This gives the option to ignore pixels on the border of the image when checking for bubbles/sfw/whatever. Why you might ask, Borders do not make the detection algorithm happy, so in some cases you want it to start its detection only inside said border, be careful to what value you want it to be since if it's larger that image it will case the program to crash/stop its operation.

*Default: 0* --- *Console Parameter Name: -ip*

#### Visualization of Ignorable Border Pixels and Scan Line Step
Red being the area ignored because of the Ignorable Border Pixels, and the blue lines would be the lines that application test for where it can slice (This example does not use the default values for those parameters)
<div align="center">
  <img alt="screenshot03" src="https://i.imgur.com/ipU6cJS.png">
</div>

### Settings Profile
For those working on various projects that require different stitching settings for each of them, you can now have multiple settings profile, that you can create and name as you like. Selecting the profile from dropdown will update all the programming settings to that of selected profile, this can for example be very useful when working with manhwas and manhuas of different resolutions.

This is setting is for convenience mainly for heavy users.

### Advanced PSD Merge (GUI Only)
The **Advanced** tab provides extra workflows focused on PSD-based editing, useful when you want to keep both the original RAW and an edited version together in a single PSD file.

There are currently **two source types**:

1. **Two folders (Normal + Edited)**
   - Use when you already have two folders of **final images** (any supported format) with matching filenames:
     - *Normal layer folder*: RAW or unedited pages.
     - *Edited layer folder*: cleaned/edited pages.
   - For every filename stem that exists in both folders (for example `001.png` and `001.jpg`):
     - Creates a 2-layer PSD with:
       - **"Normal"** layer at the bottom (RAW).
       - **"Edited"** layer on top.
   - The PSDs are written to the *Edited* folder (or to a custom output folder if you use the API).
   - This mode **only merges** images into PSDs; it does **not** run ComicZip or any external post-process automatically.

2. **PSD source (folder of PSDs)**
   - Use when your input is a folder of **PSD/PSB files** (each file is a page or a big canvas with layers).
   - You select a single *PSD source folder*; SmartStitch then runs a multi-step pipeline:
     1. **Edited pass** → `&lt;folder&gt; [Edited]`
        - Runs the standard stitching pipeline over the flattened PSDs.
        - Respects all the usual Basic/Detector settings and the **Run post process** checkbox.
        - If *Run post process* is enabled, your configured external tool runs on the **Edited** output.
        - ComicZip is **disabled** in this pass.
     2. **Original pass** → `&lt;folder&gt; [Original]`
        - Loads **only the first layer** of each PSD (usually the background/original art).
        - Uses the same stitching/detector configuration.
        - Post-process and ComicZip are **both disabled** here.
     3. **Merge pass** → `&lt;folder&gt; [Merged]`
        - For every matching filename, creates a 2-layer PSD in the **[Merged]** folder:
          - Bottom layer: **"Normal"** (from `[Original]`).
          - Top layer: **"Edited"** (from `[Edited]`).
        - If *Run ComicZip* is enabled, ComicZip is executed **only on the [Merged] folder**, producing the final archive.

Additional notes for the Advanced workflows:

- The Advanced pipeline can run **after** a Basic run (same session), or on its own if you only configure the Advanced tab.
- Folder fields in Basic and Advanced accept **drag-and-drop** of directories directly from your file explorer.

### Post Process
(GUI Only) With this option, one can set a specific console process to be fire on the output files of the application. For example, you can set it to fire waifu2x on the output files, so you can have the best raw processing experience. So how do we set that up,
  1. Navigate to the Post Process Tab
  3. Enable the run postprocess after completion flag.
  4. Set the process path/location, you can essentially browse to the process' exe file
  5. Set the arguments you want to pass to the process (Use the argument [stitched] to pass the output directory to your process).
  5. Optional: Use the argument [processed] to pass a custom output directory to your process for those that can't create their own output.

#### Visualization of After Completion Subprocess (Setup for waifu2x-caffe)
Of course you can use whatever version of waifu2x or process that you want, this is just an example of what i setup for myself.
<div align="center">
  <img alt="screenshot04" src="https://i.imgur.com/fZbP1sn.png">
</div>

### FAQ / Tips

- **Q: When should I use *Two folders (Normal + Edited)* vs *PSD source*?**
  - Use **Two folders** when you already exported final PNG/JPG/WebP/etc. into two folders with matching filenames:
    - One folder for RAW/unprocessed pages.
    - One folder for fully edited pages.
    - SmartStitch will only create the 2‑layer PSDs.
  - Use **PSD source (folder of PSDs)** when your source material is PSD/PSB files and you want SmartStitch to:
    - Flatten them, stitch + slice them into Edited pages.
    - Re‑run the stitch using only the first layer for Original pages.
    - Finally merge those into Merged PSDs.

- **Q: How exactly do Post Process and ComicZip interact with the Advanced PSD source mode?**
  - Edited pass (`[Edited]`):
    - **Respects** the *Run post process* checkbox.
    - **Ignores** ComicZip (always disabled here).
  - Original pass (`[Original]`):
    - **Does not run** post process.
    - **Does not run** ComicZip.
  - Merged pass (`[Merged]`):
    - **Does not run** post process.
    - **Runs ComicZip only here** if *Run ComicZip* is enabled.

- **Q: Example of waifu2x configuration?**
  - Post process application path:
    - `C:/waifu2x/waifu2x.exe`
  - Post process arguments (example):
    - `-i [stitched] -o [processed] -n 3 -s 1 -f jpg`
  - `[stitched]` is replaced by the SmartStitch output folder.
  - `[processed]` lets waifu2x write its own output in a clean separate folder.

- **Q: Can I drag & drop folders into the GUI instead of browsing every time?**
  - Yes. All folder path fields (Basic + Advanced + Post Process path) support drag‑and‑drop of directories from your file explorer.

- **Q: The window says "Not Responding" while many PSDs are being created. Is it frozen?**
  - The Advanced merge now periodically processes GUI events between PSD creations. You should still be able to move the window and see log lines while it works. If the OS temporarily shows "Not Responding" for extremely large jobs, give it a bit of time – the log and progress bar should continue updating.

## How to run the Console Version (For Windows, Mac, Linux Users)
1. Download the source code zip file of the latest release (Found in the releases section in this github)
2. Unzip the file to a suitable place on your device.
3. Install python edition suitable for your machine. (Python 3.7 is recommended)
4. Open a terminal and send the following command: pip install numpy pillow natsort
5. From the terminal, navigate to the directory where the source code was unzipped and run the command as per the usage details below

### Console Version Usage
```
python SmartStitchConsole.py [-h] -i INPUT_FOLDER
                                  -sh SPLIT_HEIGHT
                                  [-t {.png,.jpg,.webp,.bmp,.psd,.tiff,.tga}]
                                  [-cw CUSTOM_WIDTH]
                                  [-dt {none,pixel}]
                                  [-s [0-100]]
                                  [-lq [1-100]]
                                  [-ip IGNORABLE_PIXELS]
                                  [-sl [1-100]]
required arguments:
    --input_folder INPUT_FOLDER, -i INPUT_FOLDER               Sets the path of Input Folder
optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FOLDER       Sets the path of Input Folder
  -sh SPLIT_HEIGHT      Sets the value of the Rough Panel Height
  -t {.png,.jpg,.webp,.bmp,.psd,.tiff,.tga}
                        Sets the type/format of the Output Image Files
  -cw CUSTOM_WIDTH      [Advanced] Forces Fixed Width for All Output Image Files, Default=None (Disabled)
  -dt {none,pixel}      [Advanced] Sets the type of Slice Location Detection, Default=pixel (Pixel Comparison)
  -s [0-100]            [Advanced] Sets the Object Detection Senstivity Percentage, Default=90 (10 percent tolerance)
  -lq [1-100]           [Advanced] Sets the quality of lossy file types like .jpg if used, Default=100 (100 percent)
  -ip IGNORABLE_PIXELS  [Advanced] Sets the value of Ignorable Border Pixels, Default=5 (5px)
  -sl [1-100]           [Advanced] Sets the value of Scan Line Step, Default=5 (5px)
```

### Console Version Command Example
```
python SmartStitchConsole.py -i "Review me" -sh 7500 -t ".png"
# This will Run the application on for input_folder of "./Review me" with split_height of 7500 and output_type of ".png"
```

## How to build/compile your own GUI Version?

### How to compile GUI package (For Windows Users)
1. Install a Python version suitable for your machine. (Python 3.11 is recommended)
2. Upgrade pip (optional, mas recomendado):
   - ```python -m pip install --upgrade pip```
3. Install the required dependencies:
   - ```pip install -r requirements.txt```
4. From the terminal, navigate to the directory where the source code was unzipped and run:
   - ```python -m scripts.build```
5. The compiled application will be available under the ```dist/SmartStitch``` folder as ```SmartStitch.exe```.

### How to compile GUI package (For Mac & Linux Users)
1. Install a Python version suitable for your machine. (Python 3.11 is recommended)
2. Upgrade pip (optional, mas recomendado):
   - ```python -m pip install --upgrade pip``` or ```python3 -m pip install --upgrade pip```
3. Install the required dependencies:
   - ```pip install -r requirements.txt```
4. From the terminal, navigate to the directory where the source code was unzipped and run:
   - ```python -m scripts.build``` or ```python3 -m scripts.build```

- The output compiled application will not need python installed to run, but will only run on the platform it was built/compiled on.
- Mac and Linux Compiling was not tested by me, so uh... good luck xD
