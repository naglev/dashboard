import re
from bs4 import BeautifulSoup

def software1_text_processor(server_response):

    # Text rows to list items
    query_rows = server_response.split('\n')

    # Remove empty rows (filter object needs to be transformed to a list)
    filtered_query_rows = list(filter(None, query_rows))

    # Regex patterns
    pattern_feature = re.compile(r'Users of (?P<feature>\w+):  \(Total of (?P<issued>\d+) licenses? issued;  Total of (?P<used>\d+)')
    pattern_user = re.compile(r'(?P<user>[a-z-]{1,}) (?P<user_comp>BU2\w\d{4}).corp.knorr-bremse.com')

    license_list = []

    # Fill up the empty list with regex matches
    for row in filtered_query_rows:
        match = re.search(pattern_feature, row)
        if match:
            
            license_list.append([match.group('feature'), int(match.group('issued')), int(match.group('used'))])

        # If feature in use --> append the last item in the license_list with user row list
        match_user = re.search(pattern_user, row)
        if match_user:
            license_list[-1].append([match_user.group('user'),match_user.group('user_comp')])

            # Adding the nr. of used hpc licenses per user
            if license_list[-1][0] == 'xxx':
                match_hpc_nr = re.search(r'\d+ licenses', row)
                license_list[-1][-1].append(match_hpc_nr.group())
    
    # Output format: [..., ['feature', issued, used, [user_1_name, user_1_comp], [user_2_name, user_2_comp]], ...]      
    return license_list


def software2_text_processor(server_response):
    
    # Text rows to list items
    query_rows = server_response.split('\n')

    # Remove empty rows (filter object needs to be transformed to a list)
    filtered_query_rows = list(filter(None, query_rows))

    # Regex patterns
    pattern_feature = re.compile(r'Users of (?P<feature>\w+):  \(Total of (?P<issued>\d+) licenses? issued;  Total of (?P<used>\d+)')
    pattern_user = re.compile(r'(?P<user>[a-z-]{3,}) (?P<user_comp>BU2\w\d{4})')
    pattern_abcd_feature = re.compile(r'XXX:([^ ]*)')
    pattern_license_nr = re.compile(r'\d+ licenses')

    license_list = []

    for row in filtered_query_rows:
        match_feature = re.search(pattern_feature, row)
        if match_feature:
            license_list.append([match_feature['feature'], int(match_feature['issued']), int(match_feature['used'])])
        
        match_user = re.search(pattern_user, row)
        if match_user:
            license_list[-1].append([match_user.group('user'), match_user.group('user_comp')])
            
            if license_list[-1][0] == 'XXX':
                match_abcd_feature = re.search(pattern_abcd_feature, row)
                license_list[-1][-1].append(match_abcd_feature.group(1))
                
                match_license_nr = re.search(pattern_license_nr, row)
                if match_license_nr:
                    license_list[-1][-1].append(match_license_nr.group())

    return license_list


def software3_text_processor(server_response):
    
    soup = BeautifulSoup(server_response,'lxml')

    features = soup.select('feature')

    license_list = []

    for feature in features:
        if 'XXX' in feature['name']:
            if feature['name'] == 'XXX':
                feature_name = 'BASIC'
            else:
                feature_name = feature['name'].split('_')[1]
            license_list.append([feature_name, int(feature['total_licenses']), int(feature['used_licenses'])])
        
        users = feature.select('used user')
        if users:
            for user in users:
                if '_' in user['host']:
                    user_comp = user['host'].split('_')[0]
                else:
                    user_comp = user['host']
                license_list[-1].append([user['name'], user_comp])

    return license_list


def software4_text_processor(server_response):
    
    soup = BeautifulSoup(server_response,'lxml')

    features = soup.select('feature')

    license_list = []

    for feature in features:
        feature_name = feature['name'].split('-')[1]

        license_list.append([feature_name, int(feature['total_licenses']), int(feature['occupied_licenses'])])
            
        users = feature.select('used user')
        if users:
            for user in users:
                if '_' in user['host']:
                    user_comp = user['host'].split('_')[0]
                else:
                    user_comp = user['host']
                license_list[-1].append([user['name'], user_comp])

    return license_list
