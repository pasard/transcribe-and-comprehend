from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_s3_notifications as _s3nots,
    aws_events as _events,
    aws_events_targets as targets,
    aws_iam as _iam,
    core
)

import string
from random import *

class TCStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create unique ID
        min_char = 8
        max_char = 12
        allchar = string.ascii_lowercase + string.digits
        uniqueID = "".join(choice(allchar) for x in range(randint(min_char, max_char)))

        # --------------------------
        # create 1st lambda function
        function = _lambda.Function(self, "simple_transcribe",
                                    runtime=_lambda.Runtime.PYTHON_3_7,
                                    handler="lambda_function.lambda_handler",
                                    code=_lambda.Code.from_asset("./lambda/simple_transcribe"),
                                    environment={
                                        "CUSTOM_VOCABULARY":"custom-vocab",
                                        "LANGUAGE":"nl-NL"
                                    },
                                    timeout=core.Duration.seconds(60))
        # add policy Statement to launch a Transcribe job
        transcribe_policy = _iam.PolicyStatement(effect=_iam.Effect.ALLOW, actions=["transcribe:GetTranscriptionJob","transcribe:StartTranscriptionJob"], resources=["*"])
        function.add_to_role_policy(transcribe_policy)
        # add policy Statement to read S3 objects
        s3_policy = _iam.PolicyStatement(effect=_iam.Effect.ALLOW, actions=[
                "s3:GetAccessPoint",
                "s3:GetLifecycleConfiguration",
                "s3:GetBucketTagging",
                "s3:GetInventoryConfiguration",
                "s3:GetObjectVersionTagging",
                "s3:ListBucketVersions",
                "s3:GetBucketLogging",
                "s3:GetAccelerateConfiguration",
                "s3:GetBucketPolicy",
                "s3:GetObjectVersionTorrent",
                "s3:GetObjectAcl",
                "s3:GetEncryptionConfiguration",
                "s3:GetBucketObjectLockConfiguration",
                "s3:GetBucketRequestPayment",
                "s3:GetAccessPointPolicyStatus",
                "s3:GetObjectVersionAcl",
                "s3:GetObjectTagging",
                "s3:GetMetricsConfiguration",
                "s3:GetBucketPublicAccessBlock",
                "s3:GetBucketPolicyStatus",
                "s3:ListBucketMultipartUploads",
                "s3:GetObjectRetention",
                "s3:GetBucketWebsite",
                "s3:ListAccessPoints",
                "s3:ListJobs",
                "s3:GetBucketVersioning",
                "s3:GetBucketAcl",
                "s3:GetObjectLegalHold",
                "s3:GetBucketNotification",
                "s3:GetReplicationConfiguration",
                "s3:ListMultipartUploadParts",
                "s3:GetObject",
                "s3:GetObjectTorrent",
                "s3:GetAccountPublicAccessBlock",
                "s3:DescribeJob",
                "s3:GetBucketCORS",
                "s3:GetAnalyticsConfiguration",
                "s3:GetObjectVersionForReplication",
                "s3:GetBucketLocation",
                "s3:GetAccessPointPolicy",
                "s3:GetObjectVersion"], resources=["*"])
        function.add_to_role_policy(s3_policy)

        # create s3 bucket for source files
        s3 = _s3.Bucket(self, "transcribe-bucket-in-{}".format(uniqueID), bucket_name="transcribe-source-{}".format(uniqueID))

        # create s3 notification to trigger 1st lambda function
        notification = _s3nots.LambdaDestination(function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)

        # --------------------------
        # create 2nd lambda function
        function2 = _lambda.Function(self, "simple_transcribe_report",
                                    runtime=_lambda.Runtime.PYTHON_3_7,
                                    handler="lambda_function.lambda_handler",
                                    code=_lambda.Code.from_asset("./lambda/simple_transcribe_report"),
                                    environment={
                                        "S3_BUCKET":"transcribe-results-{}".format(uniqueID),
                                        "SOURCE_LANGUAGE":"nl",
                                        "TARGET_LANGUAGE":"en"
                                    },
                                    timeout=core.Duration.seconds(60))
        # add policy Statement to launch a Transcribe job
        function2.add_to_role_policy(transcribe_policy)
        # add policy Statement to call Translate
        translate_policy = _iam.PolicyStatement(effect=_iam.Effect.ALLOW, actions=["translate:TranslateText"], resources=["*"])
        function2.add_to_role_policy(translate_policy)
        # add policy Statement to call Comprehend
        comprehend_policy = _iam.PolicyStatement(effect=_iam.Effect.ALLOW, actions=[
            "comprehend:DetectDominantLanguage", 
            "comprehend:DetectEntities", 
            "comprehend:DetectKeyPhrases", 
            "comprehend:DetectSentiment"], resources=["*"])
        function2.add_to_role_policy(comprehend_policy)
        # add policy Statement to write to S3
        s3_policy2 = _iam.PolicyStatement(effect=_iam.Effect.ALLOW, actions=["s3:PutObject"], resources=["*"])
        function2.add_to_role_policy(s3_policy2)

        # create s3 bucket for output files
        s3 = _s3.Bucket(self, "transcribe-bucket-out-{}".format(uniqueID), bucket_name="transcribe-results-{}".format(uniqueID))

        # create event rule and target to trigger the 2nd lambda function
        rule = _events.Rule(
            self, "Rule",
            rule_name="simple-transcribe-done",
            event_pattern=_events.EventPattern(
                detail={
                    "TranscriptionJobStatus": [
                    "COMPLETED",
                    "FAILED"
                    ]
                },
                detail_type=[
                    "Transcribe Job State Change"
                ],
                source=[
                    "aws.transcribe"
                ],
            ),
        )
        rule.add_target(targets.LambdaFunction(function2))




