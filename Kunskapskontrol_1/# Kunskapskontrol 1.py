# Kunskapskontrol 1
import pandas as pd
import sqlite3 as sql
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
        filename=r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\log.txt', 
        format='[%(asctime)s][%(levelname)s] %(message)s',
        level=logging.INFO
        )
# Läsa in csv från SCB, passa på att specifiera encoding som cp1252 annars får man inte svenska bokstaver
try:
    df1 = pd.read_csv(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\000007N5_20241217-094027.csv', encoding='cp1252')
    df2 = pd.read_csv(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\000003PS_20241217-093537.csv', encoding='cp1252')
except FileNotFoundError:
    logger.warning(f'File Not Found, check file path!')
else:
    logger.info(f'CSV file was read')
# rensa df1, droppa 2 kolumner som vi inte behöver samt alla nullvärde i den kolumnen vi håller i.
# SCB använder ".." som nullvärde så pandas .dropna kommer inte funka
df1 = df1.drop(
    ['typ av konsekvens','2023'], axis=1
    ).loc[df1['2021']!='..']
# i csv'en är siffrorna klassifierade som textsträngar så vi måste omvändla til int
df1['2021'] = df1['2021'].astype(int)
# Vi är egentligen bara intresserad av total incidenter
df1 = df1.groupby('redovisningsgrupp').sum()
# SCB använder ibland inte samma exakta namn för regionerna så vi får döpa om värden i första dataframe så de matchar namnen i den andra
def fix_regions(*dfs):
    for df in dfs:
        df.rename(
            index={'Stockholms län': 'Stockholm',
                   'Norra mellansverige':'Norra Mellansverige',
                   'Östra mellansverige':'Östra Mellansverige'},
            inplace=True
            )

fix_regions(df1, df2)
  
# För df2 kan vi droppa den kolumnen eftersom den bara har värdet "Totalt" i alla rader
df2.drop(['typ av IT-tjänst'], axis=1, inplace=True)
# Vi kör merge, som tar liknande argument som SQL join, och skapar df3
df3 = df1.merge(df2, 'left', right_on='redovisningsgrupp', left_on='redovisningsgrupp')

df3.rename(
    columns={'redovisningsgrupp':'Region',
             '2021_x':'Incidenter 2021',
             '2021_y':'Utgifter för IT tjänster 2021'},
    inplace=True
    )

con = sql.connect(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\kunskapskontrol1.db')

try:
    df3.to_sql('data om it-utgifter och incidenter', con, if_exists='replace')
except:
    logger.debug(f'Loading to DB failed')
else:
    logger.info(f'Loading to DB successfull')