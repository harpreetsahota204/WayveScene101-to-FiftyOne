import argparse
import fiftyone as fo
import fiftyone.core.storage as fos


def oss_export():
    dataset = fo.load_dataset("WayveScenes101")
    dataset.export(
        ".", 
        dataset_type=fo.types.FiftyOneDataset, 
        export_media=False)


def teams_export_to_try():
    dataset = fo.Dataset.from_dir(
        ".",
        dataset_type=fo.types.FiftyOneDataset,
        overwrite=True
    )

    dataset.name = "WayveScenes-101"

    i = 0

    batch_size = 10

    while i < len(dataset):
        print(i)
        fos.upload_media(
            dataset[i:i+batch_size], 
            "gs://voxel51-test/WayveScenes101/", 
            update_filepaths=True, 
            progress=True,
            overwrite=True
        )
        i += batch_size
    dataset.persistent = True



functions = {
    'oss_export': oss_export,
    "teams_export_to_try":teams_export_to_try
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a specific function from the command line.")
    parser.add_argument('function', choices=functions.keys(), help="The function to run")
    args = parser.parse_args()

    # Call the selected function
    functions[args.function]()