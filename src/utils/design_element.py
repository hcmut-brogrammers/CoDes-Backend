import typing as t
from dataclasses import dataclass

import pydantic as p

from ..common.models import (
    BaseCircleModel,
    BaseElementModel,
    BaseRectangleModel,
    CircleModel,
    ElementModel,
    RectangleModel,
    ShapeModel,
    ShapeType,
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


def create_element(base_element: BaseElementModel) -> ElementModel:
    if BaseElementTypeChecker.is_base_circle_element(base_element):
        return CircleModel(**base_element.model_dump())

    if BaseElementTypeChecker.is_base_rectangle_element(base_element):
        return RectangleModel(**base_element.model_dump())

    return ShapeModel(**base_element.model_dump())
