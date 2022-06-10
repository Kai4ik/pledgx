from marshmallow import Schema, fields
from marshmallow.validate import Length


class CreateNoteInputSchema(Schema):
    firstName = fields.Str(required=True, validate=Length(max=30))
    lastName = fields.Str(required=True, validate=Length(max=30))
    phoneNumber = fields.Str(required=True, validate=Length(max=20))
    jobTitle = fields.Str(required=True, validate=Length(max=50))
    country = fields.Str(required=True, validate=Length(max=30))


createUserSchema = CreateNoteInputSchema()
