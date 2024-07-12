# WayveScene101-to-FiftyOne

The WayveScenes101 Dataset is a collection of high-resolution images and camera poses designed to advance research in novel view synthesis and scene reconstruction for autonomous driving applications. Key features of the dataset include[1]:

- 101 diverse driving scenarios, each 20 seconds long
- 101,000 total images (101 scenes x 5 cameras x 20 seconds x 10 frames per second)
- Scenes recorded in the US and UK
- 5 time-synchronized cameras with a separate held-out evaluation camera
- Scene-level attributes for detailed model evaluation
- Integration with the NerfStudio framework

The dataset captures a wide range of conditions, such as different weather, road types, times of day, dynamic agents, and illumination changes[1]. 

The dataset is available for download on Google Drive, and the repository provides tutorials for dataset usage and evaluating novel view synthesis models. The package is currently only supported on Linux and requires Anaconda or Miniconda for environment setup[1].

Binary masks are provided for all images to indicate anonymized regions like license plates, faces, and visible parts of the ego-vehicle. Camera calibration information is included in COLMAP files and a JSON file[1].

Citations:
[1] https://github.com/wayveai/wayve_scenes

# Installation note

You must have COLMAP installed, follow the instructions [here](https://colmap.github.io/install.html). If you're running on a Mac you need to have the several dependencies installed. Look at the file `install-dependencies.sh` to see what needs to be installed. Or blindly run it if you want.

# Downloading data
The script for downloading data is in the `download-data.sh` script. If you encounter any error unzipping, just unzip manually. I'm sure you can figure that out. 

You also need to download the metadata for each scene, which you get via: `wget https://raw.githubusercontent.com/wayveai/wayve_scenes/main/data/scene_metadata.csv`

## Installation

1. Clone this repository:

```bash
git clone https://github.com/harpreetsahota204/WayveScene101-to-FiftyOne.git
cd WayveScene101-to-FiftyOne
pip install -r requirements.txt
```

# WayveScenes101 Dataset Processing

This repository contains scripts to process the WayveScenes101 dataset, a collection of driving scenes designed for autonomous driving research. The scripts allow you to convert image sequences to videos, run the COLMAP converter to generate 3D point clouds, and create FiftyOne scenes for visualization and analysis.


The main script is `process_scenes.py`. You can run it with the following command:

```bash
python process_scenes.py --data_dir /path/to/wayve_101 --process [all|videos|colmap|fiftyone]
```

- `--data_dir`: Path to the base directory containing all scenes.
- `--process`: Type of process to run:
  - `all`: Run all processes (videos, COLMAP, and FiftyOne).
  - `videos`: Only convert image sequences to videos.
  - `colmap`: Only run the COLMAP converter to generate point clouds.
  - `fiftyone`: Only create FiftyOne scenes from existing point clouds.

For example, to process all scenes in the dataset located at `/path/to/wayve_101` and run all processes, use:

```bash
python process_scenes.py --data_dir /path/to/wayve_101 --process all
```

The script will process each scene directory (named `scene_*`) in the provided data directory. It will create videos from the image sequences, run the COLMAP converter to generate point clouds, and create FiftyOne scenes for visualization and analysis.

## Output

The script will generate the following output files in each scene directory:

- `*.mp4`: Video files for each camera view.
- `*.pcd`: Point cloud data in the PCD format.
- `*.fo3d`: FiftyOne scene files for visualization and analysis.


# Creating FiftyOne dataset

## Output

The script will create a FiftyOne dataset with the specified `DATASET_NAME` in the current directory. Each sample in the dataset will contain the following fields:

- `weather`
- `time_of_day`
- `same_direction_traffic`
- `road_type`
- `oncoming_traffic`
- `cross_vehicle_traffic`
- `ped_crossing`
- `ped_on_sidewalk`
- `bike_present`
- `large_exposure_change`
- `traffic_light_change`
- `changing_brake_light_indicator`

Additionally, each sample will have a group field `group` with a default value of `"front_forward"`.

## License

This project is licensed under the [Creative Commons License](LICENSE).

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.
