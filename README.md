
# Welcome to your CDK Python project!

This is a simple project for Python development with CDK.
It leverages Amazon Transcribe and Amazon Comprehend.

A. General instructions

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the .env
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .env
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .env/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .env\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful CDK commands 

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation


B.	Pre-requisites
The CDK must be installed on your laptop.
See https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html for more details on how to do that.

C.	Install

1.	Deploy the CDK Toolkit stack into your AWS environment
This step only has to be performed once if you never used the CDK before in your AWS account.

$ cdk bootstrap  

Note: if you use a specific AWS profile (defined in your <HOME>/.aws directory) the command would be ‘cdk bootstrap  
--profile <your AWS profile>’

The command output should look like this and give confirmation that the environment has been bootstrapped.

 

2.	Deploy the CDK stack to your AWS environment
$ cdk deploy

Note: if you use a specific AWS profile (defined in your <HOME>/.aws directory) the command would be ‘cdk deploy 
--profile <your AWS profile>’

The command output should look like this and give confirmation that the stack has been successfully deployed.
 

D.	Post-install
Transcribe is not supported yet by the CDK so the custom vocabulary has to be created manually.
Log in on the AWS Console on your account and select Amazon Transcribe among the list of services.
Create a custom vocabulary called custom-vocab_nl-NL, or replace “nl-NL” by the specific language that you want to transcribe from as illustrated on this picture :
 
The custom vocabulary has to be uploaded to S3 first (direct upload fails repeatedly in the console).


Enjoy!
