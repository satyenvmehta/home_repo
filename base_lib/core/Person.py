class Person:
    def __init__(self, first_name, last_name, age):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.age} years old"


# Function to convert tab-separated data to Person objects
def convert_data_to_objects(data, cls):
    objects = []
    for line in data:
        parts = line.strip().split('\t')
        if len(parts) == 3:
            first_name, last_name, age = parts
            person = cls(first_name, last_name, int(age))
            objects.append(person)
    return objects


# Example tab-separated data
data_str = """John\tDoe\t30
Alice\tSmith\t25
Bob\tJohnson\t40"""

# Convert the data string to a list of Person objects
data_lines = data_str.split('\n')
people = convert_data_to_objects(data_lines, Person)

# Print the Person objects
for person in people:
    print(person)
