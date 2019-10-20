const AWS = require('aws-sdk');
const cheerio = require('cheerio')
const request = require('request');
const currencyJs = require('currency.js');
const topicArn = process.env.TOPIC_ARN;
const tableName = process.env.DYNAMO_TABLE;

exports.handler = (event, context, callback) => {
    var message = event.Records[0].Sns.Message;
    console.log('Message received from SNS:', message);
    var messageObj = JSON.parse(message);

    request(messageObj.Url.S, function (error, response, body) {
        if (error) {
            console.log('error:', error); // Print the error if one occurred
        } else {
            const $ = cheerio.load(body);
            let textToExtract = '';
            
            if ("Attr" in messageObj.Selector.M) {
                // Value is in attribute of element
                textToExtract = $(messageObj.Selector.M.Value.S).first().attr(messageObj.Selector.M.Attr.S);
            } else {
                // Get text value
                textToExtract = $(messageObj.Selector.M.Value.S).first().text();
            }
            console.log(`Extracted price from page: ${textToExtract}`);

            // Parse float price using library
            let priceObj = currencyJs(textToExtract, {
                formatWithSymbol: true,
                symbol: messageObj.Currency.S
            });
            let priceStr = priceObj.format();

            // Check if product is cheaper
            if (priceObj.value <= parseFloat(messageObj.Threshold.N)) {
                let sendAlert = false;
                let previousPrice = parseFloat(messageObj.PrevPrice.N);

                // First time reduction
                if (previousPrice == -1.0) {
                    console.log(`First time reduction. Price for: ${messageObj.ProductName.S} is below threshold, currently: ${priceStr}`);
                    // Send email
                    var snsParams = {
                        Subject: "Price Point Alert",
                        Message: `${messageObj.ProductName.S} is below threshold\r\nDesired price: ${messageObj.Currency.S}${messageObj.Threshold.N}\r\nCurrent price: ${priceStr}\r\nLink: ${messageObj.Url.S}`,
                        TopicArn: topicArn
                    };
                    sendAlert = true;
                }
                // Further reduction
                else if (priceObj.value < previousPrice) {
                    console.log(`Further reduction. Price for: ${messageObj.ProductName.S} is below threshold, currently: ${priceStr}`);
                    // Send email
                    var snsParams = {
                        Subject: "Price Point Alert - Reduction",
                        Message: `${messageObj.ProductName.S} is below threshold\r\nDesired price: ${messageObj.Currency.S}${messageObj.Threshold.N}\r\nPrevious price: ${messageObj.Currency.S}${messageObj.PrevPrice.N}\r\nCurrent price: ${priceStr}\r\nLink ${messageObj.Url.S}`,
                        TopicArn: topicArn
                    };
                    sendAlert = true;
                }
                if (sendAlert) {
                    // Create promise and SNS service object
                    var publishTextPromise = new AWS.SNS({
                        apiVersion: '2010-03-31'
                    }).publish(snsParams).promise();

                    // Handle promise's fulfilled/rejected states
                    publishTextPromise.then(
                        function (data) {
                            console.log(`Message with ID ${data.MessageId} sent to the topic ${snsParams.TopicArn}`);

                            // Successful, set AlertSent = 1
                            var docClient = new AWS.DynamoDB.DocumentClient()

                            // Update the item, unconditionally,
                            var params = {
                                TableName: tableName,
                                Key: {
                                    "ProductTs": parseInt(messageObj.ProductTs.N),
                                },
                                UpdateExpression: "set PrevPrice = :p",
                                ExpressionAttributeValues: {
                                    ":p": priceObj.value,
                                },
                                ReturnValues: "UPDATED_NEW"
                            };

                            console.log("Updating the item...");
                            docClient.update(params, function (err, data) {
                                if (err) {
                                    console.error("Unable to update item. Error JSON:", JSON.stringify(err, null, 2));
                                } else {
                                    console.log("UpdateItem succeeded:", JSON.stringify(data, null, 2));
                                }
                            });
                        }).catch(
                        function (err) {
                            console.error(err, err.stack);
                        });
                } else {
                    console.log(`Price for: ${messageObj.ProductName.S} hasn't changed since last alert, currently: ${priceStr}`);
                }
                
            } else {
                console.log(`Price for: ${messageObj.ProductName.S} not cheap enough, currently: ${priceStr}`);
            }
        }
    });
};