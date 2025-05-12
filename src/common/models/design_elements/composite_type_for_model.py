from .arrow import ArrowModel, BaseArrowModel
from .circle import BaseCircleModel, CircleModel
from .ellipse import BaseEllipseModel, EllipseModel
from .image import BaseImageModel, ImageModel
from .line import BaseLineModel, LineModel
from .node import NodeModel
from .rectangle import BaseRectangleModel, RectangleModel
from .regular_polygon import BaseRegularPolygonModel, RegularPolygonModel
from .ring import BaseRingModel, RingModel
from .shape import BaseShapeModel, ShapeModel
from .star import BaseStarModel, StarModel
from .text import BaseTextModel, TextModel

BaseElementModel = (
    BaseRegularPolygonModel
    | BaseLineModel
    | BaseImageModel
    | BaseStarModel
    | BaseRingModel
    | BaseEllipseModel
    | BaseArrowModel
    | BaseTextModel
    | BaseCircleModel
    | BaseRectangleModel
    | BaseShapeModel
)

ElementModel = (
    RegularPolygonModel
    | LineModel
    | ImageModel
    | StarModel
    | RingModel
    | EllipseModel
    | ArrowModel
    | TextModel
    | CircleModel
    | RectangleModel
    | ShapeModel
)

ShapeElementModel = BaseRegularPolygonModel | CircleModel | ShapeModel | NodeModel
