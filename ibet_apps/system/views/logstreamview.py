from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import os
import json
import time
import boto3
from botocore.exceptions import ClientError
import re
#import firehose_to_s3 as fh_s3

import logging
logger = logging.getLogger('django')




class LogStreamToS3(APIView):

    permission_classes = (AllowAny, )


    def get_firehose_arn(self, firehose_name):
        """Retrieve the ARN of the specified Firehose
    
        :param firehose_name: Firehose stream name
        :return: If the Firehose stream exists, return ARN, else None
        """
    
        # Try to get the description of the Firehose
        firehose_client = boto3.client('firehose', region_name="eu-west-2")
        try:
            result = firehose_client.describe_delivery_stream(DeliveryStreamName=firehose_name)
        except ClientError as e:
            logging.error(e)
            return None
        return result['DeliveryStreamDescription']['DeliveryStreamARN']
    
    
    def firehose_exists(self, firehose_name):
        """Check if the specified Firehose exists
    
        :param firehose_name: Firehose stream name
        :return: True if Firehose exists, else False
        """
    
        # Try to get the description of the Firehose
        if self.get_firehose_arn(firehose_name) is None:
            return False
        return True
    
    
    def get_iam_role_arn(self, iam_role_name):
        """Retrieve the ARN of the specified IAM role
    
        :param iam_role_name: IAM role name
        :return: If the IAM role exists, return ARN, else None
        """
    
        # Try to retrieve information about the role
        iam_client = boto3.client('iam')
        try:
            result = iam_client.get_role(RoleName=iam_role_name)
        except ClientError as e:
            logging.error(e)
            return None
        return result['Role']['Arn']
    
    
    def iam_role_exists(self, iam_role_name):
        """Check if the specified IAM role exists
    
        :param iam_role_name: IAM role name
        :return: True if IAM role exists, else False
        """
    
        # Try to retrieve information about the role
        if self.get_iam_role_arn(iam_role_name) is None:
            return False
        return True
    
    
    def create_iam_role_for_firehose_to_s3(self, iam_role_name, s3_bucket,
                                           firehose_src_stream=None):
        """Create an IAM role for a Firehose delivery system to S3
    
        :param iam_role_name: Name of IAM role
        :param s3_bucket: ARN of S3 bucket
        :param firehose_src_stream: ARN of source Kinesis Data Stream. If
            Firehose data source is via direct puts then arg should be None.
        :return: ARN of IAM role. If error, returns None.
        """
    
        # Firehose trusted relationship policy document
        firehose_assume_role = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': '',
                    'Effect': 'Allow',
                    'Principal': {
                        'Service': 'firehose.amazonaws.com'
                    },
                    'Action': 'sts:AssumeRole'
                }
            ]
        }
        iam_client = boto3.client('iam')
        try:
            result = iam_client.create_role(RoleName=iam_role_name,
                                            AssumeRolePolicyDocument=json.dumps(firehose_assume_role))
        except ClientError as e:
            logging.error(e)
            return None
        firehose_role_arn = result['Role']['Arn']
    
        # Define and attach a policy that grants sufficient S3 permissions
        policy_name = 'firehose_s3_access'
        s3_access = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Action": [
                        "s3:AbortMultipartUpload",
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:ListBucket",
                        "s3:ListBucketMultipartUploads",
                        "s3:PutObject"
                    ],
                    "Resource": [
                        "{}/*".format(s3_bucket),
                        "{}".format(s3_bucket)
                    ]
                }
            ]
        }
        try:
            iam_client.put_role_policy(RoleName=iam_role_name,
                                       PolicyName=policy_name,
                                       PolicyDocument=json.dumps(s3_access))
        except ClientError as e:
            logging.error(e)
            return None
    
        # If the Firehose source is a Kinesis data stream then access to the
        # stream must be allowed.
        if firehose_src_stream is not None:
            policy_name = 'firehose_kinesis_access'
            kinesis_access = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "",
                        "Effect": "Allow",
                        "Action": [
                            "kinesis:DescribeStream",
                            "kinesis:GetShardIterator",
                            "kinesis:GetRecords"
                        ],
                        "Resource": [
                            "{}".format(firehose_src_stream)
                        ]
                    }
                 ]
            }
            try:
                iam_client.put_role_policy(RoleName=iam_role_name,
                                           PolicyName=policy_name,
                                           PolicyDocument=json.dumps(kinesis_access))
            except ClientError as e:
                logging.error(e)
                return None
    
        # Return the ARN of the created IAM role
        return firehose_role_arn
    
    
    def create_firehose_to_s3( self, firehose_name, s3_bucket_arn, 
                               iam_role_name, source,
                               firehose_src_type='DirectPut', 
                               firehose_src_stream=None):
        """Create a Kinesis Firehose delivery stream to S3
    
        The data source can be either a Kinesis Data Stream or puts sent directly
        to the Firehose stream.
    
        :param firehose_name: Delivery stream name
        :param s3_bucket_arn: ARN of S3 bucket
        :param iam_role_name: Name of Firehose-to-S3 IAM role. If the role doesn't
            exist, it is created.
        :param firehose_src_type: 'DirectPut' or 'KinesisStreamAsSource'
        :param firehose_src_stream: ARN of source Kinesis Data Stream. Required if
            firehose_src_type is 'KinesisStreamAsSource'
        :return: ARN of Firehose delivery stream. If error, returns None.
        """
    
        # Create Firehose-to-S3 IAM role if necessary
        if self.iam_role_exists(iam_role_name):
            # Retrieve its ARN
            iam_role = self.get_iam_role_arn(iam_role_name)
        else:
            iam_role = self.create_iam_role_for_firehose_to_s3(iam_role_name,
                                                          s3_bucket_arn,
                                                          firehose_src_stream)
            if iam_role is None:
                # Error creating IAM role
                return None
    
        # Create the S3 configuration dictionary
        # Both BucketARN and RoleARN are required
        # Set the buffer interval=60 seconds (Default=300 seconds)
        #
        #    'CloudWatchLoggingOptions': {
        #        'Enabled': True,
        #        'LogGroupName': prefix,
        #        'LogStreamName': 'string'
        #    }
        # default: 300 seconds or 5 MB, whichever comes first
        #    'BufferingHints': {
        #        'SizeInMBs': 123,
        #        'IntervalInSeconds': 60, 
        #    },
        #
        prefix = source + '/'
        s3_config = {
            'BucketARN': s3_bucket_arn,
            'RoleARN': iam_role,
            'Prefix': prefix,
            'BufferingHints': {
                'IntervalInSeconds': 60, 
            },
        }
    
        # Create the delivery stream
        # By default, the DeliveryStreamType='DirectPut'
        firehose_client = boto3.client('firehose', region_name="eu-west-2")
        try:
            if firehose_src_type == 'KinesisStreamAsSource':
                # Define the Kinesis Data Stream configuration
                stream_config = {
                    'KinesisStreamARN': firehose_src_stream,
                    'RoleARN': iam_role,
                }
                result = firehose_client.create_delivery_stream(
                    DeliveryStreamName=firehose_name,
                    DeliveryStreamType=firehose_src_type,
                    KinesisStreamSourceConfiguration=stream_config,
                    ExtendedS3DestinationConfiguration=s3_config)
            else:
                result = firehose_client.create_delivery_stream(
                    DeliveryStreamName=firehose_name,
                    DeliveryStreamType=firehose_src_type,
                    ExtendedS3DestinationConfiguration=s3_config)
        except ClientError as e:
            logging.error(e)
            return None
        return result['DeliveryStreamARN']
    
    
    def wait_for_active_firehose(self, firehose_name):
        """Wait until the Firehose delivery stream is active
    
        :param firehose_name: Name of Firehose delivery stream
        :return: True if delivery stream is active. Otherwise, False.
        """
    
        # Wait until the stream is active
        firehose_client = boto3.client('firehose', region_name="eu-west-2")
        while True:
            try:
                # Get the stream's current status
                result = firehose_client.describe_delivery_stream(DeliveryStreamName=firehose_name)
            except ClientError as e:
                logging.error(e)
                return False
            status = result['DeliveryStreamDescription']['DeliveryStreamStatus']
            if status == 'ACTIVE':
                return True
            if status == 'DELETING':
                logging.error('Firehose delivery stream {} is being deleted.'.format(firehose_name))
                return False
            time.sleep(2)
        
        
    def post(self, request, *args, **kwargs):
        
        line = request.data['line'] + "\n"
            
        """Exercise Kinesis Firehose methods"""
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)s: %(asctime)s: %(message)s')

        #
        # Limit source in ['Android','Ibetweb']?
        #
        source = ''
        for src in ['Android','Ibetweb']:
            if re.match(src, request.data['source'], re.IGNORECASE):
                source = src
                break
        
        if not source:
            source = 'Unknown'
            logging.info('Log source NOT defined, using "Unknown"')
            
        # Assign these values before running the program
        # If the specified IAM role does not exist, it will be created
        firehose_name = source + 'DeliveryStream'
        iam_role_name = 'firehose_delivery_role'
        bucket_arn = 'arn:aws:s3:::ibet-admin-eudev'
        
        logging.info('Firehose Name is {}, Bucket ARN is {}'.format(firehose_name, bucket_arn))
    
        # If Firehose doesn't exist, create it
        if not self.firehose_exists(firehose_name):
            # Create a Firehose delivery stream to S3. The Firehose will receive
            # data from direct puts.
            firehose_arn = self.create_firehose_to_s3(firehose_name, bucket_arn, iam_role_name, source)
            if firehose_arn is None:
                exit(1)
            logging.info('Created Firehose delivery stream to S3: {}'.format(firehose_arn))
    
            # Wait for the stream to become active
            if not self.wait_for_active_firehose(firehose_name):
                exit(1)
            logging.info('Firehose stream is active')
    
        firehose_client = boto3.client('firehose', region_name="eu-west-2")
        #
        # Put the record into the Firehose stream
        #
        # if necessary, do firehose_client.put_record_batch()
        #
        try:
            firehose_client.put_record(DeliveryStreamName=firehose_name,
                                       Record={'Data': line})
        except ClientError as e:
            logging.error(e)
            exit(1)
        
        
        #logging.info('Logs sent to Firehose stream')
        
        return Response({'Status': 'Successfully sent to ' + firehose_name})
    

        
