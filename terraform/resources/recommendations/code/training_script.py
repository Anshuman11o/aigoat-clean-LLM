# Modified for this distribution.
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import boto3
from io import StringIO
import pickle
import tarfile
import argparse

                                      


def parse_args():
    parser = argparse.ArgumentParser()

                         
    parser.add_argument('--bucket_name', type=str, required=True)                                   

    return parser.parse_args()
args = parse_args()

s3 = boto3.client('s3')

                                             
bucket_name = args.bucket_name

obj = s3.get_object(Bucket= bucket_name, Key= "product_ratings.csv") 


                  
file_content = obj['Body'].read().decode('utf-8')
df = pd.read_csv(StringIO(file_content))


                             
ui_matrix = df.pivot_table(index='userId', columns='productId', values='rating', fill_value=0)

                     
svd = TruncatedSVD(n_components=5, random_state=42)
matrix_reduced = svd.fit_transform(ui_matrix)

                                 
cosine_sim = cosine_similarity(matrix_reduced)

                                                                                   
                              
with open('model.pkl', 'wb') as f:
    pickle.dump(svd, f)

with open('cosine_sim.pkl', 'wb') as f:
    pickle.dump(cosine_sim, f)

with open('ui_matrix.pkl', 'wb') as f:
    pickle.dump(ui_matrix, f)
    
                      
with tarfile.open('model.tar.gz', 'w:gz') as tar:
    tar.add('ui_matrix.pkl')
    tar.add('cosine_sim.pkl')
    tar.add('model.pkl')


                             
s3.upload_file('model.tar.gz', bucket_name, 'model.tar.gz')



