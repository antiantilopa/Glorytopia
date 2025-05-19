from .tree import TechNode
from ..tile_types import ResourceTypes, BuildingTypes, TileTypes
from ..unit_types import UnitTypes

class Techs:
    base = TechNode(
        name="Base",
        cost=0,
        parent=None,
        tier=0,
        units=[UnitTypes.warrior],
        accessable=[TileTypes.plain, TileTypes.forest]
    )
    organization = TechNode(
        name="Organization",
        cost=4,
        parent=base,
        tier=1,
        harvestables=[ResourceTypes.fruits],
    )
    farming = TechNode(
        name="Farming",
        cost=4,
        parent=organization,
        tier=2,
        buildings=[BuildingTypes.farm],
    )
    construction = TechNode(
        name="Construction",
        cost=4,
        parent=farming,
        tier=3,
        buildings=[BuildingTypes.windmill],
    )
    strategy = TechNode(
        name="Strategy",
        cost=4,
        parent=organization,
        tier=2,
        units=[UnitTypes.defender],
    )
    diplomacy = TechNode(
        name="Diplomacy",
        cost=4,
        parent=strategy,
        tier=3,
        units=[UnitTypes.cloack],
    )
    riding = TechNode(
        name="Riding",
        cost=4,
        parent=base,
        tier=1,
        units=[UnitTypes.rider],
    )
    free_spirit = TechNode(
        name="Free Spirit",
        cost=4,
        parent=riding,
        tier=2,
    )
    chivalry = TechNode(
        name="Chivalry",
        cost=4,
        parent=free_spirit,
        tier=3,
        units=[UnitTypes.knight],
    )
    roads = TechNode( # TODO
        name="Roads",
        cost=4,
        parent=riding,
        tier=3,
    )
    trade = TechNode(
        name="Trade",
        cost=4,
        parent=roads,
        tier=3,
        buildings=[BuildingTypes.market],
    )
    hunting = TechNode(
        name="Hunting",
        cost=4,
        parent=base,
        tier=1,
        harvestables=[ResourceTypes.wild_animals],
    )
    forestry = TechNode(
        name="Forestry",
        cost=4,
        parent=hunting,
        tier=2,
        buildings=[BuildingTypes.hut],
    )
    mathematics = TechNode(
        name="Mathematics",
        cost=4,
        parent=forestry,
        tier=3,
        units=[UnitTypes.catapult],
        buildings=[BuildingTypes.sawmill],
    )
    archery = TechNode(
        name="Archery",
        cost=4,
        parent=hunting,
        tier=2,
        units=[UnitTypes.archer],
        defence=[TileTypes.forest]
    )
    spiritualism = TechNode(
        name="Spiritualism",
        cost=4,
        parent=archery,
        tier=3,
        units=[],
        buildings=[],
        achievements=[],
        harvestables=[],
        defence=[]
    )
    # TODO: water update is needed
    fishing = TechNode(
        name="Fishing",
        cost=4,
        parent=base,
        tier=1,
        buildings=[BuildingTypes.port],
        harvestables=[ResourceTypes.fish],
        accessable=[TileTypes.water]
    )
    aquaculture = TechNode(
        name="Aquaculture",
        cost=4,
        parent=fishing,
        tier=2,
    )
    aquatism = TechNode(
        name="Aquatism",
        cost=4,
        parent=aquaculture,
        tier=3,
        defence=[TileTypes.water, TileTypes.ocean]
    )
    sailing = TechNode(
        name="Sailing",
        cost=4,
        parent=fishing,
        tier=2,
        accessable=[TileTypes.ocean]
    )
    navigation = TechNode(
        name="Navigation",
        cost=4,
        parent=sailing,
        tier=3,
    )
    climbing = TechNode(
        name="Climbing",
        cost=4,
        parent=base,
        tier=1,
        defence=[TileTypes.mountain],
        accessable=[TileTypes.mountain]
    )
    meditation = TechNode(
        name="Meditation",
        cost=4,
        parent=climbing,
        tier=2,
    )
    philosophy = TechNode(
        name="Philosophy",
        cost=4,
        parent=meditation,
        tier=3,
        units=[UnitTypes.mindbender],
    )
    mining = TechNode(
        name="Mining",
        cost=4,
        parent=climbing,
        tier=2,
        buildings=[BuildingTypes.mine],
    )
    smithery = TechNode(
        name="Smithery",
        cost=4,
        parent=mining,
        tier=3,
        units=[UnitTypes.swordsman],
        buildings=[BuildingTypes.forge],
    )

    @staticmethod
    def by_id(id: int) -> TechNode:
        for tech in TechNode.techs:
            if tech.id == id:
                return tech
        raise KeyError(id)