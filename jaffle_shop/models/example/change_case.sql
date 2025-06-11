{{ config(
    materialized='table',
    alias='dbt_output_upper'
) }}

select *,
       upper(NAME) as NAME_UPPER_DBT
from {{ ref('dbt_input') }}