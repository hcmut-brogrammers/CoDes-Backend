from src.common.models.design_entities.node import NodeModel
from src.common.models.design_entities.shape import ShapeModel

ShapeElementModel = ShapeModel | NodeModel
