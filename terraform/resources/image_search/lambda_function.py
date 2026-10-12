# Modified for this distribution.
import json
import boto3
import numpy as np
from PIL import Image
import io
import base64

                                     
sagemaker_runtime = boto3.client('sagemaker-runtime')
s3_client = boto3.client('s3')

                         
ENDPOINT_NAME = 'image-similarity-endpoint'


def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((224, 224))                                               
    image_array = np.array(image)

    if image_array.shape[-1] == 1:                               
        image_array = np.repeat(image_array[..., np.newaxis], 3, -1)

    image_array = np.expand_dims(image_array, axis=0)                       

                        
    image_array = image_array[..., ::-1]

                                                                
    mean = [103.939, 116.779, 123.68]
    image_array = image_array.astype(np.float32)
    image_array[..., 0] -= mean[0]
    image_array[..., 1] -= mean[1]
    image_array[..., 2] -= mean[2]

    return image_array.tolist()


def lambda_handler(event, context):
                                                      
    bucket_name = event['bucket_name']
    img_key = event['img_key']

                                
    response = s3_client.get_object(Bucket=bucket_name, Key=img_key)
    image_bytes = response['Body'].read()

                          
    preprocessed_image = preprocess_image(image_bytes)

    input_data = json.dumps({'instances': preprocessed_image})

                                   
    response = sagemaker_runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType='application/json',
        Body=input_data
    )

                                       
    response_body = response['Body'].read().decode('utf-8')
    similar_images = json.loads(response_body)

                         
    return {
        'statusCode': 200,
        'body': json.dumps(similar_images)
    }