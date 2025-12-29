from sqlalchemy import select

def create_select_stmt(table, columns, conditions):
    """
    Create a generic SQLAlchemy select statement based on provided conditions.

    Args:
        table (Base): SQLAlchemy ORM table model to select from.
        columns (list): List of columns to select.
        conditions (list): List of conditions to filter on.

    Returns:
        stmt: A SQLAlchemy select statement object.
    """
    stmt = select(*columns).select_from(table)  # Start with the select statement

    # Adding each condition to the select statement
    for condition in conditions:
        stmt = stmt.where(condition)

    return stmt

# Define columns to select and conditions
columns = [StudentTable.name, StudentTable.address, StudentTable.updated_at]
conditions = [
    StudentTable.lastName == 'Patel',
    StudentTable.address == 'Gujarat'
]

# Create the select statement
stmt = create_select_stmt(StudentTable, columns, conditions)

# Execute the statement
results = session.execute(stmt).fetchall()
