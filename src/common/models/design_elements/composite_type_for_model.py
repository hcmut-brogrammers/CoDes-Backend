from .circle import BaseCircleModel, CircleModel
from .node import NodeModel
from .rectangle import BaseRectangleModel, RectangleModel
from .regular_polygon import RegularPolygonModel
from .shape import BaseShapeModel, ShapeModel

BaseElementModel = BaseCircleModel | BaseRectangleModel | BaseShapeModel

ElementModel = CircleModel | RectangleModel | ShapeModel

ShapeElementModel = RegularPolygonModel | CircleModel | ShapeModel | NodeModel
