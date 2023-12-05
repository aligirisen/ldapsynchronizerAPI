"""
Author: Ali Riza Girisen
Date: 17/11/2023
"""
import subprocess, time, os
from ldap3 import *
import threading
sync_event = threading.Event()
shared_progress = 0
progress_lock = threading.Lock()

class MyThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None
    def run(self):
        result = shared_progress
        self.result = result


def set_default(variable):
    ldap_user_group_dn = "ou=User,ou=Groups,dc=lider,dc=com"
    ldap_spec_directory_dn = "" 
    create_directory = True
    create_group = True
    sync_computers = True
    ldap_clean_mode = True


    if variable == "ldap_user_group_dn":
        variable = ldap_user_group_dn
    elif variable == "ldap_clean_mode":
        variable = ldap_clean_mode
    elif variable == "create_directory":
        variable = create_directory
    elif variable == "ldap_spec_directory_dn":
        variable = ldap_spec_directory_dn
    elif variable == "create_group":
        variable = create_group
    elif variable == "sync_computers":
        variable = sync_computers

    return variable
def sync_data(ad_config, ldap_config, pref_config, input_dn, is_api):
    global shared_progress
    
    try:
        sync_event.set()

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

        config_list = ["ldap_clean_mode","ldap_spec_directory_dn","ldap_clean_search_dn","ldap_user_group_dn","sync_directory_mode","ad_computer_search_dn","ad_user_search_dn","create_group","sync_computers"]
        for variable in config_list:

            if variable == "ad_computer_search_dn" or variable == "ldap_clean_search_dn" or variable == "ad_user_search_dn":
                pref_config['ad_user_search_dn'] = ad_base_dn
                pref_config['ad_computer_search_dn'] = ad_base_dn
                pref_config['ldap_clean_search_dn'] = ldap_base_dn
            elif variable not in pref_config:
                pref_config[variable] = set_default(variable)
        
        #PREF
        sync_directory_mode = pref_config['sync_directory_mode']
        sync_computers = pref_config['sync_computers']
        create_group = pref_config['create_group']
        ad_user_search_dn = pref_config['ad_user_search_dn']
        ad_computer_search_dn = pref_config['ad_computer_search_dn']
        ldap_user_group_dn = pref_config['ldap_user_group_dn']
        ldap_spec_directory = pref_config['ldap_spec_directory_dn']
        ldap_clean_search_dn = pref_config['ldap_clean_search_dn']
        ldap_clean_mode = bool(pref_config['ldap_clean_mode'])

        ldap_existing_groups = []
        known_directories = []
        ou_name = ""

        def add_entry (conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf):
            if objectType == "Computer":
                object_class = ['top','person','inetOrgPerson','organizationalPerson']
                new_attributes = {
                    'objectClass': object_class,
                    'cn': cn,
                    'uid': sAMAccountName,
                    'sn': sn,
                    }
                result = conn.add(dn, attributes=new_attributes)
                return
            object_class = ['inetOrgPerson','organizationalPerson','top','person']
            new_attributes = {
                'objectClass': object_class,
                'cn': cn,
                'givenName': givenName,
                'sn': sn,
                'uid': sAMAccountName,
                'mail': mail,
                'homePostalAddress': homePostalAddress,
                'telephoneNumber': phoneNumber,
                }
            result = conn.add(dn, attributes=new_attributes)
            if not result:
                return returnValue(is_api, 'error', conn.result)

        def modify_entry (conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf):
            modification_dict = {}
            attributes_to_compare = {
                'givenName': givenName,
                'sn': sn,
                'telephoneNumber': phoneNumber,
                'mail': mail,
                'homePostalAddress':homePostalAddress,
                }
            for attribute_name, expected_value in attributes_to_compare.items():
                comparison = conn.compare(dn, attribute_name, expected_value)
                if comparison is False:
                    modification_dict[attribute_name] = [(MODIFY_REPLACE, expected_value)]
            if modification_dict:
                try:
                    conn.modify(dn, modification_dict)
                except Exception as e:
                    print(f"Failed to modify the LDAP entry: {e}")
                    return returnValue(is_api, 'error', e)
            for group in memberOf:
                group_dn = f"cn={group},{ldap_user_group_dn}"
                result = conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                if not result and create_group is True:
                    object_class = ['top','groupOfNames']
                    members = [dn]
                    grp_attributes = {
                            'objectClass': object_class,
                            'cn': group,
                            'description': group,
                            'member': members,
                            }
                    conn.add(group_dn, attributes=grp_attributes)


            search_filter_groups = f"(&(objectClass=groupOfNames)(member={dn}))"
            user_membership = conn.search(ldap_user_group_dn, search_filter=search_filter_groups)
            if user_membership:
                for group in ldap_existing_groups:
                    group_dn = f"cn={group},{ldap_user_group_dn}"
                    group_existing = conn.compare(group_dn, "member", dn)
                    if group_existing:
                        if group not in memberOf:
                            group_changes = {
                                    'member': [(MODIFY_DELETE, [dn])]
                                    }
                            result = conn.modify(group_dn, changes=group_changes)


        def search_lines(filename_ad, total_lines_ad, input_dn):
            global shared_progress

            user_counter,new_user_counter = 0,0
            spec_search = False
            server = Server(ldap_server, port=ldap_port, connect_timeout=2)
            conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
            dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf = " " , " ", " ", " ", " ", " ", " ", " "," " , []
            with open(filename_ad, 'r') as file:
                for line_number, line in enumerate(file, start=1):
                    if line.startswith('#') or line.startswith(' '):
                        if dn != " " and sAMAccountName != " " and cn != " " :
                            if input_dn and spec_search:#spec user modify
                                search_result = conn.search(dn, '(objectClass=person)')
                                if search_result:
                                    response = modify_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf,)
                                    print("Existing changes have been applied")
                                    return returnValue(is_api, 'success', 'Existing changes have been applied')
                                else:
                                    return returnValue(is_api, 'success', 'User is not existing on ldap')
                            elif not input_dn:
                                search_result = conn.search(dn, '(objectClass=person)')
                                if search_result:# user modify
                                    user_counter = user_counter + 1
                                    result = modify_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                                    if result is False: 
                                        return returnValue(is_api, 'error', conn.result)
                                else: #directory modify and add new user 
                                    dir_dn = f'{ou_name},{ldap_directory}'
                                    if dir_dn not in known_directories and ou_name:
                                        exist_directory = conn.search(dir_dn,'(objectClass=*)')
                                        if exist_directory:
                                            known_directories.append(f'{ou_name},{ldap_directory}')
                                        else:
                                            exist_directory = False
                                    else:
                                        exist_directory is True
                                    if exist_directory:
                                        filter_str = f'(uid={sAMAccountName})'
                                        exist_uid = conn.search(search_base=ldap_base_dn, search_filter=filter_str, search_scope=SUBTREE, attributes=['uid'])
                                        if exist_uid:
                                            entry = conn.entries[0]
                                            conn.delete(entry.entry_dn)
                                        result = add_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                                        if result is False:
                                            return returnValue(is_api, 'error', conn.result)
                                        new_user_counter = new_user_counter + 1

                                    elif sync_directory_mode and not exist_directory:
                                        groups_dn = ldap_base_dn
                                        for directory in reversed(org_unit_list):
                                            group_str = f"{directory},{groups_dn}"
                                            groups_dn = group_str
                                            groups_attributes = {
                                                    'objectClass': ['top','pardusLider', 'organizationalUnit'],
                                                    'description': directory,
                                                    }
                                            result = conn.add(group_str, attributes=groups_attributes)
                                            known_directories.append(f'{ou_name},{ldap_directory}')
                                        filter_str = f'(uid={sAMAccountName})'
                                        exist_uid = conn.search(search_base=ldap_base_dn, search_filter=filter_str, search_scope=SUBTREE, attributes=['uid'])
                                        if exist_uid:
                                            entry = conn.entries[0]
                                            conn.delete(entry.entry_dn)
                                        result = add_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                                        if result is False:
                                            return returnValue(is_api, 'error', conn.result)
                                        new_user_counter = new_user_counter + 1
                                        for group in memberOf:
                                            group_dn = f"cn={group},{ldap_user_group_dn}"
                                            conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                            dn,cn,sn,givenName,mail,homePostalAddress,phoneNumber,sAMAccountName,objectType,memberOf = " ", " ", " ", " ", " ", " ", " ", " "," ", []

                        elif input_dn and total_lines_ad == line_number:
                            print(f"User is not found !!")
                            if is_api is True:
                                return ({'status': 'success', 'message':'User is not found'})
                            return True
                        elif total_lines_ad == line_number:
                            print ("Number of users : ",user_counter)
                            print ("Number of new users : ",new_user_counter)
                            output = {'user': user_counter, 'new_user':new_user_counter}
                            if is_api is True:
                                return returnValue(True, 'success',f'Number of users: {user_counter} Number of new users:{new_user_counter}')
                            return True

                    elif line.startswith('dn:') and not spec_search :
                        dn = line.strip()
                        str_dn = dn.split(':',1)[1].strip()
                        components = str_dn.split(',')
                        formatted_components = []
                        org_unit_list = []
                        cn_counter = 0
                        for component in components:
                            component = component.strip()
                            if component.startswith('CN='):
                                cn_counter = cn_counter + 1
                                if cn_counter >= 2 :
                                    ou_name = ('ou=' + component[3:])
                                    formatted_components.append('ou=' + component[3:])

                                    if component[3:] not in org_unit_list:
                                        org_unit_list.append('ou=' + component[3:])


                            elif component.startswith('OU='):
                                formatted_components.append('ou=' + component[3:])
                                org_unit_list.append('ou=' + component[3:])

                        ou_name = ','.join(org_unit_list)
                        new_dn = ','.join(formatted_components)
                        
                        if ldap_spec_directory == "default" or ldap_spec_directory == "":#for creating new directory if it is not existing.
                            ldap_directory = ldap_base_dn
                        else:
                            ldap_spec_directories = ldap_spec_directory.split(",")
                            for directory in ldap_spec_directories:
                                org_unit_list.append(directory)
                           
                            ldap_directory = f"{ldap_spec_directory},{ldap_base_dn}"

                    elif line.startswith('cn:'):
                        cn = line.strip()
                        cn = content(cn)
                    elif line.startswith('sn:'):
                        sn = line.strip()
                        sn = content(sn)
                    elif line.startswith('givenName:'):
                        givenName = line.strip()
                        givenName = content(givenName)
                    elif line.startswith('sAMAccountName:'):
                        sAMAccountName = line.strip()
                        sAMAccountName = content(sAMAccountName)
                        dn = f"uid={sAMAccountName},{ou_name},{ldap_directory}"
                        if input_dn == dn:
                            spec_search = True
                            dn = input_dn
                    elif line.startswith('mail:'):
                        mail = line.strip()
                        mail = content(mail)
                    elif line.startswith('homePostalAddress:'):
                        homePostalAddress = line.strip()
                        homePostalAddress = content(homePostalAddress)
                    elif line.startswith('telephoneNumber:'):
                        phoneNumber = line.strip()
                        phoneNumber = content(phoneNumber)
                    elif line.startswith('objectClass:'):
                        objectClass = line.strip()
                        objectClass = content(objectClass)
                        if objectClass == "computer":
                            objectType = "Computer"
                    elif line.startswith('operatingSystem:'):
                        sn = line.strip()
                        sn = content(sn)
                    elif line.startswith('memberOf:'):
                        group = line.strip()
                        components = group.split(",")
                        group = components[0].split('=')[1]
                        if group == "Administrators":
                            group = "adminGroups"
                        elif group == "Domain Admins":
                            group = "domainAdminGroup"
                        elif not create_group:
                            group = ""
                        
                        if group:
                            memberOf.append(group)

                    progress = (line_number + 1) / total_lines_ad * 100
                    with progress_lock:
                        shared_progress = progress
                    print(f"Progress: {progress:.0f}%", end='', flush=True)
                    backspaces = len(f"Progress ({progress:.0f}%)")
                    print('\b' * backspaces, end='', flush=True)
                print()
            conn.unbind()
                    
        def cleanLdap(filename_ad, total_lines_ad):
            user_counter,deleted_user_counter = 0,0
            server = Server(ad_server, port=ad_port, connect_timeout=2)
            conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)
            dn,uid =" "," "
            with open(filename_ad, 'r') as file:
                for line_number, line in enumerate(file, start=1):
                    if line.startswith('#') or line.startswith(' '):
                        if uid != " " :
                            filter_str = f'(sAMAccountName={uid})'
                            res = conn.search(ad_base_dn, filter_str)
                            if conn.entries:
                                user_counter = user_counter + 1
                            else:
                                server_ldap = Server(ldap_server, port=ldap_port,connect_timeout=2)
                                conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
                                res = conn_ldap.delete(dn)
                                if res is True:
                                    deleted_user_counter += 1
                                else:
                                    return returnValue(is_api, 'error', conn_ldap.result)

                            dn,uid = " "," "
                        elif total_lines_ad == line_number:
                            print ("Number of users : ",user_counter)
                            print ("Number of deleted users : ",deleted_user_counter)
                            if is_api is True:
                                return  returnValue(True,'success', f'Number of deleted users:{deleted_user_counter}')
                            return True
                    
                    elif line.startswith('dn:'):
                        dn = line.strip()
                        dn = content(dn)
                    elif line.startswith('uid:'):
                        uid = line.strip()
                        uid = content(uid)

                    progress = (line_number + 1) / total_lines_ad * 100
                    print(f"Progress: {progress:.0f}%", end='', flush=True)
                    backspaces = len(f"Progress ({progress:.0f}%)")
                    print('\b' * backspaces, end='', flush=True)
                print()
            conn.unbind()


        def getLdapGroups():
            server = Server(ldap_server, port=ldap_port, connect_timeout=2)
            conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)

            search_filter = "(objectClass=groupOfNames)"
            result = conn.search(ldap_user_group_dn,search_filter,attributes=["cn"])
            for entry in conn.entries:
                ldap_existing_groups.append(entry.cn)
            conn.unbind()
        def returnValue(is_api, status, message):
            if is_api is True:
                return ({'status': status, 'message': message})
            elif is_api is False and status == 'success':
                return True
            elif is_api is False and status == 'error':
                return False

        def content(content):
            converted = content.split(": ")
            content = converted[1]
            return content



        start_time = time.time()
        delete_ldif = f'rm ad_users.ldif'
        if os.path.exists(delete_ldif):
            subprocess.run(delete_ldif, shell=True)

        command_ad = f'ldapsearch -x -D {ad_username} -w {ad_password} -H ldap://{ad_server}:{ad_port} -b {ad_user_search_dn} "(&(objectClass=person)(objectCategory=person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)))" -s sub -E pr=1000/noprompt cn sn telephoneNumber mail homePostalAddress givenName sAMAccountName memberOf > ad_users.ldif'
        result_ad = subprocess.run(command_ad, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Fetching - Active Directory Users...")
        if sync_computers is True:
            command_ad_computer = f'ldapsearch -x -b {ad_computer_search_dn} -H ldap://{ad_server}:{ad_port} -D {ad_username} -w {ad_password} "(objectClass=computer)" >> ad_users.ldif'
            print("Fetching - Active Directory Computers...")
            result_ad_computer = subprocess.run(command_ad_computer, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


        if result_ad.returncode == 0:
            print("Successfully fetched.")
            total_lines_ad = int(subprocess.check_output(["wc", "-l", "ad_users.ldif"]).split()[0])
            print(result_ad.stdout)
        else:
            print("Fetching failed program will execute with existing ldif file. Error:")
            print(result_ad.stderr)


        file_path = 'ad_users.ldif'
        print("Synchronization is in progress...")
        getLdapGroups()
        json_response = ""
        if input_dn is None:
            result = search_lines(file_path, total_lines_ad, input_dn)
            if ldap_clean_mode is True:
                json_response = result
            else:
                return result
        else:
            print("mode : the single user search")
            result = search_lines(file_path, total_lines_ad, input_dn)
            return result

        if ldap_clean_mode is True:
            delete_ldif = f'rm ldap_users.ldif'
            if os.path.exists(delete_ldif):
                subprocess.run(delete_ldif, shell=True)

            command_ldap = f'ldapsearch -x -D {ldap_admin_username} -w {ldap_admin_password} -H ldap://{ldap_server}:{ldap_port} -b {ldap_clean_search_dn} "(objectClass=person)" -s sub -E pr=1000/noprompt uid  > ldap_users.ldif'
            result_ldap = subprocess.run(command_ldap, shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            file_path = 'ldap_users.ldif'
            print("Fetching - openLDAP Users...")
            if result_ldap.returncode == 0:
                print("Successfully fetched.")
                total_lines_ldap = int(subprocess.check_output(["wc", "-l", "ldap_users.ldif"]).split()[0])
                print(result_ldap.stdout)
                print("Deletion of unmatched entries is in progress...")
                result = cleanLdap(file_path, total_lines_ldap)
                result['message'] = json_response['message'] + ' ' + result['message'] 
                return result
            else:
                print("Fetching failed program will execute with existing ldif file. Error:")
                print(result_ldap.stderr)

    finally:
        sync_event.clear()
