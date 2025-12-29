from sqlalchemy import update, and_

def create_update_stmt(table, update_values, conditions):
    """
    Create a generic SQLAlchemy update statement based on provided conditions.

    Args:
        table (Base): SQLAlchemy ORM table model to update.
        update_values (dict): Dictionary of columns to update with their new values.
        conditions (list): List of conditions to filter on.

    Returns:
        stmt: A SQLAlchemy update statement object.
    """
    stmt = update(table).values(**update_values)  # Start with the update statement

    # Adding each condition to the update statement
    for condition in conditions:
        stmt = stmt.where(condition)

    return stmt


def update_most_recent_row(session, table, conditions, update_values, timestamp_field):
    """
    Update only the most recently updated row based on maximum timestamp and conditions.

    Args:
        session (Session): SQLAlchemy session object.
        table (Base): SQLAlchemy ORM table model to update.
        conditions (list): List of conditions to filter on.
        update_values (dict): Dictionary of columns to update with their new values.
        timestamp_field (Column): The timestamp or date field to order by for selecting the latest row.

    Returns:
        ResultProxy: Result of the update execution.
    """
    # Step 1: Retrieve the maximum timestamp for rows matching the conditions
    max_timestamp = session.execute(
        select(timestamp_field)
        .where(conditions[0])  # Start with the first condition
        .where(conditions[1])  # Chain the second condition
        .order_by(timestamp_field.desc())
        .limit(1)
    ).scalar()

    # Step 2: Perform the update on the row with this max timestamp
    stmt = update(table)

    # Adding each condition to the update statement
    for condition in conditions:
        stmt = stmt.where(condition)

    stmt = stmt.where(timestamp_field == max_timestamp).values(**update_values)

    result = session.execute(stmt)
    session.commit()
    return result

#------
# Example usage to update the most recent row where lastName is 'Patel' and address is 'Gujarat'
update_most_recent_row(
    session=session,
    table=StudentTable,
    conditions=[
        StudentTable.lastName == 'Patel',
        StudentTable.address == 'Gujarat'
    ],
    update_values={'origin': 'India'},
    timestamp_field=StudentTable.updated_at
)
#-----
from sqlalchemy import update, and_

def create_update_stmt(table, update_values, conditions):
    """
    Create a generic SQLAlchemy update statement based on provided conditions.

    Args:
        table (Base): SQLAlchemy ORM table model to update.
        update_values (dict): Dictionary of columns to update with their new values.
        conditions (list): List of conditions to filter on.

    Returns:
        stmt: A SQLAlchemy update statement object.
    """
    stmt = update(table).values(**update_values)  # Start with the update statement

    # Adding each condition to the update statement
    for condition in conditions:
        stmt = stmt.where(condition)

    return stmt



# Define your update values and conditions
update_values = {'origin': 'India'}
conditions = [
    StudentTable.lastName == 'Patel',
    StudentTable.address == 'Gujarat'
]

# Create the update statement
stmt = create_update_stmt(StudentTable, update_values, conditions)

# Execute the statement
result = session.execute(stmt)
session.commit()

from sqlalchemy import update, select, and_


def update_most_recent_row(session, table, conditions, update_values, timestamp_field):
    """
    Update only the most recently updated row based on the maximum timestamp and conditions.

    Args:
        session (Session): SQLAlchemy session object.
        table (Base): SQLAlchemy ORM table model to update.
        conditions (list): List of conditions to filter on.
        update_values (dict): Dictionary of columns to update with their new values.
        timestamp_field (Column): The timestamp or date field to order by for selecting the latest row.

    Returns:
        ResultProxy: Result of the update execution.
    """
    # Step 1: Retrieve the maximum timestamp for rows matching the conditions
    max_timestamp = session.execute(
        select(timestamp_field)
        .where(and_(*conditions))
        .order_by(timestamp_field.desc())
        .limit(1)
    ).scalar()

    # Step 2: Perform the update on the row with this max timestamp
    stmt = (
        update(table)
        .where(and_(*conditions, timestamp_field == max_timestamp))  # Add timestamp to the conditions
        .values(**update_values)
    )

    result = session.execute(stmt)
    session.commit()
    return result
# Example usage to update the most recent row where lastName is 'Patel' and address is 'Gujarat'
update_most_recent_row(
    session=session,
    table=StudentTable,
    conditions=[StudentTable.lastName == 'Patel', StudentTable.address == 'Gujarat'],
    update_values={'origin': 'India'},
    timestamp_field=StudentTable.updated_at
)
# Get the primary key columns for the table
primary_key_column = table.__table__.primary_key.columns.keys()[0]
