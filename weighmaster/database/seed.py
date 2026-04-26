"""Seed default data into the database."""
from weighmaster.database.models import Commodity


_DEFAULT_COMMODITIES = [
    ("Cement", "Saruji", 0.0, 0.0, 1),
    ("Maize", "Mahindi", 0.0, 0.0, 2),
    ("Sand", "Mchanga", 0.0, 0.0, 3),
    ("Gravel", "Changarawe", 0.0, 0.0, 4),
    ("Cotton", "Pamba", 25.0, 0.0, 5),
    ("Rice", "Mchele", 0.0, 0.0, 6),
    ("Sugar", "Sukari", 0.0, 0.0, 7),
    ("Wheat", "Ngano", 0.0, 0.0, 8),
    ("Sisal", "Katani", 0.0, 0.0, 9),
    ("Other", "Nyingine", 0.0, 0.0, 10),
]


def seed_commodities(session) -> None:
    for name_en, name_sw, deduction, price_per_tonne, sort_order in _DEFAULT_COMMODITIES:
        commodity = Commodity(
            name_en=name_en,
            name_sw=name_sw,
            deduction_kg=deduction,
            price_per_tonne=price_per_tonne,
            sort_order=sort_order,
        )
        session.add(commodity)
    session.flush()
