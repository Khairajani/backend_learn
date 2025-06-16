{{ config(
    materialized='table',
    alias='dbt_output_upper_16_june'
) }}

select *,
       upper(NAME) as NAME_UPPER_DBT
from {{ ref('dbt_input') }}