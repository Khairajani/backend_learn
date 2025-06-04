{{ config(
    materialized='table',
    alias='sample_table_upper'
) }}

select *,
       upper(NAME) as NAME_UPPER_DBT
from {{ ref('sample_table') }}