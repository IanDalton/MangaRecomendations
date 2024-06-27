import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
class ContentBasedRecommender:
   def __init__(self,df, content) -> None:
      self.df = df.reset_index()
      self.content = content
      self.tfidf = TfidfVectorizer(stop_words='english')
      self.tags_matrix = None
      self.tfidf_scores = None
      self.feature_index = None
      self.similarity_matrix = None
      self.recommendations = {}
      
   def fit_transform(self):
      self.tags_matrix = self.tfidf.fit_transform(self.content.fillna(""))
      doc = 0
      self.feature_index = self.tags_matrix[doc,:].nonzero()[1]
      
      self.tfidf_scores = zip(self.feature_index, [self.tags_matrix[doc, x] for x in self.feature_index])
      self.similarity_matrix = cosine_similarity(self.tags_matrix)
      return self
   def get_feature_names_out(self) -> list:
      feature_names = self.tfidf.get_feature_names_out()
      tfidf_scores_sorted=[]
      for w, s in [(feature_names[i], s) for (i, s) in self.tfidf_scores]:
         tfidf_scores_sorted.append([w,s])
         #print(w,s)
      return tfidf_scores_sorted   
   
   def get_recommendations(self, title, n=10, include_series=False):
      if title in self.recommendations and len(self.recommendations[title]) >= n:
         return self.recommendations[title]
      # Lowercase the title once
      title_lower = title.lower()
      # Retrieve the manga_id for the given title
      manga_index = self.df[self.df['title'] == title].index[0]
      # Directly use precomputed similarity scores
      similar_mangas_scores = self.similarity_matrix[manga_index]
      
      # Use argsort for efficient sorting, then reverse for descending order and exclude first result (itself)
      similar_mangas_indices = similar_mangas_scores.argsort()[::-1][1:]
      
      if not include_series:
         # Vectorized operation to filter out titles containing the searched-for title
        titles = self.df.loc[similar_mangas_indices, 'title'].str.lower()
        filtered_indices = similar_mangas_indices[~titles.str.contains(title_lower)]
        
        # Select top n recommendations
        manga_indices = filtered_indices[:n]
      else:
         # Select top n recommendations without additional filtering
         manga_indices = similar_mangas_indices[:n]
      
      self.recommendations[title] = self.df.iloc[manga_indices]
      
      return self.df.iloc[manga_indices]

