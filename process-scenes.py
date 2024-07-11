import argparse
import os
from multiprocessing import Pool, cpu_count
import subprocess

import open3d as o3d
import fiftyone as fo

def images_to_video(image_folder: str, output_video_path: str, fps: int = 10) -> None:
    """
    Convert a folder of images to a video.

    Args:
        image_folder (str): Path to the folder containing images.
        output_video_path (str): Path where the output video will be saved.
        fps (int, optional): Frames per second for the output video. Defaults to 10.
    """
    try:
        command = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-framerate', str(fps),
            '-pattern_type', 'glob',
            '-i', f'{image_folder}/*.jpeg',  # Adjust this if your images are not .png
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',  # Adjust for quality vs file size
            output_video_path
        ]
        
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        return False

def run_colmap_converter(scene_path: str):
    """
    Run COLMAP model converter on a given scene path and convert the result to PCD format.

    Args:
        scene_path (str): Path to the scene directory.

    Returns:
        str: Path to the output PCD file, or None if an error occurred.
    """
    input_path = os.path.join(scene_path, 'colmap_sparse', 'rig')
    ply_output_path = os.path.join(scene_path, 'model.ply')
    
    # Get the name of the subdirectory
    subdirectory_name = os.path.basename(scene_path)
    pcd_output_path = os.path.join(scene_path, f'{subdirectory_name}.pcd')
    
    command = [
        'colmap', 'model_converter',
        '--input_path', input_path,
        '--output_path', ply_output_path,
        '--output_type', 'PLY'
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"Successfully processed {scene_path} to PLY")

        pcd = o3d.io.read_point_cloud(ply_output_path)
        o3d.io.write_point_cloud(pcd_output_path, pcd)
        print(f"Successfully converted PLY to PCD for {scene_path}")

        os.remove(ply_output_path)
        print(f"Removed intermediate PLY file for {scene_path}")

        return pcd_output_path

    except subprocess.CalledProcessError as e:
        print(f"Error processing {scene_path} with COLMAP: {e}")
    except Exception as e:
        print(f"Error converting PLY to PCD for {scene_path}: {e}")
    
    return None

def create_fiftyone_scene(pcd_path: str):
    """
    Create a FiftyOne scene for a given PCD file.

    Args:
        pcd_path (str): Path to the PCD file.

    Returns:
        str: Path to the output .fo3d file, or None if an error occurred.
    """
    try:
        scene = fo.Scene()
        
        # Get the subdirectory name
        subdirectory_name = os.path.basename(os.path.dirname(pcd_path))
        
        pcd_sample = fo.PointCloud(
            name=subdirectory_name,
            pcd_path=pcd_path,
        )

        scene.add(pcd_sample)

        # Use the subdirectory name for the .fo3d file
        fo3d_output_path = os.path.join(os.path.dirname(pcd_path), f'{subdirectory_name}.fo3d')
        scene.write(fo3d_output_path)
        print(f"Created FiftyOne scene for {pcd_path}")

        return fo3d_output_path

    except Exception as e:
        print(f"Error creating FiftyOne scene for {pcd_path}: {e}")
    
    return None

def process_scene(scene_path: str):
    """
    Process a single scene: create videos, run COLMAP converter, and create FiftyOne scene.

    Args:
        scene_path (str): Path to the scene directory.

    Returns:
        tuple: (list of video paths, path to .fo3d file)
    """
    print(f"Processing {os.path.basename(scene_path)}...")
    
    video_paths = []
    images_dir = os.path.join(scene_path, "images")
    
    # Process videos
    if os.path.exists(images_dir):
        for view_folder in os.listdir(images_dir):
            view_path = os.path.join(images_dir, view_folder)
            if os.path.isdir(view_path):
                video_name = f"{os.path.basename(scene_path)}_{view_folder}.mp4"
                video_path = os.path.join(scene_path, video_name)
                success = images_to_video(view_path, video_path)
                if success:
                    video_paths.append(video_path)
                    print(f"Created video: {video_path}")
                else:
                    print(f"Failed to create video for {view_folder}")
    else:
        print(f"No images directory found in {scene_path}")

    # Process 3D data
    pcd_path = run_colmap_converter(scene_path)
    if not pcd_path:
        print(f"Failed to create PCD file for {os.path.basename(scene_path)}")
        return video_paths, None

    fo3d_path = create_fiftyone_scene(pcd_path)
    if not fo3d_path:
        print(f"Failed to create .fo3d file for {os.path.basename(scene_path)}")
        return video_paths, None

    print(f"Successfully created .fo3d file: {fo3d_path}")
    return video_paths, fo3d_path

def process_all_scenes_parallel(base_dir: str):
    """
    Process all scenes in the base directory in parallel.

    Args:
        base_dir (str): Path to the base directory containing all scenes.

    Returns:
        tuple: (list of all video paths, list of all .fo3d file paths)
    """
    scene_paths = [
        os.path.join(base_dir, scene_dir)
        for scene_dir in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, scene_dir)) and scene_dir.startswith('scene_')
    ]

    # Use all available CPU cores, but leave one free for system processes
    num_processes = max(1, cpu_count() - 1)
    print(f"Processing {len(scene_paths)} scenes using {num_processes} processes...")

    with Pool(processes=num_processes) as pool:
        results = pool.map(process_scene, scene_paths)

    all_video_paths = []
    all_fo3d_paths = []
    for video_paths, fo3d_path in results:
        all_video_paths.extend(video_paths)
        if fo3d_path:
            all_fo3d_paths.append(fo3d_path)

    return all_video_paths, all_fo3d_paths

def get_scene_paths(data_dir: str) -> list:
    """
    Get a list of all scene paths in the data directory.

    Args:
        data_dir (str): Path to the base directory containing all scenes.

    Returns:
        list: List of paths to all scene directories.
    """
    return [
        os.path.join(data_dir, scene_dir)
        for scene_dir in os.listdir(data_dir)
        if os.path.isdir(os.path.join(data_dir, scene_dir)) and scene_dir.startswith('scene_')
    ]

def main(data_dir: str, process_type: str):
    """
    Main function to run the specified process on the data directory.

    Args:
        data_dir (str): Path to the base directory containing all scenes.
        process_type (str): Type of process to run ('all', 'videos', 'colmap', or 'fiftyone').
    """
    scene_paths = get_scene_paths(data_dir)
    
    if process_type == 'all':
        video_paths, fo3d_paths = process_all_scenes_parallel(data_dir)
        print("All scenes processed.")
        print(f"Total videos created: {len(video_paths)}")
        print(f"Total .fo3d files created: {len(fo3d_paths)}")
    elif process_type == 'videos':
        for scene_path in scene_paths:
            images_dir = os.path.join(scene_path, "images")
            if os.path.exists(images_dir):
                for view_folder in os.listdir(images_dir):
                    view_path = os.path.join(images_dir, view_folder)
                    if os.path.isdir(view_path):
                        video_name = f"{os.path.basename(scene_path)}_{view_folder}.mp4"
                        video_path = os.path.join(scene_path, video_name)
                        success = images_to_video(view_path, video_path)
                        if success:
                            print(f"Created video: {video_path}")
                        else:
                            print(f"Failed to create video for {view_folder}")
    elif process_type == 'colmap':
        for scene_path in scene_paths:
            pcd_path = run_colmap_converter(scene_path)
            if pcd_path:
                print(f"Created PCD file: {pcd_path}")
            else:
                print(f"Failed to create PCD file for {os.path.basename(scene_path)}")
    elif process_type == 'fiftyone':
        for scene_path in scene_paths:
            pcd_path = os.path.join(scene_path, f"{os.path.basename(scene_path)}.pcd")
            if os.path.exists(pcd_path):
                fo3d_path = create_fiftyone_scene(pcd_path)
                if fo3d_path:
                    print(f"Created .fo3d file: {fo3d_path}")
                else:
                    print(f"Failed to create .fo3d file for {os.path.basename(scene_path)}")
            else:
                print(f"PCD file not found for {os.path.basename(scene_path)}")
    else:
        print(f"Invalid process type: {process_type}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process scenes in the dataset.")
    parser.add_argument("--data_dir", type=str, default='/Users/harpreetsahota/workspace/datasets/wayve_101/',
                        help="Path to the base directory containing all scenes.")
    parser.add_argument("--process", type=str, choices=['all', 'videos', 'colmap', 'fiftyone'],
                        default='all', help="Type of process to run.")

    args = parser.parse_args()

    main(args.data_dir, args.process)
