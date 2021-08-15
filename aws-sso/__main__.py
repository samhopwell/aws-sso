import configparser
import argparse
import subprocess
import json
from pathlib import Path
from botocore.exceptions import ParamValidationError, ClientError
import boto3
from datetime import datetime, timezone
from dateutil import parser


boto_client = boto3.client("sso")
config_path_default = Path.joinpath(Path.home(), ".aws/config")
cache_dir = Path.joinpath(Path.home(), ".aws/sso/cache/")


class ProfileError(Exception):
    pass


def exec_login(sso_profile):
    return subprocess.run(
        [f"aws sso login --profile {sso_profile}"],
        shell=True,
        check=True,
        capture_output=True,
    )


def get_role_session_credentials(sso_profile, account_id, role_name):
    access_token = __get_access_token(sso_profile)
    response = boto_client.get_role_credentials(
        accessToken=access_token, accountId=account_id, roleName=role_name
    )

    return response["roleCredentials"]


def __get_access_token(sso_profile):
    count = 0
    while True:
        try:
            access_token = get_sso_access_token()
            # Verify access token is still valid
            get_account_list(access_token)
            return access_token
        except (ParamValidationError, ClientError):
            if count >= 1:
                raise RuntimeError("Unable to retrieve SSO Access Token")
            else:
                count += 1
                exec_login(sso_profile)
                continue


def __get_file_contents(file_path):
    p = Path(file_path).expanduser()
    if p.exists() and p.is_file():
        return p.read_text()
    else:
        raise FileNotFoundError(f"File not found: {file_path}")


def get_account_list(access_token):
    response = boto_client.list_accounts(accessToken=access_token)
    return response["accountList"]


def get_sso_access_token(cache_dir_override=None):
    if cache_dir_override is None:
        cache_dir = cache_dir_override
    keys = {"accessToken", "expiresAt"}
    for file in __get_json_files(cache_dir):
        content = json.loads(__get_file_contents(file))
        if content.keys() >= keys and is_not_expired(content["expiresAt"]):
            return content["accessToken"]


def int_to_datetime(int_datetime):
    return datetime.fromtimestamp(int_datetime / 1e3, tz=timezone.utc)


def is_not_expired(expires_at):
    expiration_date = parser.parse(expires_at)
    return expiration_date > datetime.now(timezone.utc)


def minutes_from_now(expires_at):
    expiration_date = parser.parse(expires_at)
    return int((expiration_date - datetime.now(timezone.utc)).total_seconds() / 60)


def __get_json_files(dir):
    p = Path(dir).expanduser()
    files = []
    if p.exists() and p.is_dir():
        for file in p.iterdir():
            if file.suffix == ".json":
                files.append(file)
    else:
        raise NotADirectoryError(f"Directory not found: {dir}")
    return files


def get_config(sso_profile, config_path_override=None):
    if config_path_override:
        config_path = config_path_override
    else:
        config_path = config_path_default

    if not Path.exists(config_path):
        raise ProfileError("Config file does not exist")

    config = configparser.ConfigParser()
    config.read(config_path)

    try:
        account_id = config[f"profile {sso_profile}"]["sso_account_id"]
        role_name = config[f"profile {sso_profile}"]["sso_role_name"]
        return account_id, role_name
    except KeyError:
        raise ProfileError("Profile does not exist")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-p", "--profile", required=True, help="Named profile for AWS SSO login"
    )

    arg_dict = vars(arg_parser.parse_args())

    sso_profile = arg_dict["profile"]
    account_id, role_name = get_config(sso_profile=sso_profile)

    print(sso_profile)
    print(account_id)
    print(role_name)

    exit(0)

    exec_login(sso_profile=sso_profile)
    role_session_credentials = get_role_session_credentials(
        sso_profile=sso_profile, account_id=account_id, role_name=role_name
    )

    role_session_credentials

    print(json.dumps(role_session_credentials))
# return int((expiration_date - datetime.now(timezone.utc))
#                .total_seconds() / 60)

# credentials_file_path = helper.get_env_var("AWS_SHARED_CREDENTIALS_FILE", None)
# account_id = helper.parse_role_arn(cred["role_arn"])["account_id"]
# role_name = helper.parse_role_arn(cred["role_arn"])["role_name"]
# expiration = helper.int_to_datetime(cred["expiration"]).isoformat()
# x_minutes = helper.minutes_from_now(expiration)
# print("omg")
# print(f"Temporary credentials added to {credentials_file_path}")
# print(f"Account: {account_id}")
# print(f"Role:    {role_name}")
# print(f"Expires: {expiration} ({x_minutes}m)")
