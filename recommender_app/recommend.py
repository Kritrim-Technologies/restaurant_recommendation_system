import numpy as np
import pandas as pd


dataset_location = "dataset/dataset_expanded.csv"


def get_rating(filename):
    ''' read csv files '''
    ratings = pd.read_csv(filename, index_col=0, engine="python")
    ratings.reset_index(inplace=True)
    #encode_dict = {'č': 'c', 'Í': 'I','í': 'i', 'á': 'a', '�':"'"}
    #ratings = ratings.replace(encode_dict, regex=True)
    
    ratings = ratings[["Reviewer Name", "Restaurant Name", "Rating", "Tags"]]
    #ratings["Restaurant Name"] = ratings["Restaurant Name"].str.lower()
    #ratings['Rating'] = ratings["Rating"].astype(str).str.replace('[^\d.]', '').astype(float)
    #ratings = ratings[ratings["Restaurant Name"].str.contains('CLOSED|closed')== False]
    #ratings['Restaurant Name'] = ratings['Restaurant Name'].str.split(' - ').str[0].replace("\s\s+", ' ', regex=True)
    
    return ratings






def get_tag_list():
    ''' Get the list of tags '''
    ratings = get_rating(dataset_location)
    ratings = ratings[ratings["Tags"].notnull()]
    tag_list = []
    for joint_tag in list(ratings["Tags"].unique()):
        if joint_tag == np.nan:
            continue
        for tag in (joint_tag.split(",")):
            tag = tag.lstrip()
            if tag not in tag_list:
                tag_list.append(tag)
    return tag_list


def get_user_ratings():
    ratings = get_rating(dataset_location)
    userRatings = ratings.pivot_table(
        index=["Reviewer Name"], columns=["Restaurant Name"], values="Rating"
    )
    return userRatings


def get_unique_user_ratings(user):
    ratings = get_rating(dataset_location)
    user_ratings = ratings[ratings["Reviewer Name"] == user]
    all_valid_res = get_corr_matrix().columns
    dict = {}
    for res, rating in zip(user_ratings["Restaurant Name"], user_ratings["Rating"]):
        if res in all_valid_res:    
            dict.update({res: rating})
    return dict


def get_user_list():
    ratings = get_rating(dataset_location)
    return list(set(ratings["Reviewer Name"].tolist()))


def get_corr_matrix(thresh=3):
    userRatings = get_user_ratings()
    userRatings = userRatings.dropna(thresh=3, axis=1).fillna(0, axis=1)
    corrMatrix = userRatings.corr(method="pearson")
    return corrMatrix

def get_column_tag():
    ratings = get_rating(dataset_location)
    res_from_corr_matrix = get_corr_matrix().columns
    dict = {}
    res_tag = ratings[["Restaurant Name", "Tags"]]
    for res, tag in zip(res_tag["Restaurant Name"], res_tag["Tags"]):
        if res in res_from_corr_matrix:
            dict.update({res: tag})

    return dict


def get_similar(rest_name, rating):
    corrMatrix = get_corr_matrix()
    similar_ratings = corrMatrix[rest_name] * (rating) / 5 *100
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings




def get_recommendation(user):
    try:
        recommendation = []
        user_rating_history = get_unique_user_ratings(user)
        similar_rest = pd.DataFrame()

        for rest_name,rating in zip(list(user_rating_history.keys()), list(user_rating_history.values())):
            if rest_name in get_corr_matrix().columns:
                similar_rest= similar_rest.append(get_similar(rest_name,rating),ignore_index = True)

        similar = similar_rest.mean().sort_values(ascending=False)
        keys = dict(similar).keys()

        col_tag = get_column_tag()
        recommendation = []
        likeness = []
        tags = []
        for key in keys:
        
            if key not in list(user_rating_history.keys()):
                recommendation.append(key)
                tags.append(col_tag[key])
                likeness.append(similar[key])
        

 
        likeness = [ '%.2f' % elem for elem in likeness ]
        return recommendation, tags, likeness
    except Exception as e:
        return (["Sorry"], ["No Recommendation available !"])


def update_dataset(user, rest_name, rating):

    ratings = get_rating(dataset_location)
    ratings.reset_index(drop=True, inplace=True)
    ratings = ratings.append(
        {
            "Reviewer Name": user,
            "Restaurant Name": rest_name,
            "Rating": rating,
            "Tags": get_column_tag()[rest_name],
        },
        ignore_index=True,
    )
    ratings.reset_index(drop=True, inplace=True)
    ratings.drop_duplicates(inplace=True)

    ratings.to_csv(dataset_location)
