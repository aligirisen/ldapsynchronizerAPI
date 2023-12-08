#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys, configparser
from syncapp.sync import sync_ad,test_conn


def GetConfigs():

    ad_config,ldap_config,pref_config = {},{},{}

    config_path = "/etc/syncapi/config/config.ini"
    config_pref_path = "/etc/syncapi/config/pref_config.ini"

    config = configparser.ConfigParser()
    config.read(config_path)

    config_pref = configparser.ConfigParser()
    config_pref.read(config_pref_path)
    print(config_pref_path)

    #PREF
    pref_config["sync_directory_mode"] = config_pref.get('PREF','sync_directory')
    pref_config["ad_user_search_dn"] = config_pref.get('PREF','ad_user_search_dn')
    pref_config["ad_computer_search_dn"] = config_pref.get('PREF','ad_computer_search_dn')
    pref_config["ldap_directory_domain_dn"] = config_pref.get('PREF','ldap_default_directory_dn')
    pref_config["ldap_user_group_dn"] = config_pref.get('PREF','ldap_user_group_dn')
    pref_config["ldap_spec_directory"] = config_pref.get('PREF','ldap_spec_directory_dn')
    pref_config["create_group"] = config_pref.get('PREF', 'create_group')
    pref_config["sync_computers"] = config_pref.get('PREF', 'sync_computers')

    pref_config["ldap_clean_mode"] = config_pref.get('PREF', 'ldap_clean_mode')
    pref_config["ldap_clean_search_dn"] = config_pref.get('PREF', 'ldap_clean_search_dn')
    #ACTIVE DIRECTORY CONNECTION BLOCK
    ad_config["ad_server"] = config.get('AD','ad_server')
    ad_config["ad_port"] = int(config.get('AD','ad_port'))
    ad_config["ad_username"] = config.get('AD','ad_username')
    ad_config["ad_password"] = config.get('AD', 'ad_password')
    ad_config["ad_base_dn"] = config.get('AD','ad_base_dn')

    #OPENLDAP CONNECTION BLOCK
    ldap_config["ldap_server"] = config.get('LDAP','ldap_server')
    ldap_config["ldap_port"] = int(config.get('LDAP','ldap_port'))
    ldap_config["ldap_admin_username"] = config.get('LDAP','ldap_admin_username')
    ldap_config["ldap_admin_password"] = config.get('LDAP','ldap_admin_password')
    ldap_config["ldap_base_dn"] = config.get('LDAP','ldap_base_dn')

    return ad_config,ldap_config,pref_config

def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "source":
            ad_config, ldap_config, pref_config = GetConfigs()
            sync_ad.sync_data(ad_config,ldap_config,pref_config,None, False)
        elif sys.argv[1].startswith("cn") or sys.argv[1].startswith("uid"):
            ad_config, ldap_config, pref_config = GetConfigs()
            sync_ad.sync_data(ad_config,ldap_config,pref_config,sys.argv[1], False)
        elif sys.argv[1] == "test":
            ad_config, ldap_config, pref_config = GetConfigs()
            test_conn.test_connections(ad_config, ldap_config)
    else:
        """Run administrative tasks."""
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'syncapi.settings')
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ) from exc
        execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
