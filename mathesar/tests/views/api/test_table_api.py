import pytest

from mathesar.models import Table
from mathesar.imports.csv import create_table_from_csv


def check_table_response(response_table, table, table_name):
    assert response_table['id'] == table.id
    assert response_table['name'] == table_name
    assert '/api/v0/schemas/' in response_table['schema']
    assert 'created_at' in response_table
    assert 'updated_at' in response_table
    assert len(response_table['columns']) == len(table.sa_column_names)
    for column in response_table['columns']:
        assert column['name'] in table.sa_column_names
        assert 'type' in column
    assert response_table['records'].startswith('http')
    assert '/api/v0/tables/' in response_table['records']
    assert response_table['records'].endswith('/records/')


def test_table_list(engine, csv_filename, client):
    """
    Desired format:
    {
        "count": 1,
        "results": [
            {
                "id": 1,
                "name": "Fairfax County Table List",
                "schema": "http://testserver/api/v0/schemas/1/",
                "created_at": "2021-04-27T18:43:41.201851Z",
                "updated_at": "2021-04-27T18:43:41.201898Z",
                "columns": [
                    {
                        "name": "mathesar_id",
                        "type": "INTEGER"
                    },
                    {
                        "name": "X",
                        "type": "VARCHAR"
                    },
                    # etc.
                ],
                "records": "http://testserver/api/v0/tables/3/records/"
            }
        ]
    }
    """
    table_name = 'Fairfax County Table List'
    
    with open(csv_filename, 'rb') as csv_file:
        create_table_from_csv(
            name=table_name,
            schema='Libraries',
            database_key='mathesar_db_test_database',
            csv_file=csv_file
        )
    table = Table.objects.get(name=table_name)
    response = client.get('/api/v0/tables/')
    response_data = response.json()
    response_table = None
    for table_data in response_data['results']:
        if table_data['name'] == table_name:
            response_table = table_data
            break
    assert response.status_code == 200
    assert response_data['count'] >= 1
    assert len(response_data['results']) >= 1
    check_table_response(response_table, table, table_name)


def test_table_detail(engine, csv_filename, client):
    """
    Desired format:
    One item in the results list in the table list view, see above.
    """
    table_name = 'Fairfax County Table Detail'

    with open(csv_filename, 'rb') as csv_file:
        create_table_from_csv(
            name=table_name,
            schema='Libraries',
            database_key='mathesar_db_test_database',
            csv_file=csv_file
        )
    table = Table.objects.get(name=table_name)
    response = client.get(f'/api/v0/tables/{table.id}/')
    response_table = response.json()
    assert response.status_code == 200
    check_table_response(response_table, table, table_name)
