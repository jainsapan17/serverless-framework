# Serverless 3-Tier Web Application Framework

This project uses AWS CDK to deploy a serverless 3-tier web application infrastructure. It includes a frontend hosted on S3 and distributed via CloudFront, an API Gateway with Lambda backend, and a DynamoDB database, all secured with AWS Cognito authentication.

## Architecture

The application consists of the following components:

1. **Frontend**: Static website hosted on S3 and distributed via CloudFront
2. **Backend**: API Gateway with Lambda functions
3. **Database**: DynamoDB table
4. **Authentication**: Cognito User Pool
5. **Content Delivery**: CloudFront distribution

## Prerequisites

- AWS account
- AWS CLI configured
- Node.js and npm installed
- Python 3.9 or later
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Project Structure

```
.
├── my_serverless_app/
│   └── my_serverless_app_stack.py
├── lambda/
│   ├── layer/
│   └── myapp/
│       └── lambda_function.py
├── website/
├── app.py
├── requirements.txt
└── README.md
```

## Setup and Deployment

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Deploy the CDK stack:
   ```
   cdk deploy
   ```

5. After deployment, the CDK will output important information such as the API URL, Cognito User Pool ID, and CloudFront distribution domain name.

## Stack Components

### Cognito User Pool
- Enables user sign-up and sign-in
- Configures password policies and user verification

### Lambda Function
- Implements the backend logic
- Uses a custom Lambda Layer for dependencies

### API Gateway
- Creates RESTful API endpoints
- Integrates with Lambda functions
- Implements CORS and Cognito authorization

### S3 Bucket
- Hosts the static website files
- Configured with private access

### CloudFront Distribution
- Distributes the static website globally
- Uses Origin Access Control for secure S3 access

### DynamoDB Table
- Stores application data
- Configured with on-demand capacity

## Customization

- Update the `lambda/myapp/lambda_function.py` file to implement your backend logic.
- Place your frontend files in the `website/` directory.
- Modify the `MyServerlessAppStack` class in the CDK code to adjust infrastructure settings.
- Manually add required users to AWS Cognito User-pool (created by this stack)

## Cleanup

To avoid incurring future charges, delete the stack (if no longer in use):

```
cdk destroy
```

## Security

This project implements several security best practices:
- Private S3 bucket with CloudFront distribution
- Cognito user authentication
- API Gateway with Cognito authorizer
- Lambda function with least privilege permissions

Ensure to review and enhance security measures as needed for your specific use case.

## Status
Working

## Author
Sapan Jain

## Version
1.0

## Date
2024-12-03

## Contributing

Contributions to improve the project are welcome. Please follow the standard GitHub pull request process to propose changes.

## License

Copyright (c) 2024 Sapan Jain

All rights reserved.

This software and associated documentation files (the "Software") are the proprietary property of Sapan Jain. The Software is protected by copyright laws and international copyright treaties, as well as other intellectual property laws and treaties.

Unauthorized copying, modification, distribution, or use of this Software, via any medium, is strictly prohibited without the express written permission of the copyright holder.

The Software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the author or copyright holder be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the Software or the use or other dealings in the Software.

Any use of this Software is at your own risk. The author is not responsible for any damages, losses, or consequences that may arise from the use, misuse, or malfunction of the Software. By using this Software, you acknowledge and agree that you assume all risks associated with its use and that the author shall not be held liable for any direct, indirect, incidental, special, exemplary, or consequential damages resulting from the use or inability to use the Software.

For permission requests, please contact: Sapan Jain at jainsapan171@gmail.com