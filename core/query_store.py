# src/finops_framework/core/query_store.py

# This dictionary holds all SQL queries used throughout the FinOps dashboard.
# Queries are named descriptively for easy access and management.
# Parameters in queries should use the ':param_name' syntax for binding.

SQL_QUERIES = {
    # --- General/Overview Queries ---
    "TOTAL_COST_AND_CREDITS_OVERVIEW": """
        SELECT
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN CREDITS_USED ELSE 0 END) AS TOTAL_CREDITS,
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN CREDITS_USED * 2 ELSE 0 END) AS ESTIMATED_COST_USD,
            SUM(CASE WHEN START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN CREDITS_USED ELSE 0 END) AS PREV_TOTAL_CREDITS,
            SUM(CASE WHEN START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN CREDITS_USED * 2 ELSE 0 END) AS PREV_ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY;
    """,
    "DAILY_CREDIT_CONSUMPTION_TREND": """
        SELECT
            TO_DATE(START_TIME) AS USAGE_DAY,
            SUM(CREDITS_USED) AS DAILY_CREDITS_USED,
            SUM(CREDITS_USED * 2) AS DAILY_ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            1
        ORDER BY
            1;
    """,
    "COST_BY_SERVICE_TYPE": """
        SELECT
            SERVICE_TYPE,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY
        WHERE
            USAGE_DATE BETWEEN :start_date AND :end_date
        GROUP BY
            SERVICE_TYPE
        ORDER BY
            ESTIMATED_COST_USD DESC;
    """,
    "COST_BY_WAREHOUSE_TYPE": """
        SELECT
            WAREHOUSE_TYPE,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE
            START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            WAREHOUSE_TYPE
        ORDER BY
            ESTIMATED_COST_USD DESC;
    """,
    "TOP_10_WAREHOUSES_BY_COST": """
        SELECT
            WAREHOUSE_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            WAREHOUSE_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "TOP_10_USERS_BY_COST": """
        SELECT
            USER_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            USER_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,

    # --- User 360 View Queries ---
    "LIST_ACTIVE_USERS_BY_COST": """
        SELECT
            USER_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            START_TIME >= DATEADD(day, -90, CURRENT_DATE()) -- Active in last 90 days
        GROUP BY
            USER_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC;
    """,
    "USER_360_SUMMARY_METRICS": """
        SELECT
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN CREDITS_USED ELSE 0 END) AS TOTAL_CREDITS,
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN CREDITS_USED * 2 ELSE 0 END) AS ESTIMATED_COST_USD,
            SUM(CASE WHEN START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN CREDITS_USED ELSE 0 END) AS PREV_TOTAL_CREDITS,
            SUM(CASE WHEN START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN CREDITS_USED * 2 ELSE 0 END) AS PREV_ESTIMATED_COST_USD,
            AVG(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN TOTAL_ELAPSED_TIME ELSE NULL END) / 1000 AS AVG_QUERY_DURATION_SEC,
            AVG(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN CREDITS_USED ELSE NULL END) AS AVG_CREDITS_PER_QUERY,
            COUNT(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN QUERY_ID ELSE NULL END) AS TOTAL_QUERY_COUNT,
            COUNT(CASE WHEN START_TIME BETWEEN :start_date AND :end_date AND ERROR_MESSAGE IS NOT NULL THEN QUERY_ID ELSE NULL END) AS FAILED_QUERY_COUNT,
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN BYTES_SCANNED ELSE 0 END) AS TOTAL_BYTES_SCANNED,
            SUM(CASE WHEN START_TIME BETWEEN :start_date AND :end_date THEN COMPILATION_TIME ELSE 0 END) / 1000 AS TOTAL_COMPILATION_TIME_SEC
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name;
    """,
    "USER_DAILY_CREDIT_CONSUMPTION": """
        SELECT
            TO_DATE(START_TIME) AS USAGE_DAY,
            SUM(CREDITS_USED) AS DAILY_CREDITS_USED,
            SUM(CREDITS_USED * 2) AS DAILY_ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            1
        ORDER BY
            1;
    """,
    "USER_WAREHOUSE_COST_BREAKDOWN": """
        SELECT
            WAREHOUSE_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            WAREHOUSE_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "USER_ROLE_COST_BREAKDOWN": """
        SELECT
            ROLE_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            ROLE_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "USER_QUERY_TYPE_DISTRIBUTION": """
        SELECT
            QUERY_TYPE,
            COUNT(*) AS QUERY_COUNT,
            SUM(CREDITS_USED) AS TOTAL_CREDITS,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            QUERY_TYPE
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "USER_TOP_EXPENSIVE_QUERIES": """
        SELECT
            QUERY_ID,
            QUERY_TEXT,
            WAREHOUSE_NAME,
            ROLE_NAME,
            TOTAL_ELAPSED_TIME / 1000 AS TOTAL_ELAPSED_TIME_SEC,
            CREDITS_USED,
            CREDITS_USED * 2 AS ESTIMATED_COST_USD,
            BYTES_SCANNED / POW(1024,3) AS BYTES_SCANNED_GB,
            BYTES_SPILLED_TO_LOCAL_STORAGE / POW(1024,3) AS LOCAL_SPILL_GB,
            BYTES_SPILLED_TO_REMOTE_STORAGE / POW(1024,3) AS REMOTE_SPILL_GB,
            START_TIME
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
            AND CREDITS_USED IS NOT NULL
        ORDER BY
            CREDITS_USED DESC
        LIMIT 20;
    """,
    "USER_TOP_LONG_RUNNING_QUERIES": """
        SELECT
            QUERY_ID,
            QUERY_TEXT,
            WAREHOUSE_NAME,
            ROLE_NAME,
            TOTAL_ELAPSED_TIME / 1000 AS TOTAL_ELAPSED_TIME_SEC,
            EXECUTION_TIME / 1000 AS EXECUTION_TIME_SEC,
            QUEUED_OVERLOAD_TIME / 1000 AS QUEUED_OVERLOAD_TIME_SEC,
            COMPILATION_TIME / 1000 AS COMPILATION_TIME_SEC,
            CREDITS_USED,
            CREDITS_USED * 2 AS ESTIMATED_COST_USD,
            START_TIME
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date
            AND TOTAL_ELAPSED_TIME IS NOT NULL
        ORDER BY
            TOTAL_ELAPSED_TIME DESC
        LIMIT 20;
    """,
    "USER_WAREHOUSE_UTILIZATION_OVERVIEW": """
        SELECT
            WH.WAREHOUSE_NAME,
            WH.SIZE,
            WH.AUTO_SUSPEND,
            SUM(WMH.CREDITS_USED) AS TOTAL_CREDITS,
            (SUM(WMH.CREDITS_USED_COMPUTE_BLOB_STORAGE) / SUM(WMH.CREDITS_USED)) * 100 AS COMPUTE_CREDIT_RATIO,
            -- This is tricky for user-specific idle time. We'll simplify:
            -- Find warehouses this user used, then aggregate general idle time for those warehouses.
            -- A more precise 'user-incurred idle' requires complex session tracking.
            -- This query gives general idle time *for warehouses this user interacted with*.
            SUM(CASE WHEN WMH.CREDITS_USED = 0 THEN 1 ELSE 0 END) AS IDLE_MINUTES_ON_WH_USER_USED,
            COUNT(WMH.WAREHOUSE_ID) AS TOTAL_MINUTES_ON_WH_USER_USED,
            (IDLE_MINUTES_ON_WH_USER_USED * 100.0 / NULLIF(TOTAL_MINUTES_ON_WH_USER_USED, 0)) AS IDLE_PERCENTAGE_ON_WH_USER_USED
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES WH
        JOIN
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY WMH
            ON WH.WAREHOUSE_ID = WMH.WAREHOUSE_ID
        WHERE
            WMH.START_TIME BETWEEN :start_date AND :end_date
            AND WH.WAREHOUSE_ID IN (SELECT DISTINCT WAREHOUSE_ID FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY WHERE USER_NAME = :selected_user_name AND START_TIME BETWEEN :start_date AND :end_date) -- Filter to warehouses used by this user
        GROUP BY
            WH.WAREHOUSE_NAME, WH.SIZE, WH.AUTO_SUSPEND
        ORDER BY IDLE_PERCENTAGE_ON_WH_USER_USED DESC
        LIMIT 5;
    """,

    # --- Warehouse Insights Queries ---
    "WAREHOUSE_SUMMARY_METRICS": """
        SELECT
            WH.WAREHOUSE_NAME,
            WH.SIZE,
            WH.AUTO_SUSPEND,
            WH.AUTO_RESUME,
            SUM(WMH.CREDITS_USED) AS TOTAL_CREDITS_USED,
            SUM(WMH.CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CASE WHEN WMH.START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN WMH.CREDITS_USED ELSE 0 END) AS PREV_TOTAL_CREDITS_USED,
            SUM(CASE WHEN WMH.START_TIME BETWEEN :prev_start_date AND :prev_end_date THEN WMH.CREDITS_USED * 2 ELSE 0 END) AS PREV_ESTIMATED_COST_USD,
            SUM(CASE WHEN WMH.CREDITS_USED > 0 THEN 1 ELSE 0 END) AS ACTIVE_MINUTES,
            SUM(CASE WHEN WMH.CREDITS_USED = 0 THEN 1 ELSE 0 END) AS IDLE_MINUTES,
            COUNT(WMH.WAREHOUSE_ID) AS TOTAL_MINUTES_ON,
            (IDLE_MINUTES * 100.0 / NULLIF(TOTAL_MINUTES_ON, 0)) AS IDLE_PERCENTAGE
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSES WH
        JOIN
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY WMH
            ON WH.WAREHOUSE_ID = WMH.WAREHOUSE_ID
        WHERE
            WH.WAREHOUSE_NAME = :selected_warehouse_name AND WMH.START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            WH.WAREHOUSE_NAME, WH.SIZE, WH.AUTO_SUSPEND, WH.AUTO_RESUME;
    """,
    "WAREHOUSE_DAILY_CREDIT_CONSUMPTION": """
        SELECT
            TO_DATE(START_TIME) AS USAGE_DAY,
            SUM(CREDITS_USED) AS DAILY_CREDITS_USED,
            SUM(CREDITS_USED * 2) AS DAILY_ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE
            WAREHOUSE_NAME = :selected_warehouse_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            1
        ORDER BY
            1;
    """,
    "WAREHOUSE_QUERY_COMPLETION_STATUS": """
        SELECT
            CASE
                WHEN ERROR_MESSAGE IS NOT NULL THEN 'Failed'
                ELSE 'Succeeded'
            END AS STATUS,
            COUNT(QUERY_ID) AS QUERY_COUNT,
            SUM(TOTAL_ELAPSED_TIME) / 1000 AS TOTAL_ELAPSED_TIME_SEC,
            SUM(CREDITS_USED) AS TOTAL_CREDITS_USED,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            WAREHOUSE_NAME = :selected_warehouse_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            STATUS;
    """,
    "WAREHOUSE_TOP_USERS_BY_COST": """
        SELECT
            USER_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            WAREHOUSE_NAME = :selected_warehouse_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            USER_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "WAREHOUSE_TOP_ROLES_BY_COST": """
        SELECT
            ROLE_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD,
            SUM(CREDITS_USED) AS TOTAL_CREDITS
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            WAREHOUSE_NAME = :selected_warehouse_name AND START_TIME BETWEEN :start_date AND :end_date
        GROUP BY
            ROLE_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC
        LIMIT 10;
    """,
    "WAREHOUSE_QUEUED_OVERLOAD_TIME_TREND": """
        SELECT
            TO_DATE(START_TIME) AS USAGE_DAY,
            SUM(QUEUED_OVERLOAD_TIME) / 1000 AS TOTAL_QUEUED_OVERLOAD_TIME_SEC,
            AVG(QUEUED_OVERLOAD_TIME) / 1000 AS AVG_QUEUED_OVERLOAD_TIME_SEC_PER_QUERY
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
        WHERE
            WAREHOUSE_NAME = :selected_warehouse_name AND START_TIME BETWEEN :start_date AND :end_date
            AND QUEUED_OVERLOAD_TIME > 0
        GROUP BY
            1
        ORDER BY
            1;
    """,
    "LIST_ACTIVE_WAREHOUSES_BY_COST": """
        SELECT
            WAREHOUSE_NAME,
            SUM(CREDITS_USED * 2) AS ESTIMATED_COST_USD
        FROM
            SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
        WHERE
            START_TIME >= DATEADD(day, -90, CURRENT_DATE()) -- Warehouses active in last 90 days
        GROUP BY
            WAREHOUSE_NAME
        ORDER BY
            ESTIMATED_COST_USD DESC;
    """
}