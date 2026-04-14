import logging
from typing import List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

import schemas

logger = logging.getLogger(__name__)

class SQLIntegrationService:
    def __init__(self, config: schemas.SQLConnectionConfig):
        self.config = config
        self.connection_string = self._build_connection_string()

    def _build_connection_string(self) -> str:
        """Constructs the SQLAlchemy connection string."""
        # Note: In a real production app, we would handle driver-specific formatting better
        return f"{self.config.driver}://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

    def test_connection(self) -> schemas.SQLConnectionTestResponse:
        """Tests the connection and returns a sample of process numbers."""
        engine: Optional[Engine] = None
        try:
            engine = create_engine(self.connection_string, connect_args={"connect_timeout": 10})
            with engine.connect() as connection:
                # Test query execution
                result = connection.execute(text(self.config.query))
                rows = result.fetchall()
                
                # Extract numbers (assuming first column if not named 'number')
                sample_data = []
                for row in rows[:5]:
                    # Try to find a column that looks like a process number
                    val = str(row[0]).strip()
                    sample_data.append(val)
                
                return schemas.SQLConnectionTestResponse(
                    success=True,
                    message=f"Conexão bem-sucedida! Encontrados {len(rows)} registros.",
                    sample_data=sample_data
                )
        except Exception as e:
            logger.error(f"SQL Connection test failed: {str(e)}")
            return schemas.SQLConnectionTestResponse(
                success=False,
                message=f"Erro de conexão: {str(e)}"
            )
        finally:
            if engine:
                engine.dispose()

    def get_process_numbers(self) -> List[str]:
        """Executes the query and returns all extracted process numbers."""
        engine = create_engine(self.connection_string)
        try:
            with engine.connect() as connection:
                result = connection.execute(text(self.config.query))
                rows = result.fetchall()
                return [str(row[0]).strip() for row in rows]
        except Exception as e:
            logger.error(f"Failed to fetch process numbers from SQL: {str(e)}")
            raise
        finally:
            engine.dispose()
