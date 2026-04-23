import re
from typing import List

import common_include as C


@C.dataclass
class PersonName:
    raw: str
    first: str = None
    last: str = None

    def normalize(self):
        text = self.raw.strip()

        # Remove dots
        text = text.replace(".", "")

        # Split LAST, FIRST
        if "," in text:
            last, first = text.split(",", 1)
            self.last = last.strip().title()
            self.first = first.strip().title()
        else:
            parts = text.split()
            if len(parts) >= 2:
                self.first = parts[0].title()
                self.last = parts[-1].title()

        return self


class NameParser:
    @staticmethod
    def split_people(line: str) -> List[PersonName]:
        # Split by &
        parts = re.split(r"&", line)

        return [PersonName(p.strip()).normalize() for p in parts if p.strip()]

def load_names(file_path):
    with open(file_path) as f:
        return {line.strip().title() for line in f}

class IndianNameDetector:
    def __init__(self):
        # self.indian_last_names = {
        #     "Patel", "Shah", "Iyer", "Reddy", "Gupta", "Sharma", "Srivastava"
        # }

        path = r"C:\HOME\FileName.txt"

        self.indian_last_names = load_names("last_names.txt")
        self.indian_first_names = load_names("first_names.txt")

        # self.indian_first_names = {
        #     "Satyen", "Meena", "Geeta", "Rahul", "Amit", "Raj"
        # }

    def is_indian(self, person: PersonName) -> bool:
        if person.last in self.indian_last_names:
            return True

        if person.first in self.indian_first_names:
            return True

        return False


if __name__ == "__main__":
    data = [
        "SRIVASTAVA, Rahiul. & Geeta",
        "PATEL, Satyen & Meena",
        "Shah, Kevin",
        "BARRY, Steve",
        "JORGE,Bob & Geroge-JORGE,SONIA"
    ]

    parser = NameParser()
    detector = IndianNameDetector()

    for line in data:
        persons = parser.split_people(line)

        for p in persons:
            print(f"{p.first} {p.last} -> Indian? {detector.is_indian(p)}")