# Modified for this distribution.
import pickle
import pandas as pd
import numpy as np
import logging
import subprocess
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==2.0.3"])

                           
logger.info(f"Pandas version: {pd.__version__}")


                                
def model_fn(model_dir):
    
                                                 
    with open(f"{model_dir}/model.pkl", 'rb') as f:
        svd = pd.read_pickle(f)
        
    with open(f"{model_dir}/cosine_sim.pkl", 'rb') as f:
        cosine_sim = pd.read_pickle(f)
        
    with open(f"{model_dir}/ui_matrix.pkl", 'rb') as f:
        ui_matrix = pd.read_pickle(f)
        
    return svd, cosine_sim, ui_matrix

def input_fn(request_body, request_content_type):
    return int(request_body)

def predict_fn(input_data, model):
    svd, cosine_sim, ui_matrix = model
    user_id = input_data
    user_idx = user_id - 1
    sim_scores = list(enumerate(cosine_sim[user_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_users_indices = [i for i, score in sim_scores[1:6]]
    top_users_ratings = ui_matrix.iloc[top_users_indices].sum(axis=0).sort_values(ascending=False)
    recommended_items = top_users_ratings.index[:5].tolist()
    return recommended_items

def output_fn(prediction, content_type):
    return str(prediction)
