

# 以 pandas 模組載入資料
#* 以 總統-A05-4-候選人得票數一覽表-各投開票所(臺北市).xlsx 為例。
#* 使用 pd.read_excel() 函數。
#* 使用 pd.read_excel 要安裝 openpyxl 模組

import pandas as pd

county_name = "臺北市"
file_path = f"data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx"  # {county_name} placeholder
df = pd.read_excel(file_path)
df.head()


# 檢視後調整載入邏輯
#* skiprows=[0, 3, 4]: 略過第 0, 3, 4 列資料不載入。
#* .iloc[:, :6]: 只選擇前 6 欄。

county_name = "臺北市"
file_path = f"data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx"
df = pd.read_excel(file_path, skiprows=[0, 3, 4])
df = df.iloc[:, :6]
df.head()


# 擷取候選人資訊

candidates_info = df.iloc[0, 3:].values.tolist()  #seeries -> np.array -> list
candidates_info


# 調整欄位名稱

df.columns = ["town", "village", "polling_place"] + candidates_info
df.head()


# 填補鄉鎮市區的未定義值
#* df["town"].ffill(): 前向填補未定義值，碰到未定義值用前一個「非未定義值」填補。

df.loc[:, "town"] = df["town"].ffill()
df.head()
print(df["town"].unique())

# 將鄉鎮市區字元中的多餘空白去除 (leading blanks 、 trailing blanks)
#* 文字間的空白 不屬於多餘空白 

df.loc[:, "town"] = df["town"].str.strip()
df["town"].unique()


# 將觀測值中有任一個未定義值的列刪除
#* 刪除候選人資訊，因為已經記錄至欄位名稱。
#* 刪除總計票數、鄉鎮市區小計票數避免重複計票。

df = df.dropna()
print(df.head())
df

# 調整投票所編號的資料類型

df["polling_place"] = df["polling_place"].astype(int)
df.dtypes


# 轉置資料框
#* pd.melt() 函數的參數：
 #* id_vars: 辨識獨一觀測值的變數。
 #* value_vars: 不指定時為 id_vars 以外的變數。
 #* var_name: 轉置後的類別變數名稱。
 #* value_name: 轉置後的值變數名稱。

id_variables = ["town", "village", "polling_place"]
melted_df = pd.melt(df, id_vars=id_variables, var_name="candidate_info", value_name="votes")
melted_df

# 新增縣市名稱的欄位

melted_df["county"] = county_name
melted_df




# 將單一縣市的資料整理組織為函數

def tidy_county_dataframe(county_name: str):
    file_path = f"data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx"
    df = pd.read_excel(file_path, skiprows=[0, 3, 4])
    df = df.iloc[:, :6]
    candidates_info = df.iloc[0, 3:].values.tolist()
    df.columns = ["town", "village", "polling_place"] + candidates_info
    df.loc[:, "town"] = df["town"].ffill()
    df.loc[:, "town"] = df["town"].str.strip()
    df = df.dropna()
    df["polling_place"] = df["polling_place"].astype(int)
    id_variables = ["town", "village", "polling_place"]
    melted_df = pd.melt(df, id_vars=id_variables, var_name="candidate_info", value_name="votes")
    melted_df["county"] = county_name
    return melted_df


# 取得 22 個縣市

import os     # operation system
import re     # regular expression

file_names = os.listdir("data")  #列出資料夾中的所有檔案
print(file_names)

county_names = []  # 建立 空的 list
for file_name in file_names:
    if ".xlsx" in file_name:
        # 總統-A05-4-候選人得票數一覽表-各投開票所(宜蘭縣).xlsx ，以 () 作為分割符
        file_name_split = re.split("\\(|\\)", file_name)   # \\ 用於跳脫正規表達式 ，| 或
        county_names.append(file_name_split[1])
print(county_names)


# 整合 22 個縣市的資料框

country_df = pd.DataFrame()
for county_name in county_names:
    county_df = tidy_county_dataframe(county_name)
    country_df = pd.concat([country_df, county_df])    # 垂直合併
country_df = country_df.reset_index(drop=True)         # 刪除 舊的索引
country_df


# 取得候選人號碼與姓名

print(country_df["candidate_info"].str.split("\n"))

numbers, candidates = [], []
for elem in country_df["candidate_info"].str.split("\n"):
    number = re.sub("\\(|\\)", "", elem[0])           # substitute 將 () 取代掉
    numbers.append(int(number))
    candidate = elem[1] + "/" + elem[2]
    candidates.append(candidate) 

print(set(numbers))
print(set(candidates))


# 重組資料框

presidential_votes = country_df.loc[:, ["county", "town", "village", "polling_place"]]
presidential_votes["number"] = numbers
presidential_votes["candidate"] = candidates
presidential_votes["votes"] = country_df["votes"].values
presidential_votes

polling_places_df = presidential_votes.groupby(["county", "town", "village", "polling_place"]).count().reset_index()
polling_places_df = polling_places_df[["county", "town", "village", "polling_place"]]
polling_places_df = polling_places_df.reset_index()          # 建立 primary key
polling_places_df["index"] = polling_places_df["index"] + 1
polling_places_df = polling_places_df.rename(columns={"index": "id"})
polling_places_df

candidates_df = presidential_votes.groupby(["number", "candidate"]).count().reset_index()
candidates_df = candidates_df[["number", "candidate"]]
candidates_df = candidates_df.rename(columns={"number": "id"})
candidates_df

join_keys = ["county", "town", "village", "polling_place"]
# 用 left
votes_df = pd.merge(presidential_votes, polling_places_df, left_on=join_keys, right_on=join_keys, how="left")   
votes_df = votes_df[["id", "number", "votes"]]
votes_df = votes_df.rename(columns={"id": "polling_place_id", "number": "candidate_id"})
votes_df



# 整理程式碼為一個類別 CreateTaiwanPresidentialElection2024DB

import os     
import re     
import sqlite3
import pandas as pd


class CreateTaiwanPresidentialElection2024DB:
    def __init__(self):
        # 整合 22 個縣市的資料框
        file_names = os.listdir("data")
        county_names = []
        for file_name in file_names:
            if ".xlsx" in file_name:
                file_name_split = re.split("\(|\)", file_name)
                county_names.append(file_name_split[1])
        self.county_names = county_names  # 用屬性紀錄起來
    
    def tidy_county_dataframe(self, county_name: str):
        file_path = f"data/總統-A05-4-候選人得票數一覽表-各投開票所({county_name}).xlsx"
        df = pd.read_excel(file_path, skiprows=[0, 3, 4])
        df = df.iloc[:, :6]
        candidates_info = df.iloc[0, 3:].values.tolist()
        df.columns = ["town", "village", "polling_place"] + candidates_info
        df.loc[:, "town"] = df["town"].ffill()
        df.loc[:, "town"] = df["town"].str.strip()
        df = df.dropna()
        df["polling_place"] = df["polling_place"].astype(int)
        id_variables = ["town", "village", "polling_place"]
        melted_df = pd.melt(df, id_vars=id_variables, var_name="candidate_info", value_name="votes")
        melted_df["county"] = county_name
        return melted_df

    def concat_country_dataframe(self):
        country_df = pd.DataFrame()
        for county_name in self.county_names:
            county_df = self.tidy_county_dataframe(county_name)
            country_df = pd.concat([country_df, county_df])
        country_df = country_df.reset_index(drop=True)
        numbers, candidates = [], []
        for elem in country_df["candidate_info"].str.split("\n"):
            number = re.sub("\(|\)", "", elem[0])
            numbers.append(int(number))
            candidate = elem[1] + "/" + elem[2]
            candidates.append(candidate)
        presidential_votes = country_df.loc[:, ["county", "town", "village", "polling_place"]]
        presidential_votes["number"] = numbers
        presidential_votes["candidate"] = candidates
        presidential_votes["votes"] = country_df["votes"].values
        return presidential_votes

    def create_database(self):
        country_dataframe = self.concat_country_dataframe()
        polling_places_df = country_dataframe.groupby(["county", "town", "village", "polling_place"]).count().reset_index()
        polling_places_df = polling_places_df[["county", "town", "village", "polling_place"]]
        polling_places_df = polling_places_df.reset_index()
        polling_places_df["index"] = polling_places_df["index"] + 1
        polling_places_df = polling_places_df.rename(columns={"index": "id"})
        
        candidates_df = country_dataframe.groupby(["number", "candidate"]).count().reset_index()
        candidates_df = candidates_df[["number", "candidate"]]
        candidates_df = candidates_df.rename(columns={"number": "id"})

        join_keys = ["county", "town", "village", "polling_place"]
        
        votes_df = pd.merge(country_dataframe, polling_places_df, left_on=join_keys, right_on=join_keys, 
                            how="left")
        votes_df = votes_df[["id", "number", "votes"]]
        votes_df = votes_df.rename(columns={"id": "polling_place_id", "number": "candidate_id"})
        
        connection = sqlite3.connect("data/taiwan_presidential_election_2024.db")
        polling_places_df.to_sql("polling_places", con=connection, if_exists="replace", index=False)
        candidates_df.to_sql("candidates", con=connection, if_exists="replace", index=False)
        votes_df.to_sql("votes", con=connection, if_exists="replace", index=False)
        cur = connection.cursor()
        drop_view_sql = """
        DROP VIEW IF EXISTS votes_by_village;
        """
        create_view_sql = """
        CREATE VIEW votes_by_village AS
        SELECT polling_places.county,
               polling_places.town,
               polling_places.village,
               candidates.id AS number,
               candidates.candidate,
               SUM(votes.votes) AS sum_votes
          FROM votes
          LEFT JOIN polling_places
            ON votes.polling_place_id = polling_places.id
          LEFT JOIN candidates
            ON votes.candidate_id = candidates.id
         GROUP BY polling_places.county,
                  polling_places.town,
                  polling_places.village,
                  candidates.id; 
        """
        cur.execute(drop_view_sql)
        cur.execute(create_view_sql)
        connection.close()
        
        
# 檢查類別 CreateTaiwanPresidentialElection2024DB 能否順利運行
create_taiwan_presidential_election_2024_db = CreateTaiwanPresidentialElection2024DB()
create_taiwan_presidential_election_2024_db.create_database()
