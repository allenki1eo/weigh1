"""ORM models for WeighMaster Pro."""
from __future__ import annotations

import json
from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(64), unique=True, nullable=False)
    full_name: str = Column(String(128), nullable=False)
    password_hash: str = Column(String(256), nullable=False)
    role: str = Column(String(16), nullable=False, default="operator")  # "admin"|"operator"
    is_active: bool = Column(Boolean, nullable=False, default=True)
    created_at: datetime = Column(DateTime, server_default=func.now())
    last_login: Optional[datetime] = Column(DateTime, nullable=True)
    created_by: Optional[int] = Column(Integer, ForeignKey("users.id"), nullable=True)

    tickets = relationship("WeighTicket", back_populates="operator", foreign_keys="WeighTicket.operator_id")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"


class Company(Base):
    __tablename__ = "company"

    id: int = Column(Integer, primary_key=True, default=1)
    name: str = Column(String(128), nullable=False, default="My Company")
    address: str = Column(Text, nullable=False, default="")
    phone: str = Column(String(32), nullable=False, default="")
    email: Optional[str] = Column(String(128), nullable=True)
    logo_path: Optional[str] = Column(String(512), nullable=True)
    weighbridge_capacity_kg: float = Column(Float, nullable=False, default=80000.0)
    wma_cert_number: str = Column(String(64), nullable=False, default="")
    wma_valid_until: Optional[date] = Column(Date, nullable=True)
    com_port: str = Column(String(32), nullable=False, default="COM3")
    baud_rate: int = Column(Integer, nullable=False, default=9600)
    data_bits: int = Column(Integer, nullable=False, default=8)
    parity: str = Column(String(4), nullable=False, default="E")
    stop_bits: int = Column(Integer, nullable=False, default=1)
    scale_protocol: str = Column(String(16), nullable=False, default="xk3190")
    currency: str = Column(String(8), nullable=False, default="TZS")
    language: str = Column(String(4), nullable=False, default="en")
    ticket_prefix: str = Column(String(8), nullable=False, default="WM")
    allow_manual_weight: bool = Column(Boolean, nullable=False, default=False)
    print_copies: int = Column(Integer, nullable=False, default=1)
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Company {self.name}>"


class Commodity(Base):
    __tablename__ = "commodities"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name_en: str = Column(String(64), nullable=False)
    name_sw: str = Column(String(64), nullable=False)
    deduction_kg: float = Column(Float, nullable=False, default=0.0)
    price_per_tonne: float = Column(Float, nullable=False, default=0.0)
    is_active: bool = Column(Boolean, nullable=False, default=True)
    sort_order: int = Column(Integer, nullable=False, default=0)
    created_at: datetime = Column(DateTime, server_default=func.now())

    tickets = relationship("WeighTicket", back_populates="commodity")

    def __repr__(self) -> str:
        return f"<Commodity {self.name_en}>"


class WeighTicket(Base):
    __tablename__ = "weigh_tickets"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    ticket_number: str = Column(String(32), unique=True, nullable=False)
    vehicle_plate: str = Column(String(32), nullable=False)
    driver_name: str = Column(String(128), nullable=False, default="")
    company_name: str = Column(String(128), nullable=False, default="")
    commodity_id: Optional[int] = Column(Integer, ForeignKey("commodities.id"), nullable=True)
    commodity_name: str = Column(String(64), nullable=False, default="")
    deduction_kg: float = Column(Float, nullable=False, default=0.0)
    commodity_rate_per_tonne: float = Column(Float, nullable=False, default=0.0)
    commodity_value: Optional[float] = Column(Float, nullable=True)
    oil_distance_km: float = Column(Float, nullable=False, default=0.0)
    oil_rate_per_km: float = Column(Float, nullable=False, default=0.0)
    oil_price: float = Column(Float, nullable=False, default=0.0)
    total_price: Optional[float] = Column(Float, nullable=True)
    tare_weight: float = Column(Float, nullable=True)
    gross_weight: Optional[float] = Column(Float, nullable=True)
    net_weight: Optional[float] = Column(Float, nullable=True)
    tare_datetime: Optional[datetime] = Column(DateTime, nullable=True)
    gross_datetime: Optional[datetime] = Column(DateTime, nullable=True)
    tare_source: str = Column(String(8), nullable=False, default="auto")
    gross_source: Optional[str] = Column(String(8), nullable=True)
    # Multi-axle / multi-deck support
    axle_count: int = Column(Integer, nullable=False, default=1)
    axle_weights_json: str = Column(Text, nullable=False, default="[]")  # JSON list of floats
    operator_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes: Optional[str] = Column(Text, nullable=True)
    status: str = Column(String(32), nullable=False, default="tare_captured")  # tare_captured|gross_captured|complete|void
    is_void: bool = Column(Boolean, nullable=False, default=False)
    voided_by: Optional[int] = Column(Integer, ForeignKey("users.id"), nullable=True)
    void_reason: Optional[str] = Column(Text, nullable=True)
    void_datetime: Optional[datetime] = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, server_default=func.now())

    operator = relationship("User", back_populates="tickets", foreign_keys=[operator_id])
    commodity = relationship("Commodity", back_populates="tickets")
    gate_events = relationship("GateEvent", back_populates="ticket")
    exceptions = relationship("TicketException", back_populates="ticket")

    def __repr__(self) -> str:
        return f"<WeighTicket {self.ticket_number}>"


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    username: str = Column(String(64), nullable=False)
    action: str = Column(String(64), nullable=False)
    entity: str = Column(String(64), nullable=False)
    entity_id: Optional[int] = Column(Integer, nullable=True)
    details: str = Column(Text, nullable=False, default="{}")
    timestamp: datetime = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="audit_logs")

    def details_dict(self) -> dict:
        try:
            return json.loads(self.details)
        except Exception:
            return {}

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by {self.username}>"


class VehicleProfile(Base):
    __tablename__ = "vehicle_profiles"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_plate: str = Column(String(32), unique=True, nullable=False)
    default_driver_name: str = Column(String(128), nullable=False, default="")
    default_company_name: str = Column(String(128), nullable=False, default="")
    last_commodity_name: str = Column(String(64), nullable=False, default="")
    last_seen_at: Optional[datetime] = Column(DateTime, nullable=True)
    last_ticket_id: Optional[int] = Column(Integer, ForeignKey("weigh_tickets.id"), nullable=True)
    created_at: datetime = Column(DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<VehicleProfile {self.vehicle_plate}>"


class GateEvent(Base):
    __tablename__ = "gate_events"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id: int = Column(Integer, ForeignKey("weigh_tickets.id"), nullable=False)
    event_type: str = Column(String(32), nullable=False)  # arrived|on_bridge|off_bridge|dispatch|returned
    event_note: Optional[str] = Column(Text, nullable=True)
    recorded_by: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    recorded_by_name: str = Column(String(64), nullable=False)
    created_at: datetime = Column(DateTime, server_default=func.now())

    ticket = relationship("WeighTicket", back_populates="gate_events")

    def __repr__(self) -> str:
        return f"<GateEvent {self.event_type} ticket={self.ticket_id}>"


class TicketException(Base):
    __tablename__ = "ticket_exceptions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Optional[int] = Column(Integer, ForeignKey("weigh_tickets.id"), nullable=True)
    vehicle_plate: Optional[str] = Column(String(32), nullable=True)
    reason_type: str = Column(String(32), nullable=False)  # manual_weight|unstable_scale|reweigh_request
    reason_detail: str = Column(Text, nullable=False, default="")
    recorded_by: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    recorded_by_name: str = Column(String(64), nullable=False)
    created_at: datetime = Column(DateTime, server_default=func.now())

    ticket = relationship("WeighTicket", back_populates="exceptions")

    def __repr__(self) -> str:
        return f"<TicketException {self.reason_type} ticket={self.ticket_id}>"
