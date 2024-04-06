from sqlalchemy import Column, Integer, String, ForeignKey, Table

from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime



Base = declarative_base()

date_medicine = Table(

    "date_medicine",

    Base.metadata,

    Column("medicine_id", Integer, ForeignKey("medicine.medicine_id")),

    Column("date", Integer, ForeignKey("date.date_id")),

)


class Medicine(Base):

    __tablename__ = "medicine"

    medicine_id = Column(Integer, primary_key=True)

    generic_name = Column(String)

    brand_name = Column(String)

    modality = Column(String)

    raw = Column(String)

    dates = relationship(

        "Date", secondary=date_medicine, back_populates="medicines"

    )
    


class Dose(Base):

    __tablename__ = "medicine"

    dose_id = Column(Integer, primary_key=True)

    medicine_id = Column(Integer, ForeignKey("medicine.medicine_id"))

    quantity = Column(Integer)

    unit = Column(String)

    date = Column(String)
    
    time = Column(String)


class Date(Base):
    __tablename__ = "dates"

    date_id = Column(Integer, primary_key=True)

    date = Column(datetime)

    frequency = Column(String)

    start_date = Column(String)

    end_date = Column(String)

    medicines = relationship(

        "Medicine", secondary=date_medicine, back_populates="dates"

    )

#These are intended to be assumed based off of medications that are given in a consistent manner
class Treatment(Base):
    __tablename__ = "treatment"

    treatment_id = Column(Integer, primary_key=True)

    medicine_id = Column(Integer, ForeignKey("medicine.medicine_id"))

    frequency = Column(String)

    start_date = Column(String)

    end_date = Column(String)


# def add_new_book(data,medicine_obj):
#     """Adds a new book to the system"""
#     # Does the book exist?
#     first_name, _, last_name = author_name.partition(" ")
#     if any(
#         (data.first_name == first_name)
#         & (data.last_name == last_name)
#         & (data.title == book_title)
#         & (data.publisher == publisher_name)
#     ):
#         return data
#     # Add the new book
#     return data.append(
#         {
#             "first_name": first_name,
#             "last_name": last_name,
#             "title": book_title,
#             "publisher": publisher_name,
#         },
#         ignore_index=True,
#     )
