from __future__ import absolute_import

import ldap
try:
    import simplejson as json
except:
    import json


class LDAP(object):
    basedn = "ou=People, dc=aristanetworks, dc=com"  #default ldap basedn
    host = "prod-ldap-slave-1.aristanetworks.com"  #default ldap hostname
    connection = None  #ldap connector object
    search_scope = ldap.SCOPE_SUBTREE  #.....no idea
    model = 'dwh.ldap_user'  #From dwh.models.py
    #Attributes that are of interest from OpenLDAP
    attributes = [
        'employeeNumber', 'uid', 'displayName', 'givenName', 'sn',
        'destinationIndicator', 'businessCategory', 'departmentNumber',
        'manager', 'title', 'mail', 'postalAddress', 'employeeType'
    ]
    __ldap_protocol_version = ldap.VERSION3  #use ldap v3; v2 is also useable if needed

    def __init__(self,
                 ldap_host=host,
                 basedn=basedn,
                 ldap_user_attributes=None):
        self.host = ldap_host
        self.basedn = basedn
        if ldap_user_attributes:
            self.attributes = ldap_user_attributes

        #Connect to ldap
        self.__connect_to_ldap()

    '''
    Function: __connect_to_ldap
    Purpose: Attempts to connect to an ldap server based on the host and basedn. Will return
    an error if it fails
    '''

    def __connect_to_ldap(self):
        try:
            self.connection = ldap.open(self.host)
            self.connection.protocol_verison = self.__ldap_protocol_version
        except ldap.LDAPError, e:
            print e

    '''
    Function: get_all_users
    Purpose: Gets all users available in a given basedn; will return an error if ldap connection
    fails.(&(uid=*)(!(active=blocked)))"
    '''

    def get_all_users(self, search_filter="(|(uid=*)(cn=*))"):
        return self.__search(search_filter)

    '''
    Function: __Search
    Purpose: This actually performs the ldap search on a given basedn with a given filter, and
    returns a dict as a resultset.
    '''

    def __search(self, search_filter):
        try:
            #Check LDAP connection
            if not self.connection:
                self.connect_to_ldap()

            ldap_result_id = self.connection.search(
                self.basedn, self.search_scope, search_filter, self.attributes)
            result_set = []
            while 1:
                result_type, result_data = self.connection.result(
                    ldap_result_id, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            return result_set
        except ldap.LDAPError, e:
            print e

    '''
    Function: get_user
    Purpose: For finding a sole user given a uid. This may need to be adjusted since contractors use
    cn as their username.
    '''

    def get_user(self, uid):
        if not uid:
            return "Invalid uid"
        else:
            search_filter = 'uid=%s' % uid
            return self.__search(search_filter)

    '''
    Function: get_Attributes
    Purpose: Returns a  dict of attributes fetched from LDAP
    '''

    def get_attributes(self):
        return self.attributes

    def construct_db_message(self, users):
        '''
        users[i][0][1]
        Essentially i is the user, 0 is dict containing the attributes dict, and 1 is the attributes dict
        i = user
        0 = dict { query_string,attributes{} }
        1 = attributes{}
        '''
        json_ish_data = []
        for i in range(0, len(users)):
            user_attributes = users[i][0][1]  # query attributes dict
            uid = None
            try:
                uid = user_attributes['uid'][0]
                if not uid:
                    try:
                        uid = users[i][0][0].split(',')[0].split('=')[1]
                        user_attributes['uid'] = []
                        user_attributes['uid'].append(cn)
                    except:
                        uid = None
            except KeyError as ke:
                print 'Key error %s' % str(ke)
                cn = users[i][0][0].split(',')[0].split('=')[1]
                uid = cn
                user_attributes['uid'] = []
                user_attributes['uid'].append(cn)
            user_object = {}
            for attribute, value in user_attributes.iteritems():  #cleanse data
                key = self.unfuck_key(
                    attribute)  #basically make some sense of the value
                #This snippet is in here because of mind fucking...I have no idea how this attribute is getting fetched
                if (key == "registeredAddress"):
                    continue
                #more mind fucking with empid
                if (key == "employee_id" and type(value[0]) is not int):
                    value[0] = value[0].strip()  #remove excess white space
                    if (not value[0]):  #check if empty string
                        value[0] = 0
                    if (type(value[0]) is not int):
                        try:
                            value[0] = int(value[0])
                        except:
                            print "This is some mind fuckage empID is %s so I'm setting it to 0" % value[
                                0]
                            value[0] = 0
                user_object[key] = value[0]
            json_ish_data.append(user_object)
        return json_ish_data

    '''
    this block is exclusive to arista ldap mainly to resolve confusion behind attribute 
    names, but I also made it so that the field name also conform to the DB field naming 
    convention
    '''

    def unfuck_key(self, key_name):
        fucked = key_name.lower()
        if (fucked == "destinationindicator"):
            return "status"
        elif (fucked == "businesscategory"):
            return "is_manager"
        elif (fucked == "departmentnumber"):
            return "department"
        elif (fucked == "employeenumber"):
            return "employee_id"
        elif (fucked == "givenname"):
            return "first_name"
        elif (fucked == "mail"):
            return "email"
        elif (fucked == "sn"):
            return "last_name"
        elif (fucked == "postaladdress"):
            return "location"
        elif (fucked == "displayname"):
            return "full_name"
        elif (fucked == "employeetype"):
            return "employee_type"
        else:
            return key_name

    def to_fixture(self, data, file_name="ldap.json"):
        fixture = []
        counter = 0
        for row in data.iteritems():
            entry = {}
            entry['model'] = self.model
            entry['pk'] = counter
            entry['fields'] = row[1]
            fixture.append(entry)
            counter += 1
        with open(file_name, 'w+') as fp:
            fp.write(json.dumps(fixture))

##### Testing block ######
"""
ldapconn = LDAP_Consumer()
#print ldapconn.get_user('sbailey')
users = ldapconn.get_all_users()
#user = users[1][0][1]
db_message = ldapconn.construct_db_message(users)
#pp = pprint.PrettyPrinter(indent=2)
#pp.pprint(db_message)
ldapconn.to_fixture(db_message)
"""
#For testing purposes
"""
for user,attrs in db_message.iteritems():
    print user
    for attr,val in attrs.iteritems():
        print "%s => %s" % (attr,val)

"""
