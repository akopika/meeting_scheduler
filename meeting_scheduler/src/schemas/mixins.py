from marshmallow import ValidationError
from meeting_scheduler.src import ServiceFactory, container

db = ServiceFactory(container).get_db()


class DeserializationMixin:
    def deserialize(self, json: dict) -> db.Model:
        model = None
        try:
            model = self.load(json, session=db.session)
        except ValidationError as err:
            print({"message": str(err)})
        return model
