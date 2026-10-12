# Modified for this distribution.
import boto3
import json


def lambda_handler(event, context):
                                         
    if isinstance(event, dict) and 'user_id' in event:
        user_id = event['user_id']
    else:
                                       
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')

                                                     
    runtime = boto3.client('sagemaker-runtime')

                                                                                                    
    payload = str(user_id)

                                         
    endpoint_name = 'reccomendation-system-endpoint'

                                   
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='text/plain',                                                                  
        Body=payload
    )

                         
    result = response['Body'].read().decode('utf-8')

                                          
    return {
        'statusCode': 200,
        'body': json.dumps({
            'recommended_items': result
        })
    }
