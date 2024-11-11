import * as cdk from 'aws-cdk-lib';
import * as path from 'path'
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as events from 'aws-cdk-lib/aws-events'
import * as targets from 'aws-cdk-lib/aws-events-targets'
require('dotenv').config()

export class EnciclaRenewalBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    if (!process.env.ENCICLA_USER_ID || !process.env.ENCICLA_PIN_CODE) {
      throw new Error("Missing required environment variables ENCICLA_USER_ID or ENCICLA_PIN_CODE");
    }

    const PROJECT_NAME = 'EnciclaRenewalBot'
    const resource_name = (resource: string) => `${PROJECT_NAME}__${resource}`
    const function_path = path.resolve(__dirname, '..', 'lambda__encicla_bot')

    const bucketName = 'encicla-renewal-bot--s3bucket';
    const zipFileKey = 'playwright-layer.zip';
    const bucket = s3.Bucket.fromBucketName(this, resource_name('s3Bucket'), bucketName);

    const playwright_lambda_layer = new lambda.LayerVersion(this, resource_name('playwrightLambdaLayer'), {
      layerVersionName: resource_name('playwrightLambdaLayer'),
      code: lambda.Code.fromBucket(bucket, zipFileKey),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12]
    });

    const encicla_bot = new lambda.Function(this, resource_name('lambdaFunction'), {
      functionName: 'encicla_renewal_bot',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset(function_path),
      handler: 'main.lambda_handler',
      environment: {
        ENCICLA_USER_ID: process.env.ENCICLA_USER_ID!,
        ENCICLA_PIN_CODE: process.env.ENCICLA_PIN_CODE!,
        ENCICLA_USER_NAME: process.env.ENCICLA_USER_NAME!,
        ENCICLA_DOCUMENT_TYPE: process.env.ENCICLA_DOCUMENT_TYPE!,
      },
      layers: [playwright_lambda_layer]
    })

    const event_rule = new events.Rule(this, resource_name('EventBridgeRule'), {
      ruleName:resource_name('EventBridgeRule'),
      schedule: events.Schedule.rate(cdk.Duration.days(5)),
    })

    event_rule.addTarget(new targets.LambdaFunction(encicla_bot))

  }
}
