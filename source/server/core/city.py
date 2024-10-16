from tile import Tile 
from random_names import random_name_with_double as random_name
from ..vmath import Vector2d


class City(Tile):
    city_id: int
    name: str
    income: int
    population: int
    domain: list[Tile]

        
    def __init__(self, city_id, income, population):
        super().__init__()
        self.city_id=city_id
        self.name = random_name()
        self.income = income
        self.population = population
        self.domain
        # TODO domain have to be calculateed

    def grow_population(self, count):
        self.population += count

    def create_unit(self, type):
        
    


    

    
    