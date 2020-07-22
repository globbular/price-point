from aws_cdk import (
    aws_events as events,
    aws_lambda as lambda_,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda_event_sources as event_sources,
    aws_dynamodb as dynamo,
    core,
)


class PricePointStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, *, email: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        
        # Code Asset 
        lamba_code = lambda_.AssetCode("./assets/")
        
        # DynamoDB
        dynamo_store_db = dynamo.Table(self,"products_to_check_db",
                                        partition_key=dynamo.Attribute(name="ProductTs",type=dynamo.AttributeType.NUMBER))

        # SNS Topics
        sns_input_topic = sns.Topic(self,"checker_url_topic")
        sns_output_topic = sns.Topic(self,"email_topic")

        # Lambda function that scrapes the pages & emails
        lambda_checker = lambda_.Function(
            self, "lambda_checker",
            code=lamba_code,
            handler="checker.handler",
            timeout=core.Duration.seconds(60),
            runtime=lambda_.Runtime.NODEJS_12_X,
            environment= {
                "TOPIC_ARN": sns_output_topic.topic_arn,
                "DYNAMO_TABLE": dynamo_store_db.table_name
            }
        )
        # Subscribe to SNS
        sns_input_topic.add_subscription(subs.LambdaSubscription(lambda_checker))
        sns_output_topic.add_subscription(subs.EmailSubscription(email))

        # Lambda function that populates SNS
        lambda_invoker = lambda_.Function(
            self, "lambda_invoker",
            code=lamba_code,
            handler="invoker.handler",
            timeout=core.Duration.seconds(300),
            runtime=lambda_.Runtime.NODEJS_12_X,
            environment= {
                "TOPIC_ARN": sns_input_topic.topic_arn,
                "DYNAMO_TABLE": dynamo_store_db.table_name
            }
        )

        # Grant access to publish on SNS topics
        sns_input_topic.grant_publish(lambda_invoker)
        sns_output_topic.grant_publish(lambda_checker)

        # Grant access to Dynamo for lambdas
        dynamo_store_db.grant_read_data(lambda_invoker)
        dynamo_store_db.grant_read_write_data(lambda_checker)
    
        # Run every day at 05:00 UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        rule = events.Rule(
            self, "runEveryDayAt5AM",
            schedule=events.Schedule.cron(
                minute='0',
                hour='5',
                month='*',
                week_day='*',
                year='*'),
        )
        rule.add_target(targets.LambdaFunction(lambda_invoker))
