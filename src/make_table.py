import argparse
from pathlib import Path
from random import sample
from typing import Any

import lancedb
import pandas as pd

from schema import Myntra


def create_table(
    database: str,
    table_name: str,
    data_path: str,
    schema: Any = Myntra,
    mode: str = "overwrite",
    num_samples: int = 1000,
) -> None:
    """
    Create a table in the specified vector database and add data to it.

    Args:
        database (str): The name of the database to connect to.
        table_name (str): The name of the table to create.
        data_path (str): The path to the data directory.
        schema (Schema, optional): The schema to use for the table. Defaults to Myntra.
        mode (str, optional): The mode for creating the table. Defaults to "overwrite".
        num_samples(int, optional): The number of Image samples to be added to the database.

    Returns:
        None
    """

    # Connect to the lancedb database
    db = lancedb.connect(database)

    # Check if the table already exists in the database
    if table_name in db:
        print(f"Table {table_name} already exists in the database")
        table = db[table_name]
    else:
        print(f"Creating table {table_name} in the database")
        # Create the table with the given schema
        table = db.create_table(table_name, schema=schema, mode=mode)

        # Define the Path of the images and obtain the Image uri
        p = Path(data_path).expanduser()
        uris = [str(f) for f in p.glob("*.jpg")]

        if not uris:
            print("No images found in the specified directory.")
            return

        print(f"Found {len(uris)} images in {p}")

        # Ensure num_samples is not greater than the number of images
        num_samples = min(num_samples, len(uris))

        # Sample images from the data
        uris = sample(uris, num_samples)

        # Add the data to the table
        print(f"Adding {len(uris)} images to the table")
        for uri in uris:
            try:
                table.add(pd.DataFrame({"image_uri": [uri]}))
                print(f"Added {uri} to the table")
            except OSError as e:
                print(f"Skipping {uri} due to error: {e}")
                continue

        print(f"All valid images added to the table")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a table in lancedb with Myntra data"
    )
    parser.add_argument(
        "--database", help="Path to the lancedb database", default="database"
    )
    parser.add_argument(
        "--table_name", help="Name of the table to be created", default="my_table"
    )
    parser.add_argument(
        "--data_path", help="Path to the Myntra data images", default="path/to/data"
    )
    parser.add_argument(
        "--schema",
        help="Schema to use for the table. Defaults to Myntra",
        default=Myntra,
    )
    parser.add_argument(
        "--mode",
        help="Mode for creating the table. Defaults to 'overwrite'",
        default="overwrite",
    )
    parser.add_argument(
        "--num_samples",
        help="Number of Image samples to be added to the table",
        type=int,
        default=1000,
    )
    args = parser.parse_args()

    create_table(
        args.database,
        args.table_name,
        args.data_path,
        args.schema,
        args.mode,
        args.num_samples,
    )
