{{ config(
    materialized='table',
    alias='dbt_output'
) }}

select *,
       upper(NAME) as NAME_UPPER_DBT
from {{ ref('dbt_input') }}