# %%
from pathlib import Path

import pandas as pd
from tqdm.auto import tqdm

from backend import get_dive_checksum, get_dive_date

# %%
data_root = Path('//e4e-nas.ucsd.edu/fishsense_data/REEF/data')

# %%
df = pd.DataFrame()

# %%
images = data_root.rglob('*.ORF', case_sensitive=False)

# %%
dives = {img.parent.absolute() for img in images}

# %%
df['directory'] = [dive.as_posix() for dive in dives]

# %%
df['date'] = None
df['invalid_image'] = None
df['multiple_date'] = None
df['checksum'] = None

# %%
for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
    path = Path(row['directory'])
    mean_date, invalid_dates, multiple_dates = get_dive_date(path)
    dive_checksum = get_dive_checksum(path)
    df.at[idx, 'date'] = mean_date
    df.at[idx, 'invalid_image'] = invalid_dates
    df.at[idx, 'multiple_date'] = multiple_dates

# %%
df.to_csv('dives.csv')

# %%



