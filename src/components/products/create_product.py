import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends
from pymongo.cursor import Cursor

from src.common.models.product import ProductModel

from ...common.models import OrganizationModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep, UserContextDep
from ...exceptions import BadRequestError, InternalServerError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

ICreateProduct = IBaseComponent["CreateProduct.Request", "CreateProduct.Response"]


class CreateProduct(ICreateProduct):
    def __init__(self, db: MongoDbDep, logger: LoggerDep, user_context: UserContextDep) -> None:
        self._org_collection = db.get_collection(CollectionName.ORGANIZATIONS)
        self._logger = logger
        self._user_context = user_context

    class Request(p.BaseModel):
        name: str
        organization_id: UUID

    class Response(p.BaseModel):
        created_product: ProductModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))

        organization_data = self._org_collection.find_one({"_id": request.organization_id})
        if organization_data is None:
            error_message = f"No fields to update for organization id {request.organization_id}."
            self._logger.info(error_message)
            raise BadRequestError(error_message)

        organization = OrganizationModel(**organization_data)
        product = ProductModel(name=request.name, organization=organization)
        await product.create()

        return self.Response(created_product=product)


CreateProductDep = t.Annotated[CreateProduct, Depends()]
