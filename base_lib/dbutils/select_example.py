from sqlalchemy import select
from sqlalchemy.orm import aliased

# Aliases for clarity, though not strictly necessary here
StudentAlias = aliased(Student)
SubjectAlias = aliased(Subject)

# Define the query
stmt = (
    select(StudentAlias.name, StudentAlias.address, SubjectAlias.name)
    .select_from(StudentAlias)  # Set Student as the main table
    .join(SubjectAlias, StudentAlias.stud_id == SubjectAlias.stud_id)  # Join on stud_id
    .where(StudentAlias.active == 1)  # Apply the active filter
)

# Execute the query
results = session.execute(stmt).fetchall()
