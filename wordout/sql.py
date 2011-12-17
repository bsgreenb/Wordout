from django.db import connection, transaction

def dictfetchall(cursor):
    #returns all rows from a cursor as a dict
    desc = cursor.description
    return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
            ]



def display_referrer_for_identifier_sql(id, identifier_id):
    cursor = connection.cursor()
    cursor.execute('''

    SELECT wordout_request.id, wordout_request.referrer_id, count(wordout_request.id) as clicks, wordout_host.host_name, wordout_path.path_loc
    FROM wordout_request
    LEFT JOIN wordout_full_link
        ON wordout_full_link.id = wordout_request.referrer_id
    LEFT JOIN wordout_host
        ON wordout_full_link.host_id = wordout_host.id
    LEFT JOIN wordout_path
        ON wordout_full_link.path_id = wordout_path.id
    LEFT JOIN wordout_identifiers
        ON wordout_identifiers.id = wordout_request.referral_code_id
    WHERE
        wordout_identifiers.customer_id = %s AND wordout_identifiers.id = %s
    GROUP BY 
        wordout_request.referrer_id
    ORDER BY
        clicks DESC

    ''', (id, identifier_id))

    return dictfetchall(cursor)



def display_referrer_sql(id):
    cursor = connection.cursor()
    cursor.execute('''

    SELECT wordout_host.id, wordout_host.host_name, COUNT(distinct wordout_request.id) as clicks
    FROM wordout_host
    LEFT JOIN wordout_full_link
        ON wordout_full_link.host_id = wordout_host.id
    LEFT JOIN wordout_request
        ON wordout_full_link.id = wordout_request.referrer_id
    LEFT JOIN wordout_identifiers
        ON wordout_request.referral_code_id = wordout_identifiers.id
    WHERE
        wordout_identifiers.customer_id = %s
    GROUP BY
        wordout_host.id
    ORDER BY
        clicks DESC

    ''', [id])

    return dictfetchall(cursor)


def display_path_sql(id, host_id):
    cursor = connection.cursor()
    cursor.execute('''

    SELECT wordout_path.id, wordout_path.path_loc, wordout_host.host_name, wordout_host.id, COUNT(distinct wordout_request.id) as clicks
    FROM wordout_path
    LEFT JOIN wordout_full_link
        ON wordout_full_link.path_id = wordout_path.id
    LEFT JOIN wordout_host
        ON wordout_full_link.host_id = wordout_host.id
    LEFT JOIN wordout_request
        ON wordout_full_link.id = wordout_request.referrer_id
    LEFT JOIN wordout_identifiers
        ON wordout_request.referral_code_id = wordout_identifiers.id
    WHERE wordout_identifiers.customer_id = %s AND wordout_host.id = %s
    GROUP BY wordout_path.id
    ORDER BY clicks DESC

    ''', (id, host_id))
    return dictfetchall(cursor)
