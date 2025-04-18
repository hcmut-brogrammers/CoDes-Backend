import typing as t
from uuid import UUID

import pydantic as p
from fastapi import Depends

from ...common.models import ProductModel
from ...constants.mongo import CollectionName
from ...dependencies import LoggerDep, MongoDbDep
from ...exceptions import NotFoundError
from ...interfaces.base_component import IBaseComponent
from ...utils.logger import execute_service_method

IGetProductById = IBaseComponent["GetProductById.Request", "GetProductById.Response"]


class GetProductById(IGetProductById):
    def __init__(self, db: MongoDbDep, logger: LoggerDep) -> None:
        self._collection = db.get_collection(CollectionName.PRODUCTS)
        self._logger = logger

    class Request(p.BaseModel):
        product_id: UUID

    class Response(p.BaseModel):
        product: ProductModel

    async def aexecute(self, request: "Request") -> "Response":
        self._logger.info(execute_service_method(self))
        product_data = await ProductModel.find_one({"_id": request.product_id}, fetch_links=True)

        if not product_data:
            self._logger.error(f"Product with id {request.product_id} not found")
            raise NotFoundError(f"Product with id {request.product_id} not found")

        await product_data.fetch_link(ProductModel.organization)
        print(type(product_data.organization))
        return self.Response(product=product_data)


GetProductByIdDep = t.Annotated[GetProductById, Depends()]
