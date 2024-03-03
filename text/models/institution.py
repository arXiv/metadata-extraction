class Institution:
    def __init__(self, name, city, country):
        self.__name = name
        self.__city = city
        self.__country = country

    # Getter method for name
    def get_name(self):
        return self.__name

    # Getter method for city
    def get_city(self):
        return self.__city

    # Getter method for country
    def get_country(self):
        return self.__country
