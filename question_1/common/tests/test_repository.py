# test_crudbase.py
import pytest

from apps.example.models import SomeModel
from apps.example.schemas import SomeModelCreate, SomeModelUpdate
from common.repository.base import CRUDBase


@pytest.mark.asyncio
async def test_create_and_get_some_model(db_session):
    crud = CRUDBase(SomeModel, db_session)

    # Create a model instance
    payload = SomeModelCreate(name="Test Model")
    created = await crud.create(obj_in=payload)

    assert created.id is not None
    assert created.name == "Test Model"

    # Retrieve the model instance
    found = await crud.get(id=created.id)
    assert found is not None
    assert found.id == created.id
    assert found.name == "Test Model"


@pytest.mark.asyncio
async def test_update_some_model(db_session):
    crud = CRUDBase(SomeModel, db_session)

    # Create
    payload = SomeModelCreate(name="Initial")
    model = await crud.create(obj_in=payload)

    # Update
    updated_data = SomeModelUpdate(id=model.id, name="Updated Name")
    updated = await crud.update(obj_current=model, obj_new=updated_data)

    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_remove_some_model(db_session):
    crud = CRUDBase(SomeModel, db_session)

    # Create
    payload = SomeModelCreate(name="To Delete")
    model = await crud.create(obj_in=payload)

    # Remove
    deleted = await crud.remove(id=model.id)

    assert deleted.id == model.id

    result = await crud.get(id=model.id)
    assert result is None


@pytest.mark.asyncio
async def test_bulk_create_some_model(db_session):
    crud = CRUDBase(SomeModel, db_session)

    # Create a model instance
    payload = [
        SomeModelCreate(name="Test Model 1"),
        SomeModelCreate(name="Test Model 2"),
        SomeModelCreate(name="Test Model 3"),
    ]
    created_objs = await crud.bulk_create(objs_in=payload)

    for i, obj in enumerate(created_objs):
        assert obj.id is not None
        assert obj.name == f"Test Model {i+1}"

        # Retrieve the model instance
        found = await crud.get(id=obj.id)
        assert found is not None
        assert found.id == obj.id
        assert found.name == f"Test Model {i+1}"


@pytest.mark.asyncio
async def test_get_some_models(db_session):
    crud = CRUDBase(SomeModel, db_session)

    # Create a model instance
    payload = [
        SomeModelCreate(name="Test Model 1"),
        SomeModelCreate(name="Test Model 2"),
        SomeModelCreate(name="Test Model 3"),
    ]
    await crud.bulk_create(objs_in=payload)

    # test get multi
    objs = await crud.get_multi()

    assert len(objs) == 3

    for i, obj in enumerate(objs, 1):
        assert obj.name == f"Test Model {i}"
