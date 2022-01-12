import pandas as pd
import glob

data_paths = glob.glob('./crawling/*.csv')
print(data_paths)
df = pd.DataFrame()
for data_path in data_paths:
    df_temp = pd.read_csv(data_path)
    df = pd.concat([df, df_temp])

df.dropna(inplace=True)
df.reset_index(drop=True, inplace=True)
print(df.head())
print(df.tail())
print(df['genre'].value_counts())
print(df.info())
df.to_csv('./movie_genre_concat_final.csv', index=False)

