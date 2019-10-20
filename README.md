
# Price Point

Price Point scrapes webpages, extracting the price of a product. It will email you when the product is below your desired price, as well as any subsequent price drops. It checks every day at 05:00 UTC (this can be changed in the `events.Rule` definition). This is all should run nicely in the AWS free tier

## Pre-requisites
- AWS account (with access credentials setup on your computer)
- Python3
- AWS CDK
- npm

## Initial setup

### Set up venv:

```
$ python -m venv .env
```
### Activate venv

Mac/Linux:

```
$ source .env/bin/activate
```

Windows:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, install the required dependencies

```
$ pip install -r requirements.txt
```

### Bootstrap CDK

**Only needed if you haven't used CDK before**

Info from here https://cdkworkshop.com/20-typescript/20-create-project/500-deploy.html#bootstrapping-an-environment: 
```
The first time you deploy an AWS CDK app into an environment (account/region), you’ll need to install a “bootstrap stack”. This stack includes resources that are needed for the toolkit’s operation. For example, the stack includes an S3 bucket that is used to store templates and assets during the deployment process.

You can use the cdk bootstrap command to install the bootstrap stack into an environment:
```


```
$ cdk bootstrap
```

### npm

Change directory into `assets/` and run

```
npm install
```

### Enter your email address

Edit app.py and replace `'[Your email here]'` with the email you want the alerts sent to. (AWS will send you an email when you deploy the stack - You'll need to confirm the subscription to SNS to recieve alerts

### Deploy 

Now you've installed/setup everything, deploy the stack:

```
cdk deploy
```

## Adding products to Price Point

To add a product to Price Point, you'll need the URL of the page containing the price, and the DOM selector of the element. I usually visit the page and test the selector in the console with `document.querySelector([selector string])`. 

Once you've got your selector, upload the product to DynamoDB (you'll need the name of the DynamoDB table which CDK deployed):

```
python .\upload.py  "[URL]" "[DOM selector]" "[Product name]" "[Currency symbol]" [Desired price] "[DynamoDB table name]"
```

And that's it - now wait for some emails :)