from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class MyServerlessAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        #------------------------#
        # [1] Cognito ----->>>
        #------------------------#
        # Cognito User Pool
        user_pool = cognito.UserPool(
            self, "MyappUserPool",
            user_pool_name="MyappUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            )
        )
        # Cognito User Pool Client
        user_pool_client = user_pool.add_client(
            "MyappUserPoolClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            )
        )

        #------------------------#
        # [2] Lambda ----->>>
        #------------------------#
        # Create Lambda role
        lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )
        # Lambda Layer
        lambda_layer = _lambda.LayerVersion(
            self, "MyappLambdaLayer",
            code=_lambda.Code.from_asset("lambda/layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="Custom layer for MyApp Lambda function",
        )
        # Lambda Function
        lambda_function = _lambda.Function(
            self, "MyappLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda/myapp"),
            layers=[lambda_layer],
            role=lambda_role
        )
        # Add permission for API Gateway to invoke Lambda
        lambda_function.add_permission(
            "APIGatewayInvoke",
            principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
            action="lambda:InvokeFunction"
        )

        #------------------------#
        # [3] API Gateway ----->>>
        #------------------------#
        # API Gateway
        api = apigateway.LambdaRestApi(
            self, "MyappApiGateway",
            handler=lambda_function,
            rest_api_name="MyServerlessApi",
            default_cors_preflight_options={
                "allow_origins": apigateway.Cors.ALL_ORIGINS,
                "allow_methods": apigateway.Cors.ALL_METHODS
            }
        )
        # Authorizer using Cognito
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "MyappCognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )
        # Example Resource with Authorization
        api.root.add_resource("secure").add_method(
            "GET",
            apigateway.LambdaIntegration(lambda_function),
            authorization_type=apigateway.AuthorizationType.COGNITO,
            authorizer=authorizer
        )

        #------------------------#
        # [4] S3 Bucket ----->>>
        #------------------------#
        # S3 Bucket for frontend static files (private)
        website_bucket = s3.Bucket(
            self, "MyappWebsiteBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        #------------------------#
        # [5] Cloudfront ----->>>
        #------------------------#
        # CloudFront Origin Access Control
        oac = cloudfront.CfnOriginAccessControl(
            self, "MyappOAC",
            origin_access_control_config=cloudfront.CfnOriginAccessControl.OriginAccessControlConfigProperty(
                name="MyappOAC",
                description="OAC for accessing private S3 bucket",
                origin_access_control_origin_type="s3",
                signing_behavior="always",
                signing_protocol="sigv4"
            )
        )
        # CloudFront distribution
        distribution = cloudfront.CfnDistribution(
            self,
            "CloudFrontDistribution",
            distribution_config=cloudfront.CfnDistribution.DistributionConfigProperty(
                enabled=True,
                default_cache_behavior=cloudfront.CfnDistribution.DefaultCacheBehaviorProperty(
                    target_origin_id="S3Origin",
                    viewer_protocol_policy="redirect-to-https",
                    allowed_methods=["GET", "HEAD"],
                    cached_methods=["GET", "HEAD"],
                    forwarded_values=cloudfront.CfnDistribution.ForwardedValuesProperty(
                        query_string=False,
                        cookies=cloudfront.CfnDistribution.CookiesProperty(
                            forward="none"
                        )
                    )
                ),
                origins=[
                    cloudfront.CfnDistribution.OriginProperty(
                        id="S3Origin",
                        domain_name=website_bucket.bucket_regional_domain_name,
                        s3_origin_config=cloudfront.CfnDistribution.S3OriginConfigProperty(
                            origin_access_identity=""
                        ),
                        origin_access_control_id=oac.attr_id  # Attach the OAC
                    )
                ]
            )
        )

        website_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[website_bucket.arn_for_objects("*")],
                principals=[
                    iam.ServicePrincipal("cloudfront.amazonaws.com")
                ]
            )
        )

        # Add a policy to the bucket for the OAC
        website_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=[website_bucket.arn_for_objects("*")],
                principals=[
                    iam.ServicePrincipal("cloudfront.amazonaws.com")
                ],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:oac/{oac.ref}"
                    }
                }
            )
        )

        # Deploy site contents to S3 bucket
        s3deploy.BucketDeployment(
            self, "DeployWebsite",
            sources=[s3deploy.Source.asset("./website")],
            destination_bucket=website_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )


        # Outputs
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "WebsiteBucketName", value=website_bucket.bucket_name)
        # CfnOutput(self, "CloudFrontDomainName", value=distribution.domain_name)
