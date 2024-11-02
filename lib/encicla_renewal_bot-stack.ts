import * as cdk from 'aws-cdk-lib';
import * as path from 'path'
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
require('dotenv').config()

export class EnciclaRenewalBotStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const function_path = path.join('..', 'lambda__encicla_bot')

    const encicla_bot = new lambda.Function(this, 'encicla_renewal_bot', {
      functionName: 'encicla_renewal_bot',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset(function_path),
      handler: 'main.lambda_handler',
      environment: {
        ENCICLA_USER_ID: process.env.ENCICLA_USER_ID!,
        ENCICLA_PIN_CODE: process.env.ENCICLA_PIN_CODE!,
      }
    })

  }
}
