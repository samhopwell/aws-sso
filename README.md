# aws-sso
Python AWS SSO login helper.

This is a simple python package that will log into AWS SSO (using the AWS CLI and configured profiles) and then set environmental variables for the AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY/AWS_SESSION_TOKEN within that terminal. This make it easy to get credentials into the console without the need to constantly revisit the SSO login page and manual copy/paste credentials. This in conjunction with zshrc/bashrc allows for easy authentication anywhere. This does rely on you having the appropriate settings within "~/.aws/config", there is an example below along with an example of a function to put within zshrc/bashrc. 

You will need to install this module locally using setup tools. 

Example SSO configuration in "~/.aws/config"
```
[default]
region = eu-west-1
output = json
[profile ssoprofile]
sso_start_url = https://ssologinpage.awsapps.com/start
sso_region = eu-west-1
sso_account_id = 123456789123
sso_role_name = role_name
region = eu-west-1
output = json
```

Example zshrc/bashrc configuration

```
sso(){
    value=`python3 -m aws-sso -p $1`
    account_id=`echo $value | jq .account_id -r` 
    role_name=`echo $value | jq .role_name -r` 
    
    access_key_id=`echo $value | jq .accessKeyId -r` 
    secret_access_key=`echo $value | jq .secretAccessKey -r` 
    session_token=`echo $value | jq .sessionToken -r` 

    expiration=`echo $value | jq .expiration -r` 
    tput setaf 2
    
    echo "Account ID: $account_id"
    echo "Role Name:  $role_name"
    echo "Access Key: $access_key_id"
    echo "Expiration: $expiration"

    export AWS_ACCESS_KEY_ID=`echo $access_key_id`
    export AWS_SECRET_ACCESS_KEY=`echo $secret_access_key`
    export AWS_SESSION_TOKEN=`echo $session_token`
}
```
