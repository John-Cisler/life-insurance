from faker import Faker, random
import csv, datetime
fake = Faker()


with open("customers.csv", "w") as f:
    w = csv.writer(f)
    w.writerow(["first_name","last_name","dob","smoker"])
    for _ in range(100):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=70)
        smoker = random.choice([True, False, False])  # ~33 % smokers
        w.writerow([fake.first_name(), fake.last_name(),
                    dob.isoformat(), smoker])