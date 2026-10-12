# Modified for this distribution.
import boto3
import time
import datetime
import logging
import os
                
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):
                                
    retrain_model()
def retrain_model():
    sm_client = boto3.client('sagemaker')
    iam_client = boto3.client('iam')
    logger.info(f"starting proccess +{datetime.datetime.now()}")
                                      
    role_name = os.environ['SAGEMAKER_ROLE_NAME']
    s3_bucket_uri = os.environ['S3_BUCKET_URI']
    role_response = iam_client.get_role(RoleName=role_name)
    role_arn = role_response['Role']['Arn']
                         
    training_job_name = f'sklearn-training-job-{int(time.time())}'
    sm_client.create_training_job(
        TrainingJobName=training_job_name,
        AlgorithmSpecification={
            'TrainingImage': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3',
                                     
            'TrainingInputMode': 'File'
        },
        RoleArn=role_arn,
        InputDataConfig=[
            {
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': f's3://{s3_bucket_uri}/product_ratings.csv',
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv'
            }
        ],
        OutputDataConfig={
            'S3OutputPath': f's3://{s3_bucket_uri}/'
        },
        ResourceConfig={
            'InstanceType': 'ml.m5.4xlarge',
            'InstanceCount': 1,
            'VolumeSizeInGB': 30
        },
        HyperParameters={
            'sagemaker_program': 'training_script.py',                                
            'sagemaker_submit_directory': f's3://{s3_bucket_uri}/code/code.tar.gz',                                            
            'bucket_name': s3_bucket_uri                                               
        },
        StoppingCondition={
            'MaxRuntimeInSeconds': 86400
        }
    )
                                       
    while True:
        response = sm_client.describe_training_job(TrainingJobName=training_job_name)
        status = response['TrainingJobStatus']
        if status in ['Completed', 'Failed', 'Stopped']:
            break
        time.sleep(30)
    if status != 'Completed':
        raise Exception(f"Training job failed with status: {status}")
    logger.info("training done\n starting model creation")
                  
    model_name = f'sklearn-model-{int(time.time())}'
    sm_client.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'Image': '683313688378.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3',
                                     
            'ModelDataUrl': f"s3://{s3_bucket_uri}/model.tar.gz",
            'Environment': {
                'SAGEMAKER_PROGRAM': 'inference.py',
                'SAGEMAKER_SUBMIT_DIRECTORY': f's3://{s3_bucket_uri}/code/code.tar.gz'
                                                                     
            }
        },
        ExecutionRoleArn=role_arn
    )
    logger.info("done model creation")
                                   
    endpoint_config_name = f'endpoint-config-1722516468'
    sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        ProductionVariants=[
            {
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                'InitialInstanceCount': 1,
                'InstanceType': 'ml.m5.4xlarge'
            }
        ]
    )
    logger.info("done endpoint config")
                              
    existing_endpoint_name = "reccomendation-system-endpoint"                                   
    sm_client.update_endpoint(
        EndpointName=existing_endpoint_name,
        EndpointConfigName=endpoint_config_name
    )
    logger.info(f"updating gendpoint +{datetime.datetime.now()}")
                                          
    while True:
        response = sm_client.describe_endpoint(EndpointName=existing_endpoint_name)
        status = response['EndpointStatus']
        if status in ['InService', 'Failed']:
            break
        time.sleep(30)
    if status != 'InService':
        raise Exception(f"Endpoint update failed with status: {status}")
    logger.info(f"done update +{datetime.datetime.now()}")
                                               
    sm_client.delete_endpoint_config(EndpointConfigName=endpoint_config_name)
    logger.info("Model retraining and endpoint update completed successfully.")