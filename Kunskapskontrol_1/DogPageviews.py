#Kod som skapar databas med hundar och deras pageviews på wikipedia
import pandas as pd
import sqlite3 as sql

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
        filename=r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\dog_log.txt', 
        format='[%(asctime)s][%(levelname)s] %(message)s',
        level=logging.INFO
        )
#Läs in csv fil som är laddad ner från wikipedia wmcloud tjänst
try:
    df = pd.read_csv(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\massviews-20241208-20241215.csv')
except FileNotFoundError:
    logger.critical('File not found, check file path!')
else:
    logger.info('File read correctly')
#Skapa reference lista av hundtyper från wikipedia som vi sen använder för att filtrera första dataframe
df_breeds = pd.read_table(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\dog_list.txt', header=None)
# städning av datan
def name_strip(df):
    return df.map(lambda x: x.strip(' [1234567890]'))   
df_breeds = name_strip(df_breeds)

df_breeds = df_breeds.map(lambda x: x.strip(' [1234567890]'))
df_strip = df.replace((r"\s*\(.*\)"), "", regex=True)
# Vi kör merge igenom inner join som bara håller i genemensamma värden
df_new = df_breeds.merge(df_strip, 'inner', left_on=0, right_on='Title').drop([0], axis=1)

con = sql.connect(r'C:\Users\vidar\Documents\Skóli\TUC\Data_Science\Projects\Kunskapskontrol_1\dog_breeds_wiki.db')

try:
    df_new.to_sql('dogs_pageviews', con, if_exists='replace')
except:
    logger.warning('Database load failed, check connection')
else:
    logger.info('Database load successfull!')