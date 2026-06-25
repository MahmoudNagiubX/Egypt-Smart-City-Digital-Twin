from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Egypt Smart City Digital Twin"
    app_env: str = "development"
    app_debug: bool = True

    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "smart_city"
    database_user: str = "smartcity"
    database_password: str = "smartcity123"
    postgres_url: str = "postgresql://smartcity:smartcity123@localhost:5432/smart_city"

    nasr_city_center_lat: float = 30.0561
    nasr_city_center_lon: float = 31.3300

    default_weather_start_date: str = "2024-01-01"
    default_weather_end_date: str = "2024-12-31"

    use_postgis: bool = False
    demo_mode: bool = True

    class Config:
        env_file = "backend/.env"
        env_file_encoding = "utf-8"

settings = Settings()
