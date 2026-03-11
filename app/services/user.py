from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def _hash_password(self, password: str) -> str:
        """Хэширует пароль"""
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль"""
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user_data: UserCreate) -> User:
        """Создает нового пользователя"""
        # Проверяем, не занят ли email
        existing = self.repo.get_by_email(user_data.email)
        if existing:
            raise ValueError("Email already registered")

        # Хэшируем пароль
        password_hash = self._hash_password(user_data.password)

        # Создаем пользователя
        user = self.repo.create(
            email=user_data.email,
            password_hash=password_hash,
            is_active=user_data.is_active,
            is_admin=user_data.is_admin,
        )
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """Получает пользователя по ID"""
        return self.repo.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Получает пользователя по email"""
        return self.repo.get_by_email(email)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Аутентифицирует пользователя"""
        user = self.repo.get_by_email(email)
        if not user:
            return None
        if not self._verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Обновляет данные пользователя"""
        update_data = user_data.model_dump(exclude_unset=True)

        # Если обновляют пароль - хэшируем
        if "password" in update_data:
            update_data["password_hash"] = self._hash_password(
                update_data.pop("password")
            )

        return self.repo.update(user_id, **update_data)

    def deactivate_user(self, user_id: int) -> User | None:
        """Деактивирует пользователя"""
        return self.repo.update(user_id, is_active=False)
