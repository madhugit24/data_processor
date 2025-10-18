from sqlalchemy import (
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship

Base = declarative_base()


class Venue(Base):
    __tablename__ = "venues"

    VenueID = Column(Integer, primary_key=True)
    VenueName = Column(String(255), nullable=False)

    stores = relationship("Store", back_populates="venue")


class Store(Base):
    __tablename__ = "stores"

    StoreID = Column(Integer, primary_key=True)
    StoreName = Column(String(255), nullable=False)
    VenueID = Column(Integer, ForeignKey("venues.VenueID"), nullable=False)

    venue = relationship("Venue", back_populates="stores")
    transactions = relationship("Transaction", back_populates="store")


class Transaction(Base):
    __tablename__ = "transactions"

    TransactionID = Column(Integer, primary_key=True)
    TransactionType = Column(String(50), nullable=False)
    DateTimeUTC = Column(DateTime, nullable=False)
    OperatorNumber = Column(String(50))
    OperatorName = Column(String(255))
    TillID = Column(Integer)
    TillName = Column(String(255))
    ServiceCharge = Column(Float, default=0.0)
    NettTotal = Column(Float)
    NettSales = Column(Float)
    GrossSales = Column(Float)
    OrderDiscount = Column(Float, default=0.0)
    TotalDiscount = Column(Float, default=0.0)
    Taxable = Column(Float)
    NonTaxable = Column(Float)
    TaxAmount = Column(Float)

    # JSON fields
    Payments = Column(JSON, nullable=True)
    Account = Column(JSON, nullable=True)

    # Foreign key to Store
    StoreID = Column(Integer, ForeignKey("stores.StoreID"), nullable=False)

    # Relationship
    store = relationship("Store", back_populates="transactions")
    items = relationship(
        "Item", back_populates="transaction", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"

    ProductID = Column(Integer, primary_key=True)
    ProductName = Column(String(255), nullable=False)
    CategoryID = Column(Integer)
    Category = Column(String(255))
    CategoryGroupID = Column(Integer)
    CategoryGroup = Column(String(255))
    Active = Column(Boolean, default=True)
    Price = Column(Float)
    ProductCost = Column(Float)
    Size = Column(String(100))
    SizeVolume = Column(Float)
    SizeUnit = Column(String(50))
    Barcode = Column(String(100))
    Base = Column(String(50))
    BaseVolume = Column(Float)
    BaseUnit = Column(String(50))

    # Relationship
    items = relationship("Item", back_populates="product")


class Item(Base):
    __tablename__ = "items"

    LineID = Column(Integer, primary_key=True)
    TransactionID = Column(
        Integer,
        ForeignKey("transactions.TransactionID"),
        primary_key=True,  # Add primary_key=True
    )
    ProductID = Column(Integer, ForeignKey("products.ProductID"), nullable=False)
    Quantity = Column(Float)
    NettPrice = Column(Float)
    GrossPrice = Column(Float)
    ItemDiscount = Column(Float, default=0.0)
    IsCondiment = Column(Boolean, default=False)
    NettTotal = Column(Float)

    # Relationships
    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="items")
    promos = relationship("Promo", back_populates="item", cascade="all, delete-orphan")


class Promo(Base):
    __tablename__ = "promos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    LineID = Column(Integer, nullable=False)
    TransactionID = Column(Integer, nullable=False)
    PromoID = Column(Integer, nullable=True)
    PromoName = Column(String(255), nullable=True)
    TotaliserName = Column(String(255))
    Amount = Column(Float)
    TotaliserID = Column(Integer)

    # Composite foreign key to Item
    __table_args__ = (
        ForeignKeyConstraint(
            ["LineID", "TransactionID"], ["items.LineID", "items.TransactionID"]
        ),
    )

    # Relationship - only with Item
    item = relationship("Item", back_populates="promos")
