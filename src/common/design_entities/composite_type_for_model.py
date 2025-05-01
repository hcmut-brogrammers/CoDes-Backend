from src.common.models.design_entities.circle import CircleModel
from src.common.models.design_entities.node import NodeModel
from src.common.models.design_entities.regular_polygon import RegularPolygonModel
from src.common.models.design_entities.shape import ShapeModel

ShapeElementModel = RegularPolygonModel | CircleModel | ShapeModel | NodeModel
