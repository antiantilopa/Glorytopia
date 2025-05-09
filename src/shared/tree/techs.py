from .tree import TechNode
from ..tile_types import ResourceTypes, BuildingTypes
from ..unit_types import UnitTypes

class Techs:
    base = TechNode(
        name="Base",
        cost=0,
        parent=None,
        tier=0,
        units=[UnitTypes.warrior],
        buildings=[],
        achievements=[],
        harvestables=[],
        defence=[]
    )
    organization = TechNode(
        name="Organization",
        cost=4,
        parent=base,
        tier=1,
        units=[],
        buildings=[],
        achievements=[],
        harvestables=[ResourceTypes.fruits],
        defence=[]
    )
    farming = TechNode(
        name="Farming",
        cost=4,
        parent=organization,
        tier=2,
        units=[],
        buildings=[BuildingTypes.farm],
        achievements=[],
        harvestables=[],
        defence=[]
    )

    objs = [
        base,
        organization,
        farming
    ]

    @staticmethod
    def by_id(id: int) -> TechNode:
        for tech in Techs.objs:
            if tech.id == id:
                return tech
        raise KeyError(id)