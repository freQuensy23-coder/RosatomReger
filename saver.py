import csv


class Saver:
    def __init__(self, file_name="data.csv"):
        self.file_name = file_name

    def add_person(self, login, password, name, surname, f_name, date_of_birth):
        self.file = open(self.file_name, "a")
        self.csv_writer = csv.writer(self.file, delimiter=';')
        self.csv_writer.writerow([login, password, name, surname, f_name, date_of_birth])
        self.file.close()