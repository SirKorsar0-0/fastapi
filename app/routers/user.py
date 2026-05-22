from fastapi import APIRouter

# Змінна має називатися саме 'router' (маленькими літерами)
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/")
def get_users():
    return {"message": "Тут буде список користувачів"}

@router.post("/")
def create_user():
    return {"message": "Користувача створено"}