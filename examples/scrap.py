import pandas as pd
from openfigipy import OpenFigiClient


ofc = OpenFigiClient()
ofc.connect()

fmp = FMPClient()
fmp.connect()

df = fmp.get_symbol_list()
ref = fmp.get_profile(df['symbol'])
refdf = pd.DataFrame(ref)

refdf['exch_suff'] = refdf['symbol'].str.split('.').str[1]




isin_only = refdf.loc[
        ((~refdf['isin'].isna()) & (refdf['isin']!='')) |
        ((~refdf['cusip'].isna()) & (refdf['cusip']!=''))].copy()

isin_only.loc[isin_only['isin']=='', 'isin'] = np.nan
isin_only.loc[isin_only['cusip']=='', 'cusip'] = np.nan

isin_only = isin_only[['symbol', 'isin', 'currency', 'cusip', 'isActivelyTrading']]


isin_only['idType'] = 'ID_ISIN'
isin_only.loc[isin_only['isin'].isna(), 'idType'] = 'ID_CUSIP'
isin_only['isin'] = isin_only['isin'].fillna(isin_only['cusip'])

isin_only['marketSecDes'] = 'Equity'
isin_only['includeUnlistedEquities'] = False
isin_only.loc[isin_only['isActivelyTrading']==False, 'includeUnlistedEquities'] = True

isin_only = isin_only.rename(columns={'isin': 'idValue'})
isin_only = isin_only.drop(columns=['cusip'])


res = ofc.map(isin_only[['idType', 'idValue', 'currency', 'marketSecDes', 'includeUnlistedEquities']])

res['prim_sc'] = False
res.loc[res['figi']==res['compositeFIGI'], 'prim_sc'] = True


exchs = refdf[['exchange', 'exchangeShortName']].copy()

exchs = exchs.drop_duplicates()

bbg_e = ofc.get_mapping_enums('exchCode')

mlist = list(mappings.values())

for e in mlist:
    if e not in bbg_e:
        print(e)

mappings = {np.nan: 'US',
         'PA': 'FP',
         'AS': 'NA',
         'BR': 'BB',
         'LS': 'PL',
         'TO': 'CN',
         'SW': 'SW',
         'DE': 'GR',
         'ME': 'RU',
         'NS': 'IN',
         'L':  'LN',
         '':   'LN',
         'A':  'LN',
         'HK': 'HK',
         'OL': 'NO',
         'SA': 'BZ',
         'F':  'GR',
         'V':  'CN',
         'SI': 'SP',
         'MC': 'SM',
         'CN': 'CN',
         'NZ': 'NZ',
         'SZ': 'CH',
         'KS': 'KS',
         'KQ': 'KS',
         'TW': 'TW',
         'T':  'JP',
         'SS': 'CH',
         'CO': 'DC',
         'JO': 'SJ',
         'IS': 'TI',
         'VI': 'AV',
         'HE': 'FH',
         'ST': 'SS',
         'MI': 'IM',
         'AT': 'GA',
         'MX': 'MM',
         'HM': 'GR',
         'SN': 'CC'
         }
