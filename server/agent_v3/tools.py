from datetime import date, datetime
import random
from typing import Optional, Union

def parse_date(date_str: Union[str, date]) -> date:
    """Convierte una string de fecha en objeto date."""
    if isinstance(date_str, date):
        return date_str
    try:
        # Intenta parsear primero como MM/YYYY
        if '/' in date_str and len(date_str.split('/')) == 2:
            month, year = date_str.split('/')
            return date(int(year), int(month), 1)
        # Intenta diferentes formatos comunes
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"No se pudo convertir '{date_str}' a fecha")
    except ValueError as e:
        raise ValueError(f"Error al procesar la fecha: {e}")

def predict_price(
    brand: str,
    model: str,
    storage: str,
    has_5g: bool,
    release_date: Union[str, date],
    grade: str,
    sale_date: Union[str, date] = date.today()
) -> float:
    """Predicts the selling price of a device based on its characteristics."""
    # Convertir fechas
    release_date = parse_date(release_date)
    sale_date = parse_date(sale_date)
    
    # Calcular días entre fechas
    days_since_release = (sale_date - release_date).days
    
    # TODO: Replace with actual model prediction
    # Por ahora, simulamos que el precio disminuye con el tiempo
    base_price = random.uniform(800, 1200)
    age_factor = max(0.4, 1 - (days_since_release / 365 * 0.2))  # Depreciation del 20% por año, mínimo 40% del valor
    grade_factors = {'B': 0.8, 'C': 0.6, 'D': 0.4, 'E': 0.2}
    grade_factor = grade_factors.get(grade, 0.5)
    
    final_price = base_price * age_factor * grade_factor
    
    return round(final_price, 2)

def recommend_device(budget: float) -> dict:
    """Recommends a device based on budget."""
    # TODO: Replace with actual recommendation logic
    sample_devices = [
        {"brand": "Samsung", "model": "Galaxy S21", "price": 699.99},
        {"brand": "Apple", "model": "iPhone 13", "price": 799.99},
        {"brand": "Google", "model": "Pixel 6", "price": 599.99}
    ]
    return random.choice([d for d in sample_devices if d["price"] <= budget])

def get_release_date(brand: str, model: str) -> Optional[date]:
    """Gets the release date for a device model."""
    # TODO: Replace with actual database lookup
    sample_dates = {
        ("Apple", "iPhone 13"): date(2021, 9, 24),
        ("Samsung", "Galaxy S21"): date(2021, 1, 29),
    }
    return sample_dates.get((brand, model))
