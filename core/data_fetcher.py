# src/finops_framework/core/data_fetcher.py

import streamlit as st
import pandas as pd
from snowflake.snowpark import Session # Assuming Session is already established and passed in
from typing import Dict, Any, Tuple
from datetime import date, timedelta

# Import our centralized SQL queries
from finops_framework.core.query_store import SQL_QUERIES

# Define a custom exception for data fetching errors
class DataFetchError(Exception):
    """Custom exception for errors encountered during data fetching from Snowflake."""
    pass

class DataFetcher:
    """
    Manages Snowflake data fetching, query execution, and caching.
    Expects an already established Snowpark Session.
    """
    def __init__(self, session: Session):
        """
        Initializes the DataFetcher with an active Snowpark Session.
        Args:
            session (Session): An active Snowpark Session object.
        """
        if not isinstance(session, Session):
            raise TypeError("Session object must be an instance of snowflake.snowpark.Session")
        self._session = session

    @st.cache_data(ttl=3600) # Cache query results for 1 hour
    def execute_query(self, query_id: str, params: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Executes a named SQL query from the SQL_QUERIES store against Snowflake.

        Args:
            query_id (str): The unique ID of the query as defined in query_store.SQL_QUERIES.
            params (Dict[str, Any], optional): A dictionary of parameters to bind to the query.
                                                Defaults to None (no parameters).

        Returns:
            pd.DataFrame: A Pandas DataFrame containing the query results.

        Raises:
            DataFetchError: If the query_id is not found or if the Snowflake query fails.
        """
        if query_id not in SQL_QUERIES:
            raise DataFetchError(f"Query ID '{query_id}' not found in SQL_QUERIES store.")

        query_string = SQL_QUERIES[query_id]

        if params is None:
            params = {}

        try:
            # Use the passed-in Snowpark session to execute the query
            # _bind_parameters ensures secure and proper parameter handling
            result_df = self._session.sql(query_string).collect(_bind_parameters=params)
            return pd.DataFrame(result_df)
        except Exception as e:
            # Catch broad exceptions from Snowpark and re-raise as a custom DataFetchError
            raise DataFetchError(f"Snowflake query '{query_id}' failed: {e}") from e

    def calculate_prev_period_dates(self, start_date: date, end_date: date) -> Tuple[date, date]:
        """
        Calculates the start and end dates for the previous period of the same duration.

        Args:
            start_date (date): The start date of the current period.
            end_date (date): The end date of the current period.

        Returns:
            Tuple[date, date]: A tuple containing (previous_start_date, previous_end_date).
        """
        duration = end_date - start_date
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - duration
        return prev_start_date, prev_end_date