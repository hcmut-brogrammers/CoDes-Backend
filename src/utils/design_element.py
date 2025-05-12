import typing as t
from dataclasses import dataclass

import pydantic as p

from ..common.models import (
    ArrowModel,
    BaseArrowModel,
    BaseCircleModel,
    BaseElementModel,
    BaseEllipseModel,
    BaseImageModel,
    BaseLineModel,
    BaseRectangleModel,
    BaseRegularPolygonModel,
    BaseRingModel,
    BaseStarModel,
    BaseTextModel,
    CircleModel,
    ElementModel,
    EllipseModel,
    ImageModel,
    LineModel,
    RectangleModel,
    RegularPolygonModel,
    RingModel,
    ShapeModel,
    ShapeType,
    StarModel,
    TextModel,
)


@dataclass(frozen=True)
class BaseElementTypeChecker:
    @staticmethod
    def is_base_rectangle_element(element: BaseElementModel) -> t.TypeGuard[BaseRectangleModel]:
        """
        Check if the element is a base rectangle element.
        """
        return isinstance(element, BaseRectangleModel) and element.shapeType == ShapeType.Rectangle

    @staticmethod
    def is_base_circle_element(element: BaseElementModel) -> t.TypeGuard[BaseCircleModel]:
        """
        Check if the element is a base circle element.
        """
        return isinstance(element, BaseCircleModel) and element.shapeType == ShapeType.Circle

    @staticmethod
    def is_base_image_element(element: BaseElementModel) -> t.TypeGuard[BaseImageModel]:
        """
        Check if the element is a base image element.
        """
        return isinstance(element, BaseImageModel) and element.shapeType == ShapeType.Image

    @staticmethod
    def is_base_ellipse_element(element: BaseElementModel) -> t.TypeGuard[BaseEllipseModel]:
        """
        Check if the element is a base ellipse element.
        """
        return isinstance(element, BaseEllipseModel) and element.shapeType == ShapeType.Ellipse

    @staticmethod
    def is_base_star_element(element: BaseElementModel) -> t.TypeGuard[BaseStarModel]:
        """
        Check if the element is a base star element.
        """
        return isinstance(element, BaseStarModel) and element.shapeType == ShapeType.Star

    @staticmethod
    def is_base_arrow_element(element: BaseElementModel) -> t.TypeGuard[BaseArrowModel]:
        """
        Check if the element is a base arrow element.
        """
        return isinstance(element, BaseArrowModel) and element.shapeType == ShapeType.Arrow

    @staticmethod
    def is_base_ring_element(element: BaseElementModel) -> t.TypeGuard[BaseRingModel]:
        """
        Check if the element is a base ring element.
        """
        return isinstance(element, BaseRingModel) and element.shapeType == ShapeType.Ring

    @staticmethod
    def is_base_line_element(element: BaseElementModel) -> t.TypeGuard[BaseLineModel]:
        """
        Check if the element is a base line element.
        """
        return isinstance(element, BaseLineModel) and element.shapeType == ShapeType.Line

    @staticmethod
    def is_base_text_element(element: BaseElementModel) -> t.TypeGuard[BaseTextModel]:
        """
        Check if the element is a base text element.
        """
        return isinstance(element, BaseTextModel) and element.shapeType == ShapeType.Text

    @staticmethod
    def is_base_regular_polygon_element(element: BaseElementModel) -> t.TypeGuard[BaseRegularPolygonModel]:
        """
        Check if the element is a base regular polygon element.
        """
        return isinstance(element, BaseRegularPolygonModel) and element.shapeType == ShapeType.RegularPolygon


def create_element(base_element: BaseElementModel) -> ElementModel | None:
    if BaseElementTypeChecker.is_base_circle_element(base_element):
        return CircleModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_rectangle_element(base_element):
        return RectangleModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_image_element(base_element):
        return ImageModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_ellipse_element(base_element):
        return EllipseModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_star_element(base_element):
        return StarModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_arrow_element(base_element):
        return ArrowModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_ring_element(base_element):
        return RingModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_line_element(base_element):
        return LineModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_text_element(base_element):
        return TextModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_regular_polygon_element(base_element):
        return RegularPolygonModel(**base_element.model_dump())

    return None
