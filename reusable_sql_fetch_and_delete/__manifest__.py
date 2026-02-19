# -*- coding: utf-8 -*-
{
    "name": "Reusable SQL Fetch and Delete",
    "summary": """
        This module provides a reusable method for deleting records from any model in Odoo.
        It allows you to delete records directly via SQL queries, bypassing ORM-related foreign key constraints.
        The method can be used in scheduled actions to automate the deletion of records based on provided parameters.

        Example usage in Scheduled Actions:

        1. **Delete Records**:
        To delete records from a model, call the `delete_records` method with the model name, field name, and value.

        Example for deletion:
        
        ```python
        # Example to delete records with move_id=6119 from account.move.line
        model_name = 'account.move.line'
        field_name = 'move_id'
        field_value = 6119
        self.env['reusable.sql.delete'].delete_records(model_name, field_name, field_value)
        ```

        2. **Fetch Record IDs**:
        To fetch record IDs from a model based on a field value, use the `get_record_ids` method.

        Example for fetching IDs:
        
        ```python
        # Example to fetch IDs of records with move_id=6119 from account.move.line
        model_name = 'account.move.line'
        field_name = 'move_id'
        field_value = 6119
        record_ids = self.env['reusable.sql.delete'].get_record_ids(model_name, field_name, field_value)
        ```

        This module should be used manually in scheduled actions to avoid issues with foreign key constraints. It is especially useful for cleaning up orphaned records in the database.
    """,
    "author": "Calyx Servicios S.A.",
    "maintainers": [],
    "website": "https://odoo.calyx-cloud.com.ar/",
    "license": "AGPL-3",
    "category": "Tools",
    "version": "11.0.1.0.0",
    "development_status": "Production/Stable",
    "application": False,
    "installable": True,
    "depends": [
        'base',
        'account',
        ],
    "data": [],
}
