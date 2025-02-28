##### 成品 #####

# 透過 gradio 建立一個可以篩選指定村鄰里的介面

#* gradio 是一個能夠讓非網頁工程師建立簡單網頁應用程式的模組。
#* gradio 的 Interface 類別允許我們建立四種不同的介面：
 #* 標準介面：左邊輸入、右邊輸出。
 #* 僅有輸入。
 #* 僅有輸出。
 #* 整合介面：輸入與輸出在同一個區塊。

 
# 先以一個僅有輸入的介面嘗試
#* gradio 的 Interface 類別可以接受基本的三個參數：
 #* fn: 函數。
 #* inputs: 輸入的 UI 元件，可以設定為 None 成為僅有輸出的介面。
 #* outputs: 輸出的 UI 元件，可以設定為 None 成為僅有輸入的介面。

import gradio as gr
import sqlite3
import pandas as pd


def filter_county_town_village(county_name, town_name, village_name):
    pass

interface = gr.Interface(fn=filter_county_town_village,
                         inputs=[
                             "text",
                             "text",
                             "text"
                         ],
                         outputs=None,
                         title="找出章魚里",
                         description="輸入你想篩選的縣市、鄉鎮市區與村鄰里："
)
interface.launch()


# 在輸入與輸出各新增一個資料框元件

import gradio as gr
import sqlite3
import pandas as pd
import numpy as np
 

def filter_county_town_village(df, county_name, town_name, village_name):
    pass

interface = gr.Interface(fn=filter_county_town_village,
                         inputs=[
                             "dataframe",
                             "text",
                             "text",
                             "text"
                         ],
                         outputs="dataframe",
                         title="找出章魚里",
                         description="輸入你想篩選的縣市、鄉鎮市區與村鄰里："
                         )
interface.launch()


# 加入計算完餘弦相似度的資料框

def create_gradio_dataframe():
    connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
    votes_by_village = pd.read_sql("""SELECT * FROM votes_by_village;""", con=connection)
    connection.close()
    total_votes = votes_by_village["sum_votes"].sum()
    country_percentage = votes_by_village.groupby("number")["sum_votes"].sum() / total_votes
    vector_a = country_percentage.values
    groupby_variables = ["county", "town", "village"]
    village_total_votes = votes_by_village.groupby(groupby_variables)["sum_votes"].sum().reset_index()
    merged = pd.merge(votes_by_village, village_total_votes, left_on=groupby_variables, right_on=groupby_variables,
                      how="left")
    merged["village_percentage"] = merged["sum_votes_x"] / merged["sum_votes_y"]
    merged = merged[["county", "town", "village", "number", "village_percentage"]]
    pivot_df = merged.pivot(index=["county", "town", "village"], columns="number", values="village_percentage").reset_index()
    pivot_df = pivot_df.rename_axis(None, axis=1)
    cosine_similarities = []
    for row in pivot_df.iterrows():
        vector_bi = np.array([row[1][1], row[1][2], row[1][3]])
        vector_a_dot_vector_bi = np.dot(vector_a, vector_bi)
        length_vector_a = pow((vector_a**2).sum(), 0.5)
        length_vector_bi = pow((vector_bi**2).sum(), 0.5)
        cosine_similarity = vector_a_dot_vector_bi / (length_vector_a*length_vector_bi)
        cosine_similarities.append(cosine_similarity)
    cosine_similarity_df = pivot_df.iloc[:, :]
    cosine_similarity_df["cosine_similarity"] = cosine_similarities
    cosine_similarity_df = cosine_similarity_df.sort_values(["cosine_similarity", "county", "town", "village"],
                                                            ascending=[False, True, True, True])
    cosine_similarity_df = cosine_similarity_df.reset_index(drop=True).reset_index()
    cosine_similarity_df["index"] = cosine_similarity_df["index"] + 1
    column_names_to_revise = {
        "index": "similarity_rank",
        1: "candidate_1",
        2: "candidate_2",
        3: "candidate_3"
    }
    cosine_similarity_df = cosine_similarity_df.rename(columns=column_names_to_revise)
    return cosine_similarity_df


def filter_county_town_village(df, county_name, town_name, village_name):
    pass

gradio_dataframe = create_gradio_dataframe()

# print(gradio_dataframe)

interface = gr.Interface(fn=filter_county_town_village,
                         inputs=[
                             gr.DataFrame(gradio_dataframe),
                             "text",
                             "text",
                             "text"
                         ],
                         outputs="dataframe",
                         title="找出章魚里",
                         description="輸入你想篩選的縣市、鄉鎮市區與村鄰里："
                         )
interface.launch()




# 加入篩選指定村鄰里函數

import gradio as gr


gradio_dataframe = create_gradio_dataframe()

def create_gradio_dataframe():
    connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
    votes_by_village = pd.read_sql("""SELECT * FROM votes_by_village;""", con=connection)
    connection.close()
    total_votes = votes_by_village["sum_votes"].sum()
    country_percentage = votes_by_village.groupby("number")["sum_votes"].sum() / total_votes
    vector_a = country_percentage.values
    groupby_variables = ["county", "town", "village"]
    village_total_votes = votes_by_village.groupby(groupby_variables)["sum_votes"].sum().reset_index()
    merged = pd.merge(votes_by_village, village_total_votes, left_on=groupby_variables, right_on=groupby_variables,
                      how="left")
    merged["village_percentage"] = merged["sum_votes_x"] / merged["sum_votes_y"]
    merged = merged[["county", "town", "village", "number", "village_percentage"]]
    pivot_df = merged.pivot(index=["county", "town", "village"], columns="number", values="village_percentage").reset_index()
    pivot_df = pivot_df.rename_axis(None, axis=1)
    cosine_similarities = []
    for row in pivot_df.iterrows():
        vector_bi = np.array([row[1][1], row[1][2], row[1][3]])
        vector_a_dot_vector_bi = np.dot(vector_a, vector_bi)
        length_vector_a = pow((vector_a**2).sum(), 0.5)
        length_vector_bi = pow((vector_bi**2).sum(), 0.5)
        cosine_similarity = vector_a_dot_vector_bi / (length_vector_a*length_vector_bi)
        cosine_similarities.append(cosine_similarity)
    cosine_similarity_df = pivot_df.iloc[:, :]
    cosine_similarity_df["cosine_similarity"] = cosine_similarities
    cosine_similarity_df = cosine_similarity_df.sort_values(["cosine_similarity", "county", "town", "village"],
                                                            ascending=[False, True, True, True])
    cosine_similarity_df = cosine_similarity_df.reset_index(drop=True).reset_index()
    cosine_similarity_df["index"] = cosine_similarity_df["index"] + 1
    column_names_to_revise = {
        "index": "similarity_rank",
        1: "candidate_1",
        2: "candidate_2",
        3: "candidate_3"
    }
    cosine_similarity_df = cosine_similarity_df.rename(columns=column_names_to_revise)
    return vector_a, cosine_similarity_df

country_percentage, gradio_dataframe = create_gradio_dataframe()
ko_wu, lai_hsiao, hou_chao  = country_percentage

# print(gradio_dataframe)
# print(ko_wu)
# print(lai_hsiao)
# print(hou_chao)


def filter_county_town_village(df, county_name, town_name, village_name):
    county_condition = df["county"] == county_name
    town_condition = df["town"] == town_name
    village_condition = df["village"] == village_name
    return df[county_condition & town_condition & village_condition]

interface = gr.Interface(fn=filter_county_town_village,
                         inputs=[
                             gr.DataFrame(gradio_dataframe),
                             "text",
                             "text",
                             "text"
                         ],
                         outputs="dataframe",
                         title="找出章魚里",
                         description=f"輸入你想篩選的縣市、鄉鎮市區與村鄰里。(柯吳, 賴蕭, 侯趙) = ({ko_wu:.6f}, {lai_hsiao:.6f}, {hou_chao:.6f})"
                        )
interface.launch()