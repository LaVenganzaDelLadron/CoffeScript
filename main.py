from fastapi import FastAPI
from controllers import authentication, coffee_controller, categories_controller, order_controller, cart_controller, store_controller, money_controller

app = FastAPI()


app.include_router(authentication.router)
app.include_router(cart_controller.router)
app.include_router(categories_controller.router)
app.include_router(coffee_controller.router)
app.include_router(order_controller.router)
app.include_router(store_controller.router)
app.include_router(money_controller.router)