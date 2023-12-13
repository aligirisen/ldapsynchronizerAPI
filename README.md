# Active Directory to openldap synchronize tool

Transfer and update operations for users and computers in the active directory to openldap. It creates policies and groups, but cannot add authorizations or restrictions to groups and policies.

## Installation
- git clone https://github.com/aligirisen/ldapsynchronizerAPI.git
- For Debian
    - cd ldapsynchronizerAPI
    - dpkg-buildpackage -us -uc
    - cd .. && sudo dpkg -i syncapi_1.0-1_all.deb
- When the application is installed, it starts to run as a system service and uses port 8000.

## Connection Config
- `/etc/syncapi/config/config.ini` the file where to enter the credentials and informations about of Active Directory and openldap server.

- After completing credentials, hit the test with`python3 /usr/bin/syncapi/manage.py test` or (if system service or api running)`/syncapp/sync/test`


## Preference Config

- `/etc/syncapi/config/pref_config.ini` path of the preference config file.
- Preferences:
    - `sync_directory = True` | creating a directory that exists on the active directory side but does not exist on the openldap side.
    - `create_group = True` | creating a group that exists on the active directory side but does not exist on the openldap side. (Example: DnsAdmins)
    - `sync_computers = True` | synchronization of computers.
    - **`ldap_group_dn = ou=Groups,dc=example,dc=com`** | DN of the directory containing the groups.
    - `ldap_clean_mode = True` | enables the deletion of users that have been deleted from the active directory in openLDAP as well.
    - `ldap_clean_search_dn = ` | Specifies the directory where the deleted users from the active directory will be deleted in openLDAP. To apply to a specific directory, for example: `ou=Istanbul,ou=Turkey,dc=example,dc=com`
    - `ldap_spec_directory_dn = ` | used to move the entire tree from the active directory to a new directory in openLDAP. for example: `ou=From Active Directory,dc=example,dc=com`
    - `time_zone = Europa/Istanbul` | used when returning the start and end times of the process.
    - `ad_user_search_dn = ` | used to update specific users in the active directory. For example: `ou=IT Team,dc=example,dc=com`
    - `ad_computer_search_dn = ` | used to update specific computers in the active directory. for example: `ou=Computers Poland,dc=example,dc=com`


## Running Standalone Source Code
`python3 manage.py source`
 
`python3 manage.py source "input_dn"`

For testing : `python3 manage.py test`



## Instance Request and Endpoints

- The request sent for the deletion of users deleted from the active directory by openLDAP after synchronization.

### Endpoint I
POST /syncapp/sync
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
        "ldap_clean_mode": True
    }
}
```
If just update an entry instead of all the tree. Use entry's DN.
```
"input_dn": "cn=Ali Riza Girisen,ou=Users,dc=example,dc=com"
```

### Endpoint II
POST /syncapp/test
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
    }
}
```
### Endpoint III
GET /syncapp/sync/status
```
no parameter
```