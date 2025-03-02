import argparse
import contextlib
import sqlite3
from pathlib import Path

from tqdm.auto import tqdm

from backend import get_dive_checksum, get_dive_date, get_camera_sns


class Processor:
    def __init__(self, data_db: Path):
        self.__db_name = data_db
        self.__setup_tables()
        
    def load_script(self, path) -> str:
        with open(path, 'r', encoding='utf-8') as handle:
            return handle.read()

    def __setup_tables(self):
        try:
            con = sqlite3.connect(self.__db_name)
            try:
                curr = con.cursor()
                curr.executescript(self.load_script('sql/setup_tables.sql'))
                con.commit()
            finally:
                curr.close()
        finally:
            con.close()

    def run(self, data_root: Path):
        self.get_images(data_root)
        self.get_dive_dates(data_root=data_root)
        self.get_dive_checksums(data_root=data_root)
        self.extract_unique_dives()
        self.get_camera_sn(data_root=data_root)

    def get_camera_sn(self, data_root: Path):
        with contextlib.closing(sqlite3.connect(self.__db_name)) as con, \
                contextlib.closing(con.cursor()) as cur:
            cur.execute(self.load_script('sql/select_unique_dives.sql'))
            dives = [row[0] for row in cur.fetchall()]
            for dive in tqdm(dives, 'Get Camera Serial Numbers'):
                cur.execute(
                    self.load_script('sql/select_frames_from_dive.sql'),
                    {
                        'dive': dive
                    }
                )
                keys = [row[0] for row in cur.fetchall()]
                frames = [data_root / Path(key) for key in keys]
                camera_sns = get_camera_sns(frames)
                
                cur.executemany(
                    self.load_script('sql/update_camera_sn.sql'),
                    [
                        {
                            'camera_sn': camera_sns[idx],
                            'path': keys[idx]
                        }
                        for idx in range(len(keys))
                    ]
                )
                con.commit()

    def extract_unique_dives(self):
        with contextlib.closing(sqlite3.connect(self.__db_name)) as con, \
            contextlib.closing(con.cursor()) as cur:
            cur: sqlite3.Cursor
            cur.execute(self.load_script('sql/insert_unique_dives.sql'))
            con.commit()
    
    def get_images(self, data_root: Path):
        try:
            con = sqlite3.connect(self.__db_name)
            try:
                curr = con.cursor()
                images = list(data_root.rglob('*.ORF'))
                dives = list({image.parent for image in tqdm(images, 'Discovering dives')})
                dives = [dive for dive in dives if '@eaDir' not in dive.parts]
                dives = [dive for dive in dives if '.Trashes' not in dive.parts]
                for dive in tqdm(dives, 'Discovering images'):
                    images = dive.glob('*.ORF')
                    curr.execute(
                        self.load_script('sql/insert_dive_path.sql'),
                        {
                            'path': dive.relative_to(data_root).as_posix()
                        }
                    )
                    curr.executemany(
                        self.load_script('sql/insert_image_path.sql'),
                        [
                            {
                                'path': image.absolute().relative_to(data_root).as_posix(),
                                'dive': dive.relative_to(data_root).as_posix()
                            }
                            for image in images
                        ]
                    )
                    con.commit()
            finally:
                curr.close()
        finally:
            con.close()
    
    def get_dive_dates(self, data_root: Path):
        try:
            con = sqlite3.connect(self.__db_name)
            try:
                curr = con.cursor()
                curr.execute(self.load_script('sql/select_next_dive_for_date.sql'))
                rows = curr.fetchall()
                for row in tqdm(rows, 'Checking dates'):
                    path = data_root / Path(row[0])
                    mean_date, invalid_dates, multiple_dates = get_dive_date(path)
                    if mean_date is None:
                        curr.execute(
                            self.load_script('sql/drop_dive.sql'),
                            {
                                'path': path.relative_to(data_root).as_posix()
                            }
                        )
                        con.commit()
                        continue
                    curr.execute(
                        self.load_script('sql/update_dive_date.sql'),
                        {
                            'date': mean_date.isoformat(),
                            'invalid_image': invalid_dates,
                            'multiple_date': multiple_dates,
                            'path': path.relative_to(data_root).as_posix()
                        }
                    )
                    con.commit()
            finally:
                curr.close()
        finally:
            con.close()

    def get_dive_checksums(self, data_root: Path):
        try:
            con = sqlite3.connect(self.__db_name)
            try:
                curr = con.cursor()
                curr.execute(self.load_script('sql/select_next_dive_for_cksum.sql'))
                rows = curr.fetchall()
                for row in tqdm(rows, 'Computing checksums'):
                    path = data_root / Path(row[0])
                    cksum = get_dive_checksum(path)

                    curr.execute(
                        self.load_script('sql/update_dive_cksum.sql'),
                        {
                            'checksum': cksum,
                            'path': path.relative_to(data_root).as_posix()
                        }
                    )
                    con.commit()
            finally:
                curr.close()
        finally:
            con.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_root', type=Path, required=True)
    parser.add_argument('--data_db', type=Path, required=True)

    args = parser.parse_args()
    Processor(args.data_db).run(args.data_root)

if __name__ == '__main__':
    main()
