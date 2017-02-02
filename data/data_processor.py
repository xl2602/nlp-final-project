import pandas as pd
import os
import shutil
from geopy.geocoders import Nominatim
import re
from geopy.exc import GeocoderTimedOut
# import geograpy




def check_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    if not os.path.exists(dir):
        os.makedirs(dir)


def create_lrr_file(csv_file, output_dir):
    def write_file(records, id):
        file_name = '/user_' + str(id) + '.dat'
        with open(output_dir+file_name, 'w', encoding='utf-8') as of:
            try:
                of.write('<User Name>' + records['user_name'].values[0] + '\n')
                of.write('\n')
                for i, row in records.iterrows():
                    of.write('<Title> ' + row['title'] + '\n')
                    of.write('<Content> ' + row['content'] + '\n')
                    of.write('<Overall>' + str(row['review_stars']) + '\n')
                    of.write('\n')
            except:
                print(records)

    check_dir(output_dir)

    print('Read csv file.')
    # df = pd.read_csv(csv_file, encoding='cp1252')
    df = pd.read_csv(csv_file, encoding='iso-8859-15')
    nl = list(df[['user_name', 'reviewer_location']].drop_duplicates().values.tolist())

    print('Size: ', len(nl))
    print('Creating files...')
    j = 1

    with open('userid_map_'+csv_file, 'w') as userid_map:
        for user_name, location in nl:
            userid_map.write(str(user_name) + '\t' + str(location) + '\t' + str(j) + '\t' + '' + '\n')
            records = df.loc[(df['user_name'] == user_name) & (df['reviewer_location'] == location)]
            write_file(records, j)
            j += 1
            if j % 1000 == 0:
                print('Load ' + str(j) + ' users...')





def update_geo():
    map_df = pd.read_csv('geolist-no.csv', encoding='utf-8', sep='\t', header=None)
    print(map_df)

    # print(len(map_df[0].drop_duplicates()))
    for idx, cell in map_df.iterrows():
        if pd.isnull(cell.values[1]):
            print(cell.values[0], cell.values[1])
            location = get_geo(cell.values[0])
            if location == 'NORESULT':
                pass
            else:
                with open('geolist-no.csv', 'a+') as g_list:
                    g_list.write(str(cell.values[0]) + '\t' + str(location) + '\n')


def new_userid_map(userid_map, prediction):
    map_df = pd.read_csv(userid_map, encoding='utf-8', header=None, sep='\t')
    map_df.columns = ['user_name', 'reviewer_location', 'id', 'geo']

    prediction_df = pd.read_csv(prediction, encoding='utf-8', header=None)
    prediction_df[0] = pd.DataFrame(prediction_df[0].str.split('_').tolist())[1].astype(int)
    prediction_df.columns = ['id', 'facility', 'location', 'cleanliness', 'service']

    new_userid_map_df = pd.merge(map_df, prediction_df, on='id', how='inner')
    new_userid_map_df.to_csv('new_userid_map_'+prediction, index=False, sep='\t', encoding='utf-8')


# def combine_results(csv, userid_map, prediction):
#
#     map_df = pd.read_csv(userid_map, encoding='utf-8', header=None, sep='\t')
#     map_df.columns = ['user_name', 'reviewer_location', 'id']
#
#     geo_col = map_df['reviewer_location'].apply(get_geo)
#     map_df = map_df.assign(geo=geo_col)
#
#     prediction_df = pd.read_csv(prediction, encoding='utf-8', header=None)
#     prediction_df[0] = pd.DataFrame(prediction_df[0].str.split('_').tolist())[1].astype(int)
#     prediction_df.columns = ['id', 'value', 'facility', 'location', 'cleanliness', 'service']
#
#     pre_name_df = pd.merge(map_df, prediction_df, on='id')
#
#     # csv_df = pd.read_csv(csv, encoding='cp1252')
#     csv_df = pd.read_csv(csv, encoding='iso-8859-15')
#     user_df = csv_df[['user_name', 'reviewer_location']].drop_duplicates()
#
#     all_df = pd.merge(user_df, pre_name_df, on=['user_name', 'reviewer_location'], how='inner')
#
#     all_df.to_csv('final_output.csv', index=False)


def get_city(long_location):
    city = long_location.lower().split(',')[0]
    if re.match('^[a-z]*', city):
        return city
    else:
        return ''

# def get_exist_geodict():
#     df = pd.read_csv('geolist-no.csv', encoding='utf-8', header=None, sep='\t')
#     df.columns = ['reviewer_location', 'geo']
#     df['reviewer_location'] = df['reviewer_location'].apply(lambda x: get_city(x))
#     geo_list = []
#     for idx, row in df.iterrows():
#         if not pd.isnull(row['geo']):
#             geo_list.append([row['reviewer_location'], row['geo']])
#     new_df = pd.DataFrame(geo_list)
#     new_df.to_csv('citylist_exist.csv', encoding='utf-8', sep='\t', header=None, index=False)


def check_geolist(row):
    # print(row[0], row[1])
    location = row[0]
    geo = row[1]

    exist_df = pd.read_csv('citylist_exist.csv', encoding='utf-8', sep='\t', header=None)
    exist_df.columns = ['reviewer_location', 'geo']

    if row['reviewer_location'] in exist_df['reviewer_location'].values:
        geo = exist_df[exist_df['reviewer_location'] == location]['geo'].iloc[0]
        # print(geo)
    else:
        get_geo(location)

    return geo


def update_geolist():
    df = pd.read_csv('citylist_125.csv', encoding='utf-8', sep='\t', header=None)
    df.columns = ['reviewer_location', 'geo']
    print(df['geo'].isnull().sum())

    df['geo'] = df[['reviewer_location', 'geo']].apply(lambda row: check_geolist(row) if pd.isnull(row['geo']) else row['geo'], axis=1)

    df.to_csv('citylist_125.csv', encoding='utf-8', sep='\t', header=None, index=False)


def process_map(userid_map):
    df = pd.read_csv(userid_map, encoding='utf-8', sep='\t')
    df['city'] = df['reviewer_location']
    df['city'] = df['city'].apply(lambda x: get_city(x))
    df.to_csv('city_'+userid_map, index=False, sep='\t', encoding='utf-8')
    # print(df['city'].drop_duplicates())

    # df[['city', 'geo']].drop_duplicates().to_csv('citylist_125.csv', index=False, sep='\t', encoding='utf-8', header=None)



# ---- START HERE ----
# create_lrr_file('test_12_1_min2.csv', 'output_lrr_nodup/test_12_1_min2')

# new_userid_map('userid_map_test_12_1_min2.csv', 'prediction_min2_a4.csv')
#
# process_map('new_userid_map_prediction_min2_a4.csv')

# generate list file
# df = pd.read_csv('new_userid_map_prediction_min2_a4.csv', encoding='utf-8', sep='\t')
# df['reviewer_location'] = df['reviewer_location'].apply(lambda x: x.lower())
#
# add_list = list(df['reviewer_location'].drop_duplicates().values.tolist())
# new_df = pd.DataFrame(add_list)
# new_df.to_csv('address_list.csv', encoding='utf-8', sep='\t', header=None, index=False)


def lower_loc(loc):
    return loc.lower()

def get_lat(geolist):
    print(geolist)
    print(l)
    if len(l) > 0:
        return l[2]
    else:
        return ''

def get_lon(geolist):
    print(geolist)
    if len(l) > 0:
        return l[1]
    else:
        return ''

def get_standard_add(geolist):
    l = list(geolist)
    if len(l) > 0:
        return l[0]
    else:
        return ''

geo_df = pd.read_csv('gold_geolist', encoding='utf-8', sep='\t', header=None)
geo_df.columns = ['reviewer_location', 'geolist']
# print(geo_df)

data_df = pd.read_csv('data_min2_a4.csv', encoding='utf-8', sep='\t')
data_df['reviewer_location'] = data_df['reviewer_location'].apply(lambda x: lower_loc(x))
# print(data_df)


master_df = pd.merge(data_df, geo_df, on=['reviewer_location'], how='left')
# print(master_df)
master_df['lat']= master_df['geolist'].apply(lambda x: get_lat(x) if not pd.isnull(x) else '')
master_df['lon']= master_df['geolist'].apply(lambda x: get_lon(x) if not pd.isnull(x) else '')
master_df['standard_address']= master_df['geolist'].apply(lambda x: get_standard_add(x) if not pd.isnull(x) else '')


master_df.to_csv('master.csv', index=False, sep='\t', encoding='utf-8')


