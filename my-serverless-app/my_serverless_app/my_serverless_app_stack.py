from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_cognito as cognito
)
from constructs import Construct

class MyServerlessAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Cognito User Pool
        user_pool = cognito.UserPool(
            self, "MyappUserPool",
            user_pool_name="MyappUserPool",
            self_sign_up_enabled=True,  # Allow users to sign up
            sign_in_aliases=cognito.SignInAliases(
                email=True,  # Allow sign in with email
                username=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),  # Auto-verify email
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

        # Lambda Function
        lambda_function = _lambda.Function(
            self, "MyappLambdaFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda/myapp"),  # Assuming your code is in a folder named "lambda"
        )

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

        # Outputs
        self.add_output("ApiUrl", api.url)
        self.add_output("UserPoolId", user_pool.user_pool_id)
        self.add_output("UserPoolClientId", user_pool_client.user_pool_client_id)

    def add_output(self, id: str, value: str):
        from aws_cdk import CfnOutput
        CfnOutput(self, id, value=value)