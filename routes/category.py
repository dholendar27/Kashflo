from fastapi import APIRouter, Depends, HTTPException, status, responses
from sqlalchemy.orm import Session

from schema import CategoryResponse, CategoryCreateSchema, CategorySchema, CategoryUpdateSchema
from utils import get_db, get_current_user
from models import Category, User

categories_router = APIRouter(prefix="/categories", tags=["Category"])


@categories_router.post("", response_model=CategoryResponse)
def create_category(category: CategoryCreateSchema, user_details=Depends(get_current_user),
                    session: Session = Depends(get_db)):
    # Checking if category already exists
    existing_category = session.query(Category).filter(Category.name == category.name,
                                                       Category.user_id == user_details.id).first()
    if existing_category:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    # Creating a new category
    new_category = Category(name=category.name, description=category.description, user_id=user_details.id)
    session.add(new_category)
    session.commit()

    # Returning the response
    return responses.JSONResponse({
        "message": "Category created successfully",
        "data": {
            "id": str(new_category.id),  # You can include other fields as needed
            "name": new_category.name,
            "description": new_category.description,
            "is_active": new_category.is_active,
            "created_at": new_category.created_at.isoformat(),
            "updated_at": new_category.updated_at.isoformat()
        }
    }, status_code=status.HTTP_201_CREATED)


@categories_router.get("", response_model=CategoryResponse)
def list_categories(user_details=Depends(get_current_user), session: Session = Depends(get_db)):
    categories = session.query(Category).filter(Category.user_id == user_details.id).all()
    if not categories:
        return CategoryResponse(
            message="No categories found",
            categories=[]
        )
    return CategoryResponse(
        message="Categories retrieved successfully",
        categories=[CategorySchema.model_validate(category) for category in categories]
    )


@categories_router.delete("/{category_id}/")
def delete_categories(category_id: str, user_details: User = Depends(get_current_user),
                      session: Session = Depends(get_db)):
    exisiting_category = session.query(Category).filter(
        Category.user_id == user_details.id and Category.id == category_id).first()
    if not exisiting_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    session.delete(exisiting_category)
    session.commit()

    return responses.Response(status_code=status.HTTP_204_NO_CONTENT)


@categories_router.put("/{category_id}/")
def delete_categories(category_id: str, category: CategoryUpdateSchema, user_details: User = Depends(get_current_user),
                      session: Session = Depends(get_db)):
    existing_category = session.query(Category).filter(
        Category.user_id == user_details.id, Category.id == category_id).first()

    if not existing_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if category.name is not None:
        existing_category.name = category.name
    if category.description is not None:
        existing_category.description = category.description
    if category.is_active is not None:
        existing_category.is_active = category.is_active

    session.commit()
    return CategoryResponse(
        message="Category updated successfully",
        categories=[CategorySchema.model_validate(existing_category)]
    )
