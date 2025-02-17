# TradeMind 📈🤖

## Estado del Proyecto 🚧
Este proyecto está actualmente en desarrollo.

## Descripción del Proyecto 📚
TradeMind es una red multiagente especializada en la predicción y estudio de precios de trade-in de smartphones. Utilizando técnicas avanzadas de inteligencia artificial y análisis de datos, nuestro objetivo es proporcionar estimaciones precisas y útiles para los usuarios interesados en el mercado de trade-in de dispositivos móviles.

## Backend 🖥️
El backend de TradeMind está construido utilizando FastAPI. Proporciona un endpoint para interactuar con el agente de predicción.

### Instrucciones para ejecutar el backend 🚀

1. Clona el repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd TradeMind/server
    ```

2. Crea un entorno virtual y actívalo:
    ```bash
    python -m venv env
    source env/bin/activate  # En Windows usa `env\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Ejecuta el servidor:
    ```bash
    uvicorn main:app --reload
    ```

5. Accede a la documentación interactiva de la API:
    Abre tu navegador y ve a `http://127.0.0.1:8000/docs` para ver la documentación generada automáticamente por FastAPI.

¡Mantente atento para más actualizaciones! 🚀