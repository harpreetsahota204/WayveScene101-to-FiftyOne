import cv2
import os
import subprocess
import open3d as o3d
import fiftyone as fo
from multiprocessing import Pool, cpu_count

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
    pcd_output_path = os.path.join(scene_path, 'model.pcd')
    
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
        
        pcd_sample = fo.PointCloud(
            name=os.path.basename(os.path.dirname(pcd_path)),
            pcd_path=pcd_path,
        )

        scene.add(pcd_sample)

        fo3d_output_path = os.path.join(os.path.dirname(pcd_path), 'scene.fo3d')
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

# Main execution
if __name__ == "__main__":
    DATA_DIR = '/Users/harpreetsahota/workspace/datasets/wayve_101/scene_062'
    video_paths, fo3d_paths = process_all_scenes_parallel(DATA_DIR)

    print("All scenes processed.")
    print(f"Total videos created: {len(video_paths)}")
    print(f"Total .fo3d files created: {len(fo3d_paths)}")
    
