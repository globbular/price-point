const AWS = require('aws-sdk');
const topicArn = process.env.TOPIC_ARN;
const tableName  = process.env.DYNAMO_TABLE;

exports.handler = (event, context, callback) => {
    // Create DynamoDB service object
    var ddb = new AWS.DynamoDB({apiVersion: '2012-08-10'});

    var params = {
        TableName: tableName
    };

    ddb.scan(params, function(err, data) {
    if (err) {
        console.log("Error", err);
    } else {
        data.Items.forEach(function(element, index, array) {
            // Send to SNS
            var params = {
                Message: JSON.stringify(element),
                TopicArn: topicArn
            };
            // Create promise and SNS service object
            var publishTextPromise = new AWS.SNS({
                apiVersion: '2010-03-31'
            }).publish(params).promise();
    
            // Handle promise's fulfilled/rejected states
            publishTextPromise.then(
                function (data) {
                    console.log(`Message ${params.Message} sent to the topic ${params.TopicArn}`);
                    console.log("MessageID is " + data.MessageId);
                }).catch(
                function (err) {
                    console.error(err, err.stack);
                });
        });
    }
    });
        
}