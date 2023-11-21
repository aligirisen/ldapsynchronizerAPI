# ldapsynchronizerAPI
synchronizer API for active directory to ldap


## Config Guide ( Connection configs are required as expected, except pref_conf which is existing for detailed settings )

## Test your connection and credentials.
/syncapp/test

## Sync Active Directory server to lider.
/syncapp/sync


### Groups directory (cn=DnsAdmins ...)
``` ldap_user_group_dn = ou=User,ou=Groups,dc=lider,dc=com ```


### Get all entries and tree to new directory. (ldap_spec_directory_dn = ou=TestDirectory)
``` ldap_spec_directory_dn = ```


### Used to narrow down the directory field to be searched.
```
ad_user_search_dn = cn=Builtin,dc=ornek,dc=local
ad_computer_search_dn = dc=ornek,dc=local
```


### Create directories which are does not exist in openldap site.
``` create_directory = True ```

### Create groups which are does not exist in openldap site. (check up groups directory in pref_config)
```create_group```

### Sync computers mode
``` sync_computer = True ```

### Example Request Body:
```
{
    "ad_config": {
        "ad_server": "win.ornek.local",
        "ad_port": 389,
        "ad_username": "cn=Administrator,cn=Users,dc=ornek,dc=local",
        "ad_password": "123456A.",
        "ad_base_dn": "dc=ornek,dc=local"
    },
    "ldap_config": {
        "ldap_base_dn": "dc=ldap,dc=local",
        "ldap_server": "192.168.1.150",
        "ldap_admin_username": "cn=admin,dc=ldap,dc=com",
        "ldap_admin_password": "123456",
        "ldap_port": 389
    },
    "pref_config": {
        "ldap_spec_directory_dn": "ou=Synchronizedtest"
    },
    "input_dn": "uid=AC150589,ou=Europa,ou=IT Team,dc=ldap,dc=com"
}
```
