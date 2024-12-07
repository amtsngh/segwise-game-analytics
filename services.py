import json
import psycopg2
from models import get_connection

class GameDataService:

    @staticmethod
    def get_data(req):
        sql = GameDataService.build_sql(req)
        connection = get_connection()
        with connection.cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            row_count = GameDataService.get_row_count(req, results)
            results_for_page = GameDataService.cut_results_to_page_size(req, results)
        results_as_dicts = [dict(zip(columns, row)) for row in results_for_page]
        return results_as_dicts, row_count

    @staticmethod
    def build_sql(req):
        select_sql = GameDataService.create_select_sql(req)
        from_sql = ' FROM game_data '
        where_sql = GameDataService.create_where_sql(req)
        group_by_sql = GameDataService.create_group_by_sql(req)
        order_by_sql = GameDataService.create_order_by_sql(req)
        limit_sql = GameDataService.create_limit_sql(req)
        sql = f"{select_sql}{from_sql}{where_sql}{group_by_sql}{order_by_sql}{limit_sql}"
        print(sql)
        return sql

    @staticmethod
    def create_select_sql(req):
        row_group_cols = req.get('rowGroupCols', [])
        value_cols = req.get('valueCols', [])
        group_keys = req.get('groupKeys', [])

        if GameDataService.is_doing_grouping(row_group_cols, group_keys):
            cols_to_select = []

            row_group_col = row_group_cols[len(group_keys)]
            cols_to_select.append(row_group_col['field'])

            for value_col in value_cols:
                cols_to_select.append(f"{value_col['aggFunc']}({value_col['field']}) as {value_col['field']}")

            return 'SELECT ' + ', '.join(cols_to_select)

        return 'SELECT *'

    @staticmethod
    def create_where_sql(req):
        row_group_cols = req.get('rowGroupCols', [])
        group_keys = req.get('groupKeys', [])
        filter_model = req.get('filterModel', {})

        where_parts = []

        for index, key in enumerate(group_keys):
            col_name = row_group_cols[index]['field']
            where_parts.append(f"{col_name} = '{key}'")

        for key, item in filter_model.items():
            where_parts.append(GameDataService.create_filter_sql(key, item))

        if where_parts:
            return ' WHERE ' + ' AND '.join(where_parts)
        return ''

    @staticmethod
    def create_filter_sql(key, item):
        filter_type = item.get('filterType')
        filter_type_map = {
            'text': GameDataService.create_text_filter_sql,
            'number': GameDataService.create_number_filter_sql
        }
        return filter_type_map.get(filter_type, lambda k, i: 'TRUE')(key, item)

    @staticmethod
    def create_number_filter_sql(key, item):
        type_map = {
            'equals': f"{key} = {item['filter']}",
            'notEqual': f"{key} != {item['filter']}",
            'greaterThan': f"{key} > {item['filter']}",
            'greaterThanOrEqual': f"{key} >= {item['filter']}",
            'lessThan': f"{key} < {item['filter']}",
            'lessThanOrEqual': f"{key} <= {item['filter']}",
            'inRange': f"({key} >= {item['filter']} AND {key} <= {item['filterTo']})"
        }
        return type_map.get(item.get('type'), 'TRUE')

    @staticmethod
    def create_text_filter_sql(key, item):
        type_map = {
            'equals': f"{key} = '{item['filter']}'",
            'notEqual': f"{key} != '{item['filter']}'",
            'contains': f"{key} LIKE '%{item['filter']}%'",
            'notContains': f"{key} NOT LIKE '%{item['filter']}%'",
            'startsWith': f"{key} LIKE '{item['filter']}%'",
            'endsWith': f"{key} LIKE '%{item['filter']}'"
        }
        return type_map.get(item.get('type'), 'TRUE')

    @staticmethod
    def create_group_by_sql(req):
        row_group_cols = req.get('rowGroupCols', [])
        group_keys = req.get('groupKeys', [])

        if GameDataService.is_doing_grouping(row_group_cols, group_keys):
            row_group_col = row_group_cols[len(group_keys)]
            return f" GROUP BY {row_group_col['field']}"
        return ''

    @staticmethod
    def create_order_by_sql(req):
        sort_model = req.get('sortModel', [])
        sort_parts = [f"{item['colId']} {item['sort']}" for item in sort_model]
        if sort_parts:
            return ' ORDER BY ' + ', '.join(sort_parts)
        return ''

    @staticmethod
    def create_limit_sql(req):
        start_row = req.get('startRow', 0)
        end_row = req.get('endRow', 100)
        page_size = end_row - start_row
        return f" LIMIT {page_size + 1} OFFSET {start_row}"

    @staticmethod
    def is_doing_grouping(row_group_cols, group_keys):
        return len(row_group_cols) > len(group_keys)

    @staticmethod
    def get_row_count(req, results):
        if not results:
            return None
        current_last_row = req['startRow'] + len(results)
        return current_last_row if current_last_row <= req['endRow'] else -1

    @staticmethod
    def cut_results_to_page_size(req, results):
        page_size = req['endRow'] - req['startRow']
        return results[:page_size] if len(results) > page_size else results