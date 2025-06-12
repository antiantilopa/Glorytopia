from .tree import TechNode
from ..tile_types import ResourceTypes, BuildingTypes, TileTypes
from ..unit_types import UnitTypes

class Techs:
    base = TechNode(
        name="base",
        cost=0,
        parent=None,
        tier=0,
        units=[UnitTypes.warrior],
        accessable=[TileTypes.plain, TileTypes.forest]
    )
    organization = TechNode(
        name="organization",
        cost=4,
        parent=base,
        tier=1,
        harvestables=[ResourceTypes.fruits],
    )
    farming = TechNode(
        name="farming",
        cost=4,
        parent=organization,
        tier=2,
        buildings=[BuildingTypes.farm],
    )
    construction = TechNode(
        name="construction",
        cost=4,
        parent=farming,
        tier=3,
        buildings=[BuildingTypes.windmill],
    )
    strategy = TechNode(
        name="strategy",
        cost=4,
        parent=organization,
        tier=2,
        units=[UnitTypes.defender],
    )
    diplomacy = TechNode(
        name="diplomacy",
        cost=4,
        parent=strategy,
        tier=3,
        units=[UnitTypes.cloack],
    )
    riding = TechNode(
        name="riding",
        cost=4,
        parent=base,
        tier=1,
        units=[UnitTypes.rider],
    )
    free_spirit = TechNode(
        name="free_Spirit",
        cost=4,
        parent=riding,
        tier=2,
    )
    chivalry = TechNode(
        name="chivalry",
        cost=4,
        parent=free_spirit,
        tier=3,
        units=[UnitTypes.knight],
    )
    roads = TechNode( # TODO
        name="roads",
        cost=4,
        parent=riding,
        tier=3,
    )
    trade = TechNode(
        name="trade",
        cost=4,
        parent=roads,
        tier=3,
        buildings=[BuildingTypes.market],
    )
    hunting = TechNode(
        name="hunting",
        cost=4,
        parent=base,
        tier=1,
        harvestables=[ResourceTypes.wild_animals],
    )
    forestry = TechNode(
        name="forestry",
        cost=4,
        parent=hunting,
        tier=2,
        buildings=[BuildingTypes.hut],
    )
    mathematics = TechNode(
        name="mathematics",
        cost=4,
        parent=forestry,
        tier=3,
        units=[UnitTypes.catapult],
        buildings=[BuildingTypes.sawmill],
    )
    archery = TechNode(
        name="archery",
        cost=4,
        parent=hunting,
        tier=2,
        units=[UnitTypes.archer],
        defence=[TileTypes.forest]
    )
    spiritualism = TechNode(
        name="spiritualism",
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
        name="fishing",
        cost=4,
        parent=base,
        tier=1,
        buildings=[BuildingTypes.port],
        harvestables=[ResourceTypes.fish],
        accessable=[TileTypes.water]
    )
    aquaculture = TechNode(
        name="aquaculture",
        cost=4,
        parent=fishing,
        tier=2,
    )
    aquatism = TechNode(
        name="aquatism",
        cost=4,
        parent=aquaculture,
        tier=3,
        defence=[TileTypes.water, TileTypes.ocean]
    )
    sailing = TechNode(
        name="sailing",
        cost=4,
        parent=fishing,
        tier=2,
        accessable=[TileTypes.ocean]
    )
    navigation = TechNode(
        name="navigation",
        cost=4,
        parent=sailing,
        tier=3,
    )
    climbing = TechNode(
        name="climbing",
        cost=4,
        parent=base,
        tier=1,
        defence=[TileTypes.mountain],
        accessable=[TileTypes.mountain]
    )
    meditation = TechNode(
        name="meditation",
        cost=4,
        parent=climbing,
        tier=2,
    )
    philosophy = TechNode(
        name="philosophy",
        cost=4,
        parent=meditation,
        tier=3,
        units=[UnitTypes.mindbender],
    )
    mining = TechNode(
        name="mining",
        cost=4,
        parent=climbing,
        tier=2,
        buildings=[BuildingTypes.mine],
    )
    smithery = TechNode(
        name="smithery",
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