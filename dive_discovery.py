from pathlib import Path
import argparse
import pandas as pd
from tqdm.auto import tqdm

from backend import get_dive_checksum, get_dive_date

def process(data_root: Path):

    df = pd.DataFrame()

    images = data_root.rglob('*.ORF')

    dives = {img.parent.absolute() for img in images}

    dives = [dive for dive in dives if dive.name != '@eaDir']

    df['directory'] = [dive.as_posix() for dive in dives]

    df['date'] = None
    df['invalid_image'] = None
    df['multiple_date'] = None
    df['checksum'] = None

    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        path = Path(row['directory'])
        mean_date, invalid_dates, multiple_dates = get_dive_date(path)
        dive_checksum = get_dive_checksum(path)
        df.at[idx, 'date'] = mean_date
        df.at[idx, 'invalid_image'] = invalid_dates
        df.at[idx, 'multiple_date'] = multiple_dates

    df.to_csv('dives.csv')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_root', type=Path)
    args = parser.parse_args()
    process(args.data_root)

if __name__ == '__main__':
    main()