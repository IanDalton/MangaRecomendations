import pandas as pd

from .content_based_recommender import ContentBasedRecommender
from sklearn.preprocessing import MultiLabelBinarizer
from surprise import SVD
from surprise import Dataset,Reader

class Recomendator:
    def __init__ (self, user_path, manga_path):
        self.users = pd.read_csv(user_path)

        self.mangas = pd.read_csv(manga_path)
        self.mangas["thumbnail"] = self.mangas["thumbnail"].fillna("null")
        self.mangas["genres"] = self.mangas["genres"].apply(lambda x: eval(x))
        self.mangas["authors"] = self.mangas["authors"].apply(lambda x: eval(x))
        self.mangas = self.mangas.dropna(subset=["mean"])

        self.users = self.users.reset_index()
        self.users = self.users[self.users["score"]>0]
        self.mangas = self.mangas.reset_index()

        self.full_df = self.users.merge(self.mangas, on="manga_id", how="inner", suffixes=('_user', '_manga'))    

        self.recommend_by_synopsis = ContentBasedRecommender(self.mangas, self.mangas["synopsis"])
        self.recommend_by_genres = ContentBasedRecommender(self.mangas, self.mangas["genres"].str.join(" "))
        


        self.users = self.users.reset_index()
        self.mangas = self.mangas.reset_index()

        self.svd = SVD(n_factors= 50, lr_all= 0.005, reg_all= 0.05)

        reader = Reader(rating_scale=(1, 10))
        data = Dataset.load_from_df(self.users[['user', 'manga_id', 'score']], reader)
        trainset = data.build_full_trainset()
        
        self.svd.fit(trainset)

        self.user_to_uid = {user: uid for uid, user in enumerate(self.users['user'].unique())}
        self.manga_to_iid = {manga_id: iid for iid, manga_id in enumerate(self.users['manga_id'].unique())}
        self.manga_to_iid = {manga_title: self.manga_to_iid.get(manga_id) for manga_title, manga_id in self.mangas[['title', 'manga_id']].values}
        #self.genres = self.mlb.fit_transform(self.mangas["genres"])
        self.recommend_by_genres.fit_transform()
        self.recommend_by_synopsis.fit_transform()

    def set_manga_thumnail(self, manga_id, url):
        print(f"Setting thumbnail for manga_id: {manga_id} with URL: {url}")
        
        dataframes = [
            self.mangas,
            self.full_df,
            self.recommend_by_genres.df,
            self.recommend_by_synopsis.df
        ]
        
        for df in dataframes:
            matching_rows = df['manga_id'] == manga_id
            if matching_rows.any():
                print(f"Updating {sum(matching_rows)} rows in DataFrame")
                df.loc[matching_rows, "thumbnail"] = url
            else:
                print("No matching manga_id found in DataFrame")
        
        print("Done setting thumbnail.")

    def fetch_user_data(self, user:str):
        print("Fetching new user data", user)
        return None

    def get_recommendations(self, user:str, n:int=10) -> dict:
        if user not in self.users["user"].values:
            self.fetch_user_data(user)

        recommendations = set()
        # Assuming users_view is a DataFrame that represents the same data as in the SQL query
        user_read_mangas = self.full_df[ self.full_df['user'] == user]['title'].unique()
        user_read_mangas = set(user_read_mangas)

        for manga_title in user_read_mangas:
            try:
                recommendations.update(self.recommend_by_genres.get_recommendations(manga_title, n=n, include_series=False)['title'])
                recommendations.update(self.recommend_by_synopsis.get_recommendations(manga_title, n=n, include_series=False)['title'])
            except Exception as e:
                print(f"Error getting recommendations for {manga_title}: {e}")
        #print("done getting recommendations")
        #eliminamos los mangas similares ya leidos
    
        scores = {}
        
        for rec in recommendations:
            if rec in user_read_mangas:
                continue
            uid = self.user_to_uid.get(user)
            iid = self.manga_to_iid.get(rec)
            if uid is not None and iid is not None:  # Ensure both uid and iid are found
                score = self.svd.predict(uid=uid, iid=iid).est
                scores[rec] = score
        #print("done getting scores")
        scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return scores[:n]
    
    def get_recommendations_with_info(self, user:str, n:int=10) -> dict:
        recommendations = self.get_recommendations(user, n)
        recommendations_with_info = []
        for rec, score in recommendations:
            manga_id = self.mangas[self.mangas["title"]==rec]["manga_id"].values[0]
            manga_info = self.mangas[self.mangas["title"]==rec]
            manga_info = manga_info.where(pd.notnull(manga_info), None).to_dict(orient="records")[0]
            manga_info["predicted_score"] = score
            recommendations_with_info.append(manga_info)
        return recommendations_with_info
    


        
