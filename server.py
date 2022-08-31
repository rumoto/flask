from __future__ import annotations

import pydantic
import typing
from flask import Flask, jsonify, request
from flask.views import MethodView
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Text, DateTime, func, create_engine


class HttpError(Exception):

    def __init__(self, status_code: int, message: str | dict | list):
        self.status_code = status_code
        self.message = message

class CreateAdvertisement(pydantic.BaseModel):
    title: str
    description: str
    owner: str

class PatchAdvertisement(pydantic.BaseModel):
    title: typing.Optional[str]
    description: typing.Optional[str]
    owner: typing.Optional[str]

def validate(model, raw_data: dict):
    try:
        return model(**raw_data).dict()
    except pydantic.ValidationError as error:
        raise HttpError(400, error.errors())

app = Flask('app')

@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):
    response = jsonify({
        'status': 'error',
        'reason': error.message
    })
    response.status_code = error.status_code
    return response

PG_DSN = 'postgresql://postgres:postgres@127.0.0.1:5431/flask'

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Advertisement(Base):

    __tablename__ = 'advertisements'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    owner = Column(String, nullable=False)

def get_advertisement(session: Session, advertisement_id: int):
    advertisement = session.query(Advertisement).get(advertisement_id)
    if advertisement is None:
        raise HttpError(404, 'advertisement not found')
    return advertisement

Base.metadata.create_all(engine)


class AdvertisementView(MethodView):

    def get(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            return jsonify({'title': advertisement.title, 'created_at': advertisement.created_at.isoformat()})


    def post(self):

        validated = validate(CreateAdvertisement, request.json)

        with Session() as session:
            #advertisement = Advertisement(**json_data)
            advertisement = Advertisement(title=validated['title'], description=validated['description'],
                                          owner=validated['owner'])
            session.add(advertisement)
            session.commit()
            return {'id': advertisement.id}

    def patch(self, advertisement_id: int):

        validated = validate(PatchAdvertisement, request.json)

        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            if validated.get('title'):
                advertisement.title = validated['title']
            if validated.get('description'):
                advertisement.description = validated['description']
            if validated.get('owner'):
                advertisement.owner = validated['owner']
            session.add(advertisement)
            session.commit()
            return {'status': 'success'}

    def delete(self, advertisement_id: int):
        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            session.delete(advertisement)
            session.commit()
            return {'status': 'deleted'}


advertisement_view = AdvertisementView.as_view('advertisements')
app.add_url_rule('/advertisements/', view_func=advertisement_view, methods=['POST'])
app.add_url_rule('/advertisements/<int:advertisement_id>', view_func=advertisement_view, methods=['GET', 'PATCH', 'DELETE'])


app.run()