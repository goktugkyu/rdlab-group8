#!/usr/bin/env python

import os

import os.path



import irods

from irods.session import iRODSSession

from irods.password_obfuscation import encode



# iRODS connection config

config = """

{

    "irods_host": "set.irods.icts.kuleuven.be",

    "irods_port": 1247,

    "irods_zone_name": "set",

    "irods_authentication_scheme": "native",

    "irods_encryption_algorithm": "AES-256-CBC",

    "irods_encryption_salt_size": 8,

    "irods_encryption_key_size": 32,

    "irods_encryption_num_hash_rounds": 8,

    "irods_user_name": "r1022717",

    "irods_ssl_ca_certificate_file": "",

    "irods_ssl_verify_server": "cert",

    "irods_client_server_negotiation": "request_server_negotiation",

    "irods_client_server_policy": "CS_NEG_REQUIRE",

    "irods_default_resource": "default",

    "irods_cwd": "/set/home",

    "irods_authentication_uid": 1000

}

"""



# <<< PUT YOUR MANGO PASSWORD HERE >>>

password = "IhvRXeCPLQVEUj0hZLKYkUebgbGO1VyW"





def put(path: str, contents: str) -> None:

    """Write contents to a file, creating parent dir if needed."""

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:

        f.write(contents)





def main():

    if irods.__version__.startswith(("1.", "0.")):

        print(

            "Warning: old python-irodsclient detected "

            f"({irods.__version__}), please upgrade to >= 2.0.0 if possible."

        )



    env_file = os.getenv(

        "IRODS_ENVIRONMENT_FILE",

        os.path.expanduser("~/.irods/irods_environment.json"),

    )



    # Write environment JSON and encoded password file

    put(env_file, config)

    put(iRODSSession.get_irods_password_file(), encode(password, uid=1000))



    print("✅ Wrote iRODS environment and password files.")

    print(f"  Env file: {env_file}")

    print(f"  Password file: {iRODSSession.get_irods_password_file()}")





if __name__ == "__main__":

    main()


