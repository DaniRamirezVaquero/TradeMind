from datetime import date
import random
from typing import Optional, Union

from .models import DeviceInfo

from .utils import parse_date



def predict_price(
    brand: str,
    model: str,
    storage: str,
    has_5g: bool,
    release_date: Union[str, date],
    grade: str = 'C',
    sale_date: Union[str, date] = date.today()
) -> float:
    """Predicts the selling price of a device based on its characteristics."""
    
    print(f"Predicting price for {brand} {model} ({storage}, 5G: {has_5g}, grade: {grade})") 
    
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

def recommend_device(budget: float, brand_preference: str, min_storage: int, grade_preference: str) -> DeviceInfo:
    """Recommends a device based on budget, brand preference, and other criteria."""
    # TODO: Replace with actual recommendation logic
    # For now, we'll just return a random device
    brands = ["Apple", "Samsung", "Google", "OnePlus"]
    models = ["iPhone 13", "Galaxy S21", "Pixel 6", "OnePlus 9"]
    storages = ["64GB", "128GB", "256GB"]
    has_5g = random.choice([True, False])
    release_date = date.today()
    
    print(f"Recommending device within ${budget} with {min_storage}GB storage, brand: {brand_preference}, grade: {grade_preference}")
    
    return DeviceInfo(
        brand=random.choice(brands),
        model=random.choice(models),
        storage=random.choice(storages),
        has_5g=has_5g,
        release_date=release_date
    )

def get_release_date(brand: str, model: str) -> Optional[date]:
    """Gets the release date for a device model."""
    # TODO: Replace with actual database lookup
    sample_dates = {
        ("Apple", "iPhone 13"): date(2021, 9, 24),
        ("Samsung", "Galaxy S21"): date(2021, 1, 29),
    }
    return sample_dates.get((brand, model))
