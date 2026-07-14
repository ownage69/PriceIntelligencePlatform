from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exceptions import ProductNotFoundError, register_exception_handlers


def test_business_error_uses_standard_response_contract() -> None:
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/products/{product_id}")
    async def get_product(product_id: int) -> None:
        raise ProductNotFoundError(product_id)

    class PricePayload(BaseModel):
        price: int

    @app.post("/prices")
    async def create_price(payload: PricePayload) -> None:
        del payload

    client = TestClient(app)
    response = client.get("/products/42")

    assert response.status_code == 404
    assert response.json() == {
        "success": False,
        "error": {
            "type": "ProductNotFoundError",
            "message": "Product not found.",
            "details": {"product_id": 42},
        },
    }

    validation_response = client.post("/prices", json={"price": "invalid"})
    assert validation_response.status_code == 422
    assert validation_response.json()["error"]["type"] == "RequestValidationError"
