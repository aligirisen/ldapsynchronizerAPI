"""
Author: Ali Riza Girisen
Date: 17/11/2023
"""
import subprocess, time
from ldap3 import *

def test_connections(ad_config, ldap_config):

    #ACTIVE DIRECTORY CONNECTION BLOCK
    ad_server = ad_config['ad_server']
    ad_port = int(ad_config['ad_port'])
    ad_username = ad_config['ad_username']
    ad_password = ad_config['ad_password']
    ad_base_dn = ad_config['ad_base_dn']

    #OPENLDAP CONNECTION BLOCK
    ldap_server = ldap_config['ldap_server']
    ldap_port = int(ldap_config['ldap_port'])
    ldap_admin_username = ldap_config['ldap_admin_username']
    ldap_admin_password = ldap_config['ldap_admin_password']
    ldap_base_dn = ldap_config['ldap_base_dn']

    test_user_dn = 'cn=testtestconnections,' + ldap_base_dn
    test_ou_dn = 'ou=testtestOrganizationalUnit,' + ldap_base_dn


    def addUser(dn):
        object_class = ['inetOrgPerson','organizationalPerson','top','person']
        new_attributes = {
            'objectClass': object_class,
            'cn': dn,
            'uid': dn,
            'sn': dn,
            }
                
        result_add = conn.add(dn, attributes=new_attributes)
        return result_add

    # default test 
    server = Server(ldap_server, ldap_port)
    conn = Connection(server,user=ldap_admin_username,password=ldap_admin_password)

    if not conn.bind():
        print('Failed to bind to the LDAP server.')
        return False
    else:
        print('Connected to the LDAP server successfully. Necessary privileges are checking up...')
        try:
            if not conn.search(test_ou_dn, '(objectClass=*)'):
                groups_attributes = {
                      'objectClass': ['top', 'organizationalUnit','pardusLider'],
                }
                result_ou = conn.add(test_ou_dn, attributes=groups_attributes)
                if result_ou:
                    print("Passed -add organiztional unit-")
                    ou_test = conn.delete(test_ou_dn)
                    if ou_test:
                        print("Passed -delete organizational unit-")
                    else:
                        print("Failed -delete organizational unit-")
                        return False
                else:
                    print("Failed -add organizational unit-")
                    return False
            else:
                ou_test = conn.delete(test_ou_dn)
                if ou_test:
                    print("Passed -delete organizational unit-")
                    groups_attributes = {
                        'objectClass': ['top', 'organizationalUnit','pardusLider'],
                    }

                    result = conn.add(test_ou_dn, attributes=groups_attributes)
                    if result:
                        conn.delete(test_ou_dn)
                        print("Passed -add organiztional unit-")
                    else:
                        print("Failed -add organizational unit-")
                        return False
                else:
                    print("Failed -delete organizational unit-")
                    return False

            result = conn.search(test_user_dn, '(objectClass=person)')
            if result:
                result_delete = conn.delete(test_user_dn)
                if result_delete:
                    print("Passed -delete entry-")
                    result_add = addUser(test_user_dn)
                    if result_add:
                        print("Passed -add entry-")
                        conn.delete(test_user_dn)
                    else:
                        print("Failed -add entry-")
                        return False
                else:
                    print("Failed -delete entry-")
                    return False

            else:
                result_add = addUser(test_user_dn)
                if result_add:
                    print("Passed -add entry-")
                    result_delete = conn.delete(test_user_dn)
                    if result_delete:
                        print("Passed -delete entry-")
                    else:
                        print("Failed -delete entry-")
                        return False
                else:
                    print(test_user_dn)
                    print("Failed -add entry-")
                    return False
        except Exception as e:
            print(f'An error occurred: {str(e)}')
            return False
        finally:
            conn.unbind()



    server_ad = Server(ad_server, ad_port)
    conn_ad = Connection(server_ad,user=ad_username,password=ad_password)

    if not conn_ad.bind():
        print('Failed to bind to the Active Directory.')
        return False
    else:
        print('Connected to the Active Directory successfully.')
        try:
            search_filter = '(objectClass=person)'
            search_base = ad_base_dn
            search_result_ad = conn_ad.search(search_base, search_filter, SUBTREE)

            if search_result_ad:
                print("Passed -Active Directory-")
            else:
                print("Failed -Active Directory-")
                return False
        except Exception as e:
            print(f'An error occured: {str(e)}')
            return False
        finally:
            conn_ad.unbind()
    return True
# Create your tests here
